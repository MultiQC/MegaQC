# -*- coding: utf-8 -*-

from __future__ import division

import copy
import json
import os
import random
import string
import sys
from builtins import map, range, str
from collections import OrderedDict, defaultdict
from datetime import datetime, timedelta
from hashlib import md5

import plotly.figure_factory as ff
import plotly.graph_objs as go
import plotly.offline as py
from flask import current_app
from megaqc.api.constants import (
    comparators,
    type_to_tables_fields,
    valid_join_conditions,
)
from megaqc.extensions import db
from megaqc.model.models import *
from megaqc.user.models import User
from megaqc.utils import settings
from past.utils import old_div
from sqlalchemy import Numeric, cast, distinct, func, or_
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import aliased
from sqlalchemy.sql import and_, not_, or_

if sys.version_info.major == 2:
    lc_string = string.lowercase
elif sys.version_info.major == 3:
    lc_string = string.ascii_lowercase
else:
    raise (Exception("Unsupported python version"))


def generate_hash(d):
    data = copy.deepcopy(d)
    data.pop("config_creation_date")
    data_string = json.dumps(data).encode("utf-8")
    md5er = md5()
    md5er.update(data_string)
    ret = md5er.hexdigest()
    return ret


def store_report_data(user, report_data, uploaded_file):
    file_name = "".join([random.choice(lc_string) for i in range(10)])

    if not os.path.isdir(current_app.config["UPLOAD_FOLDER"]):
        os.mkdir(current_app.config["UPLOAD_FOLDER"])

    if report_data:
        with open(
            os.path.join(current_app.config["UPLOAD_FOLDER"], file_name), "wb"
        ) as fh:
            fh.write(report_data)
    else:
        uploaded_file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], file_name))

    upload_row = Upload(
        status="NOT TREATED",
        path=os.path.join(current_app.config["UPLOAD_FOLDER"], file_name),
        message="File has been created, loading in MegaQC is queued.",
        user_id=user.user_id,
    )
    upload_row.save()
    return (True, "Data upload queued successfully")


def handle_report_data(user, report_data):
    if "data" in report_data:
        report_data = report_data["data"]
    report_hash = generate_hash(report_data)

    # Check that we don't already have a data file with this md5hash
    if db.session.query(Report).filter(Report.report_hash == report_hash).first():
        return (False, "Report already uploaded")

    # Pull the creation date if we can
    try:
        report_created_at = datetime.strptime(
            report_data["config_creation_date"], "%Y-%m-%d, %H:%M"
        )
    except:
        report_created_at = datetime.now()

    # Add to the main report table
    new_report = Report(
        report_hash=report_hash, user_id=user.user_id, created_at=report_created_at
    )
    try:
        new_report.save()
    except InvalidRequestError as e:
        if "UNIQUE constraint failed" in str(e):
            return (False, "Report already processed")
        else:
            raise e
    current_app.logger.info(
        "Created new report {} from {}".format(new_report.report_id, user.email)
    )
    report_id = new_report.report_id

    # Save the user as a report meta value
    # TODO: Replace this with special cases in get_report_metadata_fields()
    user_report_meta = ReportMeta(
        report_meta_key="username", report_meta_value=user.username, report_id=report_id
    )
    user_report_meta.save()

    # Get top-level `config_` JSON keys (strings only).
    # eg. config_title / config_short_version / config_creation_date etc
    new_meta_cnt = 0
    for key in report_data:
        if (
            key.startswith("config")
            and not isinstance(report_data[key], list)
            and not isinstance(report_data[key], dict)
            and report_data[key]
        ):
            new_meta_cnt += 1
            new_meta = ReportMeta(
                report_meta_key=key,
                report_meta_value=report_data[key],
                report_id=report_id,
            )
            new_meta.save()
    current_app.logger.info(
        "Finished writing {} metadata fields for report {}".format(
            new_meta_cnt, new_report.report_id
        )
    )

    # Save the raw parsed data (stuff that ends up in the multiqc_data directory)
    new_samp_cnt = 0
    for s_key in report_data.get("report_saved_raw_data", {}):
        section = s_key.replace("multiqc_", "")
        # Go through each sample
        for s_name in report_data["report_saved_raw_data"][s_key]:
            new_samp_cnt += 1
            report_sample = (
                db.session.query(Sample).filter(Sample.sample_name == s_name).first()
            )
            if not report_sample:
                report_sample = Sample(sample_name=s_name, report_id=report_id)
                report_sample.save()
            sample_id = report_sample.sample_id

            # Go through each data key
            for d_key in report_data["report_saved_raw_data"][s_key][s_name]:
                # Save / load the data type
                key_type = (
                    db.session.query(SampleDataType)
                    .filter(SampleDataType.data_id == d_key)
                    .first()
                )
                if not key_type:
                    key_type = SampleDataType(
                        data_key="{}__{}".format(section, d_key),
                        data_section=section,
                        data_id=d_key,
                    )
                    key_type.save()
                type_id = key_type.sample_data_type_id

                # Save the data value
                value = report_data["report_saved_raw_data"][s_key][s_name][d_key]
                new_data = SampleData(
                    report_id=report_id,
                    sample_data_type_id=type_id,
                    sample_id=sample_id,
                    value=str(value),
                )
                new_data.save()
    current_app.logger.info(
        "Finished writing {} samples for report {}".format(
            new_samp_cnt, new_report.report_id
        )
    )

    # Save report plot data and configs
    new_plotcfg_cnt = 0
    new_plotdata_cnt = 0
    for plot in report_data.get("report_plot_data"):
        #  skip custom plots
        if "mqc_hcplot_" in plot:
            continue
        # TODO: Add support for scatter / beeswarm / heatmap
        if report_data["report_plot_data"][plot]["plot_type"] not in [
            "bar_graph",
            "xy_line",
        ]:
            continue
        # Save the plot config as a JSON string
        config = json.dumps(report_data["report_plot_data"][plot]["config"])
        for dst_idx, dataset in enumerate(
            report_data["report_plot_data"][plot]["datasets"]
        ):
            try:
                if isinstance(
                    report_data["report_plot_data"][plot]["config"]["data_labels"][
                        dst_idx
                    ],
                    dict,
                ):
                    dataset_name = report_data["report_plot_data"][plot]["config"][
                        "data_labels"
                    ][dst_idx]["ylab"]
                else:
                    dataset_name = report_data["report_plot_data"][plot]["config"][
                        "data_labels"
                    ][dst_idx]
            except KeyError:
                try:
                    dataset_name = report_data["report_plot_data"][plot]["config"][
                        "ylab"
                    ]
                except KeyError:
                    dataset_name = report_data["report_plot_data"][plot]["config"][
                        "title"
                    ]

            plot_config = (
                db.session.query(PlotConfig)
                .filter(
                    PlotConfig.config_type
                    == report_data["report_plot_data"][plot]["plot_type"],
                    PlotConfig.config_name == plot,
                    PlotConfig.config_dataset == dataset_name,
                )
                .first()
            )
            if not plot_config:
                plot_config = PlotConfig(
                    config_type=report_data["report_plot_data"][plot]["plot_type"],
                    config_name=plot,
                    config_dataset=dataset_name,
                    data=config,
                )
                plot_config.save()
                new_plotcfg_cnt += 1
            config_id = plot_config.config_id

            # Save bar graph data
            if report_data["report_plot_data"][plot]["plot_type"] == "bar_graph":

                for sub_dict in dataset:
                    data_key = str(sub_dict["name"])
                    existing_category = (
                        db.session.query(PlotCategory)
                        .filter(PlotCategory.category_name == data_key)
                        .first()
                    )
                    data = json.dumps(
                        {x: y for x, y in list(sub_dict.items()) if x != "data"}
                    )
                    if not existing_category:
                        existing_category = PlotCategory(
                            report_id=report_id,
                            config_id=config_id,
                            category_name=data_key,
                            data=data,
                        )
                        existing_category.save()
                    else:
                        existing_category.data = data
                        existing_category.save()
                        category_id = existing_category.plot_category_id
                    for sa_idx, actual_data in enumerate(sub_dict["data"]):
                        existing_sample = (
                            db.session.query(Sample)
                            .filter(
                                Sample.sample_name
                                == report_data["report_plot_data"][plot]["samples"][
                                    dst_idx
                                ][sa_idx]
                            )
                            .first()
                        )
                        if existing_sample:
                            sample_id = existing_sample.sample_id
                        else:
                            new_sample = Sample(
                                sample_name=sub_dict["name"], report_id=report_id
                            )
                            new_sample.save()
                            sample_id = new_sample.sample_id
                        new_dataset_row = PlotData(
                            report_id=report_id,
                            config_id=config_id,
                            sample_id=sample_id,
                            plot_category_id=existing_category.plot_category_id,
                            data=json.dumps(actual_data),
                        )
                        new_dataset_row.save()
                        new_plotdata_cnt += 1

            # Save line plot data
            elif report_data["report_plot_data"][plot]["plot_type"] == "xy_line":
                for sub_dict in dataset:
                    try:
                        data_key = report_data["report_plot_data"][plot]["config"][
                            "data_labels"
                        ][dst_idx]["ylab"]
                    except (KeyError, TypeError):
                        try:
                            data_key = report_data["report_plot_data"][plot]["config"][
                                "ylab"
                            ]
                        except KeyError:
                            data_key = report_data["report_plot_data"][plot]["config"][
                                "title"
                            ]

                    existing_category = (
                        db.session.query(PlotCategory)
                        .filter(PlotCategory.category_name == data_key)
                        .first()
                    )
                    data = json.dumps(
                        {x: y for x, y in list(sub_dict.items()) if x != "data"}
                    )
                    if not existing_category:
                        existing_category = PlotCategory(
                            report_id=report_id,
                            config_id=config_id,
                            category_name=data_key,
                            data=data,
                        )
                        existing_category.save()
                    else:
                        existing_category.data = data
                        existing_category.save()
                    category_id = existing_category.plot_category_id

                    for sa_idx, actual_data in enumerate(sub_dict["data"]):
                        sample = (
                            db.session.query(Sample)
                            .filter(Sample.sample_name == sub_dict["name"])
                            .first()
                        )
                        if not sample:
                            sample = Sample(
                                sample_name=sub_dict["name"], report_id=report_id
                            )
                            sample.save()
                        sample_id = sample.sample_id

                        new_dataset_row = PlotData(
                            report_id=report_id,
                            config_id=config_id,
                            sample_id=sample_id,
                            plot_category_id=category_id,
                            data=json.dumps(sub_dict["data"]),
                        )
                    new_dataset_row.save()
                    new_plotdata_cnt += 1
    current_app.logger.info(
        "Finished writing plot data ({} cfg, {} data points) for report {}".format(
            new_plotcfg_cnt, new_plotdata_cnt, new_report.report_id
        )
    )

    # We made it this far - everything must have worked!
    return (True, "Data upload successful")


def generate_report_plot(plot_type, sample_names):
    # The common part of the query
    query = (
        db.session.query(PlotConfig, PlotData, PlotCategory, Sample)
        .join(PlotData, PlotData.config_id == PlotConfig.config_id)
        .join(PlotCategory)
        .join(Sample)
        .filter(Sample.sample_name.in_(sample_names))
    )

    if " -- " in plot_type:
        # Plot type also contains data_key : True for most xy_lines
        plot_type = plot_type.split(" -- ")
        rows = query.filter(
            PlotConfig.config_name == plot_type[0],
            PlotConfig.config_dataset == plot_type[1],
        ).all()
    else:
        rows = query.filter(PlotConfig.config_name == plot_type).all()

    if len(rows) == 0:
        return '<div class="alert alert-danger">No samples found</div>'

    if rows[0][0].config_type == "bar_graph":
        # not using sets to keep the order
        samples = []
        series = []
        colors = []
        total_per_sample = defaultdict(lambda: 0)
        plot_data = defaultdict(lambda: defaultdict(lambda: 0))
        plot_data_perc = defaultdict(lambda: defaultdict(lambda: 0))
        # get the latest config
        config = json.loads(rows[-1][0].data)
        for row in rows:
            if row[3].sample_name not in samples:
                samples.append(row[3].sample_name)
            if row[2].category_name not in series:
                series.append(row[2].category_name)
                cat_config = json.loads(row[2].data)
                if "color" in cat_config:
                    colors.append(cat_config["color"])
            plot_data[row[2].category_name][row[3].sample_name] = float(row[1].data)
            # count total per sample for percentages
            total_per_sample[row[3].sample_name] = total_per_sample[
                row[3].sample_name
            ] + float(row[1].data)
        for key in plot_data:
            for sample in plot_data[key]:
                plot_data_perc[key][sample] = (
                    100 * plot_data[key][sample] / total_per_sample[sample]
                )

        # Build the plot bars
        plots = []
        if not colors:
            colors = settings.default_plot_colors

        # Make the plot bars for the main count datasets
        for idx, d in enumerate(series):
            my_trace = go.Bar(
                y=samples,
                x=[plot_data[d][x] for x in samples],
                name=d,
                text=row[3].sample_name,
                orientation="h",
                visible=config.get("cpswitch_c_active", True),
                marker=dict(
                    color=colors[idx % len(colors)],
                    line=dict(color=colors[idx % len(colors)], width=3),
                ),
                hoverinfo="text+x",
            )
            plots.append(my_trace)

        # Make the plot traces for the bar graph percentages
        for idx, d in enumerate(series):
            my_trace = go.Bar(
                y=samples,
                x=[plot_data_perc[d][x] for x in samples],
                name=d,
                text=row[3].sample_name,
                orientation="h",
                visible=not config.get("cpswitch_c_active", True),
                marker=dict(
                    color=colors[idx % len(colors)],
                    line=dict(color=colors[idx % len(colors)], width=3),
                ),
                hoverinfo="text+x",
            )
            plots.append(my_trace)

        updated_layout = config_translate(
            "bar_graph",
            config,
            len(series),
            go.Layout(
                barmode="stack",
                hovermode="closest",
                height=500,
                margin=dict(t=80, b=80, l=100, r=40),
            ),
        )
        fig = go.Figure(data=plots, layout=updated_layout)
        plot_div = py.plot(
            fig,
            output_type="div",
            show_link=False,
            config=dict(
                modeBarButtonsToRemove=[
                    "sendDataToCloud",
                    "resetScale2d",
                    "hoverClosestCartesian",
                    "hoverCompareCartesian",
                    "toggleSpikelines",
                ],
                displaylogo=False,
            ),
        )
        return plot_div

    elif rows[0][0].config_type == "xy_line":
        plots = []
        config = json.loads(rows[-1][0].data)  # grab latest config
        for idx, row in enumerate(rows):
            xs = []
            ys = []
            data = json.loads(row[1].data)
            config = json.loads(row[0].data)
            if "categories" in config:
                for d_idx, d in enumerate(data):
                    xs.append(" " + str(config["categories"][d_idx]))
                    ys.append(d)

            else:
                for d in data:
                    xs.append(d[0])
                    ys.append(d[1])
            line_color = settings.default_plot_colors[
                idx % len(settings.default_plot_colors)
            ]
            plots.append(
                go.Scatter(
                    y=ys,
                    x=xs,
                    name=row[3].sample_name,
                    text=row[3].sample_name,
                    mode="lines",
                    marker=dict(color=line_color, line=dict(color=line_color, width=1)),
                    hoverinfo="text",
                )
            )
        updated_layout = config_translate(
            "xy_line",
            config,
            len(rows),
            go.Layout(
                xaxis={"type": "category"},
                showlegend=False,
                hovermode="closest",
                height=500,
                margin=dict(t=80, b=80, l=80, r=40),
            ),
        )
        fig = go.Figure(data=plots, layout=updated_layout)
        plot_div = py.plot(
            fig,
            output_type="div",
            show_link=False,
            config=dict(
                modeBarButtonsToRemove=[
                    "sendDataToCloud",
                    "resetScale2d",
                    "hoverClosestCartesian",
                    "hoverCompareCartesian",
                    "toggleSpikelines",
                ],
                displaylogo=False,
            ),
        )
        return plot_div


def config_translate(plot_type, config, series_nb, plotly_layout=go.Layout()):
    plotly_layout.title = config.get("title")
    xaxis = {}
    xaxis["title"] = config.get("xlab")
    yaxis = {}
    yaxis["title"] = config.get("ylab")
    if "ymin" in config and "ymax" in config:
        my_range = [float(config["ymin"]), float(config["ymax"])]
        if "logswitch_active" in config:
            my_range = list(map(math.log, my_range))
    # TODO : Figure out how yfloor and yceiling should be handled
    if plot_type == "bar_graph":
        # For stacked bar graphs, axes are reversed in Plotly
        plotly_layout.yaxis = xaxis
        plotly_layout.xaxis = yaxis

        updatemenus = list(
            [
                dict(
                    buttons=list(
                        [
                            dict(
                                args=[
                                    {
                                        "visible": [
                                            i < series_nb for i in range(series_nb * 2)
                                        ]
                                    }
                                ],
                                label="Count",
                                method="restyle",
                            ),
                            dict(
                                args=[
                                    {
                                        "visible": [
                                            i >= series_nb for i in range(series_nb * 2)
                                        ]
                                    }
                                ],
                                label="Percentage",
                                method="restyle",
                            ),
                        ]
                    ),
                    direction="left",
                    active=0 if config.get("cpswitch_c_active", True) else 1,
                    showactive=True,
                    type="buttons",
                    x=-0.1,
                    xanchor="left",
                    y=1.15,
                    yanchor="top",
                ),
            ]
        )
        plotly_layout["updatemenus"] = updatemenus
    elif plot_type == "xy_line":
        plotly_layout.yaxis = yaxis
        plotly_layout.xaxis = xaxis

        if "xPlotBands" in config:
            # Treat them as shapes
            shapes = []
            for band in config["xPlotBands"]:
                shape = {
                    "type": "rect",
                    "yref": "paper",
                    "x0": band["from"],
                    "y0": 0,
                    "x1": band["to"],
                    "y1": 1,
                    "line": {"color": band["color"], "width": 1,},
                    "fillcolor": band["color"],
                    "opacity": 0.5,
                }
                shapes.append(shape)
            plotly_layout.shapes = shapes

        if "yPlotBands" in config:
            # Treat them as shapes
            shapes = []
            for band in config["yPlotBands"]:
                shape = {
                    "type": "rect",
                    "xref": "paper",
                    "x0": 0,
                    "y0": band["from"],
                    "x1": 1,
                    "y1": band["to"],
                    "line": {"color": band["color"], "width": 1,},
                    "fillcolor": band["color"],
                    "opacity": 0.5,
                }
                shapes.append(shape)
            plotly_layout.shapes = shapes

    return plotly_layout


def get_samples(filters=None, count=False, ids=False):
    if not filters:
        filters = []
    if count:
        sample_query = db.session.query(func.count(distinct(Sample.sample_name)))
        sample_query = build_filter(sample_query, filters, Sample)
        return sample_query.one()[0]
    elif ids:
        sample_query = db.session.query(distinct(Sample.sample_id))
        sample_query = build_filter(sample_query, filters, Sample)
        samples = [x[0] for x in sample_query.all()]
        return samples
    else:
        sample_query = db.session.query(distinct(Sample.sample_name))
        sample_query = build_filter(sample_query, filters, Sample)
        samples = [x[0] for x in sample_query.all()]
        return samples


def get_report_metadata_fields(filters=None):
    if not filters:
        filters = []
    report_metadata_query = db.session.query(distinct(ReportMeta.report_meta_key)).join(
        Report
    )
    report_metadata_query = build_filter(report_metadata_query, filters, Report)
    return [row[0] for row in report_metadata_query.all()]


def get_sample_metadata_fields(filters=None):
    if not filters:
        filters = []
    sample_metadata_query = db.session.query(
        distinct(SampleDataType.data_key),
        SampleDataType.data_section,
        SampleDataType.sample_data_type_id,
    ).join(SampleData)
    sample_metadata_query = build_filter(sample_metadata_query, filters, SampleData)
    sample_fields = []
    for row in sample_metadata_query.all():
        if settings.sample_metadata_fields.get(row[0], {}).get("hidden", False):
            continue
        # Generate a default nice name (can be overwritten by config below)
        nicename = row[0][len(row[1]) :] if row[0].startswith(row[1]) else row[0]
        nice_section = row[1].title() if row[1].islower() else row[1]
        nicename = "{0}: {1}".format(
            nice_section.replace("_", " "), nicename.replace("_", " ")
        )
        sample_fields.append(
            {
                "key": row[0],
                "section": row[1],
                "type_id": row[2],
                "nicename": settings.report_metadata_fields.get(row[0], {}).get(
                    "nicename", nicename
                ),
                "priority": settings.report_metadata_fields.get(row[0], {}).get(
                    "priority", 1
                ),
            }
        )

    # Sort alphabetically, then by section and then overwrite with priority if given
    sample_fields.sort(key=lambda x: x["nicename"].lower())
    sample_fields.sort(key=lambda x: x["section"])
    sample_fields.sort(key=lambda x: x["priority"], reverse=True)
    return sample_fields


def get_plot_types(user, filters=None):
    plot_types = []
    if not filters:
        filters = []
    pt_query = (
        db.session.query(
            distinct(PlotConfig.config_name),
            PlotConfig.config_dataset,
            PlotConfig.data,
            PlotConfig.config_type,
        )
        .join(PlotCategory)
        .join(PlotData)
    )
    pt_query = build_filter(pt_query, filters, PlotData)
    fav_plot_types = [
        (x.config_name, x.config_dataset) for x in user.favourite_plotconfigs
    ]
    for row in pt_query.all():
        if row[3] == "xy_line":
            plot_type_obj = {
                "name": "{} -- {}".format(row[0], row[1]),
                "nicename": json.loads(row[2]).get("title", row[0].replace("_", " ")),
                "plot_id": row[0],
                "plot_ds_name": row[1],
                "type": "linegraph",
                "favourite": (row[0], row[1]) in fav_plot_types,
            }
        elif row[3] == "bar_graph":
            plot_type_obj = {
                "name": "{} -- {}".format(row[0], row[1]),
                "nicename": "{0} ({1})".format(
                    json.loads(row[2]).get("title", row[0].replace("_", " ")), row[1]
                ),
                "type": "bargraph",
                "favourite": (row[0], row[1]) in fav_plot_types,
            }

        plot_types.append(plot_type_obj)

    plot_types = sorted(plot_types, key=lambda k: k["name"])
    return plot_types


def aggregate_new_parameters(user, filters=None, short=True):
    if not filters:
        filters = []

    sample_ids = get_samples(filters, ids=True)
    samples = get_samples(filters)
    if filters:
        new_filters = [[{"type": "sampleids", "cmp": "inlist", "value": sample_ids}]]
    else:
        new_filters = []

    plot_types = get_plot_types(user, new_filters)
    if not short:
        report_field_keys = get_report_metadata_fields(new_filters)
        sample_fields = get_sample_metadata_fields(new_filters)
        return len(samples), report_field_keys, sample_fields, plot_types
    else:
        return len(samples), plot_types


def build_filter(query, filters, source_table):
    # Build sqlalchemy filters for the provided query based on constants and the provided filters
    alchemy_or_cmps = []
    for filter_group in filters:
        alchemy_and_cmps = []
        for filter_idx, one_filter in enumerate(filter_group):
            params = []
            cmps = []
            if one_filter["type"] == "daterange":
                # daterange : make values actual datetimes
                params = [datetime.strptime(x, "%Y-%m-%d") for x in one_filter["value"]]
                params[1] = params[1] + timedelta(
                    1
                )  # right border is midnight, you usually want to include the date you use as right border
                # in and not in are handled by making 2 filters, default is "in"
                if one_filter["cmp"] == "not in":
                    cmps = ["<=", ">="]
                else:
                    cmps = [">=", "<="]

            elif one_filter["type"] == "date":
                params = [datetime.strptime(one_filter["value"], "%Y-%m-%d")]
                cmps = [one_filter["cmp"]]
            elif one_filter["type"] == "timedelta":
                # timedeltarange : make datetime based on now and reverse the cmp,
                # because time <7 days == time > _date_seven_days_ago
                params = [datetime.now() - timedelta(int(one_filter["value"]))]
                if one_filter["cmp"] in ["gt", ">"]:
                    cmps = ["<="]
                elif one_filter["cmp"] in ["lt", "<"]:
                    cmps = [">="]
                elif one_filter["cmp"] in ["ge", ">="]:
                    cmps = ["<"]
                elif one_filter["cmp"] in ["le", "<="]:
                    cmps = [">"]
            else:
                # default behaviour
                cmps = [one_filter["cmp"]]
                if "not in" == one_filter["cmp"]:
                    # not in is a special case, there is no sqlalchemy operator to deal with it, although there is one for "in" and "notlike"
                    params = ["%{0}%".format(one_filter["value"])]
                else:
                    try:
                        val = float(one_filter["value"])
                        params = [val]
                    except:
                        params = [one_filter["value"]]
                key = one_filter.get("key", None)
                if key:
                    params.append(key)
                    cmps.append("==")
                    # if there is a key/value pair, the cmp only applies to the value, the key should be matched
                key = one_filter.get("section", None)
                if one_filter.get("section"):
                    params.append(one_filter["section"])
                    cmps.append("==")

            # make named joins
            aliased_fields = []
            current_source = source_table
            current_alias = source_table
            for idx, table in enumerate(type_to_tables_fields[one_filter["type"]]):
                aliased_table = aliased(table)
                on_clause = getattr(
                    current_alias, valid_join_conditions[current_source][table][0]
                ).__eq__(
                    getattr(
                        aliased_table, valid_join_conditions[current_source][table][1]
                    )
                )
                if idx == 0:
                    query = query.join(aliased_table, on_clause)
                else:
                    query = query.join(aliased_table)

                current_source = table
                current_alias = aliased_table
                for field in type_to_tables_fields[one_filter["type"]][table]:
                    aliased_fields.append(getattr(aliased_table, field))

            for idx, param in enumerate(params):
                # field is a db_column
                field = aliased_fields[idx]
                if isinstance(params[idx], float):
                    field = cast(field, Numeric)
                # sql_cmp is a comparison function
                sql_cmp = getattr(field, comparators[cmps[idx]])
                alchemy_and_cmps.append(sql_cmp(param))
        alchemy_or_cmps.append(and_(*alchemy_and_cmps))

    query = query.filter(or_(*alchemy_or_cmps))
    # current_app.logger.debug(
    #     query.statement.compile(dialect=db.session.bind.dialect, compile_kwargs={"literal_binds": True})
    # )
    return query


def get_user_filters(user):
    clauses = []
    sfq = db.session.query(SampleFilter)
    clauses.append(SampleFilter.user_id == user.user_id)
    if not user.is_admin:
        clauses.append(SampleFilter.is_public == True)
    sfq.filter(or_(*clauses))
    sfs = sfq.all()
    data = [
        {
            "name": x.sample_filter_name,
            "set": x.sample_filter_tag,
            "id": x.sample_filter_id,
            "filters": json.loads(x.sample_filter_data),
        }
        for x in sfs
    ]
    return data


def update_fav_sample_field(method, user, sample_field_id):
    existing_sample_field = (
        db.session.query(SampleDataType)
        .filter(SampleDataType.sample_data_type_id == sample_field_id)
        .first()
    )
    if not existing_sample_field:
        raise Exception("No such sample_field")
    if method == "save":
        db.session.execute(
            user_sampletype_map.insert().values(
                user_id=user.user_id,
                plot_config_id=existing_sample_field.sample_data_type_id,
            )
        )
    elif method == "delete":
        db.session.execute(
            user_sampletype_map.delete().where(
                and_(
                    user_sampletype_map.c.user_id == user.user_id,
                    user_sampletype_map.c.sample_data_type_id
                    == existing_sample_fielexisting_sample_fieldd.sample_data_type_id,
                )
            )
        )
    else:
        raise Exception("No such method")
    db.session.commit()


def update_fav_report_plot_type(method, user, plot_info):

    existing_plot_config_q = db.session.query(PlotConfig).filter(
        PlotConfig.config_name == plot_info[0]
    )
    if len(plot_info) == 2:
        existing_plot_config_q = existing_plot_config_q.filter(
            PlotConfig.config_dataset == plot_info[1]
        )
    existing_plot_config = existing_plot_config_q.first()
    if not existing_plot_config:
        raise Exception("No such plot")
    if method == "save":
        db.session.execute(
            user_plotconfig_map.insert().values(
                user_id=user.user_id, plot_config_id=existing_plot_config.config_id
            )
        )
    elif method == "delete":
        db.session.execute(
            user_plotconfig_map.delete().where(
                and_(
                    user_plotconfig_map.c.user_id == user.user_id,
                    user_plotconfig_map.c.plot_config_id
                    == existing_plot_config.config_id,
                )
            )
        )
    else:
        raise Exception("No such method")
    db.session.commit()


def get_plot_favourites(user):
    """
    Return a list of the plot favourites for the given user.
    """
    favourite_list_query = (
        db.session.query(
            PlotFavourite.plot_favourite_id,
            PlotFavourite.user_id,
            PlotFavourite.title,
            PlotFavourite.description,
            PlotFavourite.plot_type,
            PlotFavourite.data,
            PlotFavourite.created_at,
        )
        .filter_by(user_id=user.user_id)
        .order_by(PlotFavourite.created_at.desc())
    )
    ret_data = []
    for row in favourite_list_query.all():
        ret_data.append(
            dict(
                plot_favourite_id=row.plot_favourite_id,
                title=row.title,
                description=row.description,
                plot_type=row.plot_type,
                data=json.loads(row.data),
                created_at=row.created_at,
            )
        )
    return ret_data


def get_favourite_plot_data(user, favourite_id):
    """
    Fetch a plot favourite by ID and return the HTML to generate the plot.
    """
    # Get the database row for this favourite
    fp_row = (
        db.session.query(
            PlotFavourite.plot_favourite_id,
            PlotFavourite.user_id,
            PlotFavourite.title,
            PlotFavourite.description,
            PlotFavourite.plot_type,
            PlotFavourite.data,
            PlotFavourite.created_at,
        )
        .filter_by(plot_favourite_id=favourite_id)
        .first()
    )
    # Prep variables
    plot_type = fp_row[4]
    api_data = json.loads(fp_row[5])
    plot_html = '<p class="text-error">Could not find favourite plot</p>'
    # Report plot
    if plot_type == "report_plot":
        plot_type = api_data.get("plot_type")
        filters = api_data.get("filters", [])
        sample_names = get_samples(filters)
        plot_html = generate_report_plot(plot_type, sample_names)
    # Distribution plot
    elif plot_type == "distribution":
        my_filters = get_filter_from_data(api_data)
        data_keys = api_data.get("fields", {})
        nbins = api_data.get("nbins", 20)
        ptype = api_data.get("ptype", 20)
        plot_data = get_sample_fields_values(data_keys, my_filters)
        plot_html = generate_distribution_plot(plot_data, nbins, ptype)
    # Trend plot
    elif plot_type == "trend":
        my_filters = get_filter_from_data(api_data)
        data_keys = api_data.get("fields", {})
        plot_data = get_timeline_sample_data(my_filters, data_keys)
        plot_html = generate_trend_plot(plot_data)
    # Comparison plot
    elif plot_type == "comparison":
        my_filters = get_filter_from_data(api_data)
        data_keys = api_data.get("fields", {})
        field_names = api_data.get("field_names", {})
        pointsize = api_data.get("pointsize", 10)
        joinmarkers = api_data.get("joinmarkers", False)
        plot_data = get_sample_fields_values(
            data_keys.values(), my_filters, num_fieldids=True
        )
        plot_html = generate_comparison_plot(
            plot_data, data_keys, field_names, pointsize, joinmarkers
        )
    else:
        plot_html = '<p class="text-error">Plot type <code>{}</code> not recognised.</p>'.format(
            plot_type
        )
    return {
        "user_id": fp_row[1],
        "title": fp_row[2],
        "description": fp_row[3],
        "plot_type": fp_row[4],
        "created_at": fp_row[6],
        "plot_html": plot_html,
    }


def save_plot_favourite_data(user, plot_type, data, title, description=None):
    """
    Save a new plot favourite to the database.
    """
    new_plot_favourite = PlotFavourite(
        user_id=user.user_id,
        title=title,
        description=description,
        plot_type=plot_type,
        data=json.dumps(data),
    )
    new_plot_favourite.save()
    return new_plot_favourite.plot_favourite_id


def get_dashboards(user):
    """
    Return list of saved dashboards for the user.
    """
    dashboard_list_query = (
        db.session.query(
            Dashboard.dashboard_id,
            Dashboard.user_id,
            Dashboard.title,
            Dashboard.data,
            Dashboard.is_public,
            Dashboard.modified_at,
            Dashboard.created_at,
        )
        .filter_by(user_id=user.user_id)
        .order_by(Dashboard.created_at.desc())
    )
    ret_data = []
    for row in dashboard_list_query.all():
        ret_data.append(
            dict(
                dashboard_id=row.dashboard_id,
                user_id=row.user_id,
                title=row.title,
                data=json.loads(row.data),
                is_public=row.is_public,
                modified_at=row.modified_at,
                created_at=row.created_at,
            )
        )
    return ret_data


def get_dashboard_data(user, dashboard_id):
    """
    Fetch a dashboard by ID and return the data.
    """
    # Get the database row for this favourite
    row = (
        db.session.query(
            Dashboard.dashboard_id,
            Dashboard.user_id,
            Dashboard.title,
            Dashboard.data,
            Dashboard.is_public,
            Dashboard.modified_at,
            Dashboard.created_at,
        )
        .filter(
            or_(Dashboard.user_id == user.user_id, Dashboard.is_public == True),
            Dashboard.dashboard_id == dashboard_id,
        )
        .first()
    )
    if row is None:
        return None
    # Calculate extra variables
    parsed_data = json.loads(row.data)
    max_height = max([d["y"] + d["height"] for d in parsed_data])

    return dict(
        dashboard_id=row.dashboard_id,
        user_id=row.user_id,
        title=row.title,
        data=parsed_data,
        max_height=max_height,
        is_public=row.is_public,
        modified_at=row.modified_at,
        created_at=row.created_at,
    )


def save_dashboard_data(user, title, data, is_public=False, dashboard_id=None):
    """
    Save a dashboard.
    """
    new_dashboard = Dashboard(
        user_id=user.user_id, title=title, data=json.dumps(data), is_public=is_public
    )
    new_dashboard.save()
    return new_dashboard.dashboard_id


def get_sample_fields_values(keys, filters=None, num_fieldids=False):
    if not filters:
        filters = []
    sample_ids = get_samples(filters, ids=True)
    if filters:
        new_filters = [
            [
                {"type": "sampleids", "cmp": "inlist", "value": sample_ids},
                {"type": "samplemetaids", "cmp": "inlist", "value": keys},
            ]
        ]
    else:
        new_filters = [[{"type": "samplemetaids", "cmp": "inlist", "value": keys}]]
    sample_list_query = db.session.query(Sample.sample_name).filter(
        Sample.sample_id.in_(sample_ids)
    )
    sample_meta_ids_query = db.session.query(
        SampleDataType.data_key,
        SampleDataType.data_section,
        SampleDataType.sample_data_type_id,
    ).filter(SampleDataType.sample_data_type_id.in_(keys))
    sample_metadata_query = (
        db.session.query(Sample.sample_name)
        .join(SampleData, Sample.sample_id == SampleData.sample_id)
        .join(
            SampleDataType,
            SampleData.sample_data_type_id == SampleDataType.sample_data_type_id,
        )
        .add_columns(
            SampleDataType.data_key,
            SampleDataType.data_section,
            SampleData.value,
            SampleDataType.sample_data_type_id,
        )
    )
    sample_metadata_query = build_filter(sample_metadata_query, new_filters, SampleData)
    results = {}
    for row in sample_list_query.all():
        results[row[0]] = {}
        for row2 in sample_meta_ids_query.all():
            nicename = (
                row2[0][len(row2[1]) :] if row2[0].startswith(row2[1]) else row2[0]
            )
            nice_section = row2[1].title() if row2[1].islower() else row2[1]
            nicename = "{0}: {1}".format(
                nice_section.replace("_", " "), nicename.replace("_", " ").strip()
            )
            if num_fieldids:
                nicename = row2[2]
            results[row[0]][nicename] = None

    for row in sample_metadata_query.all():
        nicename = row[1][len(row[2]) :] if row[1].startswith(row[2]) else row[1]
        nice_section = row[2].title() if row[2].islower() else row[2]
        nicename = "{0}: {1}".format(
            nice_section.replace("_", " "), nicename.replace("_", " ").strip()
        )
        if num_fieldids:
            nicename = row[4]
        try:
            results[row[0]][nicename] = float(row[3])
        except ValueError:
            results[row[0]][nicename] = row[3]

    return results


def generate_distribution_plot(plot_data, nbins=20, ptype="boxplot"):
    dtypes = set()
    for s_name in plot_data:
        dtypes.update(plot_data[s_name])
    figs = []
    for dtype in sorted(dtypes):
        pdata = []
        for s_name in plot_data:
            try:
                pdata.append(float(plot_data[s_name][dtype]))
            except:
                pass
        if ptype == "boxplot":
            figs.append(go.Box(y=pdata, name="{} ({})".format(dtype, len(pdata))))
        elif ptype == "dotplot":
            figs.append(
                go.Box(
                    y=pdata,
                    name="{} ({})".format(dtype, len(pdata)),
                    boxpoints="all",
                    jitter=0.5,
                    pointpos=0,
                    line=dict(width=0),
                    whiskerwidth=0,
                    fillcolor="rgba(0, 0, 0, 0)",
                )
            )
        elif ptype == "hist":
            figs.append(
                go.Histogram(
                    x=pdata,
                    opacity=0.75,
                    nbinsx=nbins,
                    name="{} ({})".format(dtype, len(pdata)),
                )
            )
        elif ptype == "violin":
            if len(figs) == 0:
                figs = {}
            dname = "{} ({})".format(dtype, len(pdata))
            figs[dname] = pdata
        else:
            return "Error - unrecognised plot type: {}".format(ptype)
    layout = {}
    if ptype == "hist":
        layout = go.Layout(
            barmode="overlay",
            showlegend=True,
            xaxis=dict(title="Data"),
            yaxis=dict(
                title="Sample Count"
                # TODO - integers only
            ),
        )
    if ptype == "violin":
        figure = ff.create_violin(figs)
    else:
        figure = go.Figure(data=figs, layout=layout)
    plot_div = py.plot(
        figure,
        output_type="div",
        show_link=False,
        config=dict(
            modeBarButtonsToRemove=[
                "sendDataToCloud",
                "resetScale2d",
                "hoverClosestCartesian",
                "hoverCompareCartesian",
                "toggleSpikelines",
            ],
            displaylogo=False,
        ),
    )
    return plot_div


def generate_trend_plot(plot_data):
    # return '<pre>{}</pre>'.format(plot_data)
    ptype = "line"
    figs = []
    for field in sorted(plot_data.keys()):
        if ptype == "line":
            yvals = []
            yvalcount = 0
            for x in plot_data[field]:
                try:
                    yvals.append(float(x["value"]))
                    yvalcount += 1
                except ValueError:
                    yvals.append(None)
            figs.append(
                go.Scatter(
                    x=[x["time"] for x in plot_data[field]],
                    y=yvals,
                    mode="markers",
                    text=[x["name"] for x in plot_data[field]],
                    name="{} ({})".format(field, yvalcount),
                    hoverinfo="text+x+y",
                )
            )
        else:
            return "Error - unrecognised plot type: {}".format(ptype)
    plot_div = py.plot(
        go.Figure(data=figs, layout=go.Layout(hovermode="closest")),
        output_type="div",
        show_link=False,
        config=dict(
            modeBarButtonsToRemove=[
                "sendDataToCloud",
                "resetScale2d",
                "hoverClosestCartesian",
                "hoverCompareCartesian",
                "toggleSpikelines",
            ],
            displaylogo=False,
        ),
    )
    return plot_div


def generate_comparison_plot(
    plot_data, data_keys, field_names=None, pointsize=10, joinmarkers=False
):
    if field_names is None:
        field_names = data_keys
    ptitle = "MegaQC Comparison Plot"
    plot_x = []
    plot_y = []
    plot_z = []
    plot_col = []
    plot_size = []
    plot_names = plot_data.keys()
    annotations = go.Annotations([])
    # Sort the data by the x, y variables (needed when joining dots with lines)
    plot_names = sorted(
        plot_names,
        key=lambda s_name: (
            plot_data[s_name][data_keys["x"]],
            plot_data[s_name][data_keys["y"]],
        ),
    )
    # Collect the variables
    for s_name in plot_names:
        try:
            plot_x.append(plot_data[s_name][data_keys["x"]])
            plot_y.append(plot_data[s_name][data_keys["y"]])
        except KeyError:
            current_app.logger.error(
                "Couldn't find key {} (available: {})".format(
                    list(plot_data[s_name].keys()), data_keys
                )
            )
        try:
            plot_z.append(plot_data[s_name][data_keys["z"]])
        except KeyError:
            plot_z.append(None)
        try:
            plot_col.append(plot_data[s_name][data_keys["col"]])
        except KeyError:
            plot_col.append(None)
        try:
            plot_size.append(plot_data[s_name][data_keys["size"]])
        except KeyError:
            plot_size.append(None)

    # Colour with a colour scale
    markers = {}
    if not all([x == None for x in plot_col]):
        markers["color"] = plot_col
        markers["colorscale"] = "Viridis"
        markers["showscale"] = True
        annotations.append(
            go.Annotation(
                text=field_names["col"],
                x=1.02,
                y=0.5,
                textangle=-90,
                xref="paper",
                yref="paper",
                showarrow=False,
            )
        )

    # Scale the marker size according to a variable
    if not all([x == None for x in plot_size]):
        smax = max([x for x in plot_size if type(x) is float])
        smin = min([x for x in plot_size if type(x) is float])
        srange = smax - smin
        if srange > 0:
            norm_plot_size = []
            for x in plot_size:
                if type(x) is float:
                    norm_plot_size.append(((old_div((x - smin), srange)) * 35) + 2)
                else:
                    norm_plot_size.append(2)
            markers["size"] = norm_plot_size
            ptitle += '<br><span style="font-size:0.7rem">Marker Size represents "{}"</span>'.format(
                field_names["size"]
            )
    else:
        markers["size"] = pointsize

    plot_height = 600
    if all([x == None for x in plot_z]):
        fig = go.Scatter(
            x=plot_x,
            y=plot_y,
            mode="lines+markers" if joinmarkers else "markers",
            marker=markers,
            text=plot_names,
        )
    else:
        markers.update({"opacity": 0.8})
        fig = go.Scatter3d(
            x=plot_x,
            y=plot_y,
            z=plot_z,
            mode="markers",
            marker=markers,
            text=plot_names,
        )
        plot_height = 800
    # Make the plot
    layout = go.Layout(
        title=ptitle,
        # For 2D plots
        xaxis=dict(title=field_names["x"]),
        yaxis=dict(title=field_names["y"]),
        # For 3D plots
        scene=dict(
            xaxis=dict(title=field_names["x"]),
            yaxis=dict(title=field_names["y"]),
            zaxis=dict(title=field_names["z"]),
        ),
        annotations=annotations,
        height=plot_height,
    )
    plot_div = py.plot(
        go.Figure(data=[fig], layout=layout),
        output_type="div",
        show_link=False,
        config=dict(
            modeBarButtonsToRemove=[
                "sendDataToCloud",
                "resetScale2d",
                "hoverClosestCartesian",
                "hoverCompareCartesian",
                "toggleSpikelines",
            ],
            displaylogo=False,
        ),
    )
    return plot_div


def update_user_filter(user, method, filter_id, filter_object=None):
    if not filter_object:
        filter_object = []

    if method == "delete":
        SampleFilter.query.filter_by(
            user_id=user.user_id, sample_filter_id=filter_id
        ).delete()
    elif method == "update":
        SampleFilter.query.filter_by(
            user_id=user.user_id, sample_filter_id=filter_id
        ).update({"sample_filter_data": json.dumps(filter_object)})
    db.session.commit()


def get_filter_from_data(data):
    filter_id = int(data.get("filters_id", 0))
    if filter_id:
        # Hardcoded "All Samples" filter set
        if filter_id == -1:
            my_filter = []
        else:
            my_filter = json.loads(
                db.session.query(SampleFilter.sample_filter_data)
                .filter(SampleFilter.sample_filter_id == filter_id)
                .first()[0]
            )
    else:
        my_filter = data.get("filters", [])

    return my_filter


def get_timeline_sample_data(filters, fields):
    if not filters:
        filters = []
    sample_ids = get_samples(filters, ids=True)
    if filters:
        new_filters = [
            [
                {"type": "sampleids", "cmp": "inlist", "value": sample_ids},
                {"type": "samplemetaids", "cmp": "inlist", "value": fields},
            ]
        ]
    else:
        new_filters = [[{"type": "samplemetaids", "cmp": "inlist", "value": fields}]]

    sample_meta_ids_query = db.session.query(
        SampleDataType.data_key, SampleDataType.data_section
    ).filter(SampleDataType.sample_data_type_id.in_(fields))
    sample_metadata_query = (
        db.session.query(Sample.sample_id, Sample.sample_name)
        .join(SampleData, Sample.sample_id == SampleData.sample_id)
        .join(
            SampleDataType,
            SampleData.sample_data_type_id == SampleDataType.sample_data_type_id,
        )
        .join(Report, Report.report_id == Sample.report_id)
        .add_columns(
            SampleDataType.data_key,
            SampleDataType.data_section,
            SampleData.value,
            Report.created_at,
        )
    )
    sample_metadata_query = build_filter(sample_metadata_query, new_filters, SampleData)
    sample_metadata_query = sample_metadata_query.order_by(Report.created_at)
    results = {}
    for row in sample_meta_ids_query.all():
        nicename = row[0][len(row[1]) :] if row[0].startswith(row[1]) else row[0]
        nice_section = row[1].title() if row[1].islower() else row[1]
        nicename = "{0}: {1}".format(
            nice_section.replace("_", " "), nicename.replace("_", " ")
        )
        results[nicename] = []
    for row in sample_metadata_query.all():
        nicename = row[2][len(row[3]) :] if row[2].startswith(row[3]) else row[2]
        nice_section = row[3].title() if row[3].islower() else row[3]
        nicename = "{0}: {1}".format(
            nice_section.replace("_", " "), nicename.replace("_", " ")
        )
        try:
            value = float(row[4])
        except ValueError:
            value = row[4]

        res_dict = {
            "id": row[0],
            "name": row[1],
            "time": row[5].isoformat(),
            "value": value,
        }
        results[nicename].append(res_dict)

    return results


def delete_report_data(report_id):
    PlotData.query.filter(PlotData.report_id == report_id).delete()
    db.session.commit()
    PlotCategory.query.filter(
        PlotCategory.plot_category_id.in_(
            db.session.query(PlotCategory.plot_category_id)
            .outerjoin(PlotData)
            .filter(PlotData.plot_data_id == None)
        )
    ).delete(synchronize_session="fetch")
    db.session.commit()
    db.session.execute(
        user_plotconfig_map.delete().where(
            user_plotconfig_map.c.plot_config_id.in_(
                db.session.query(PlotConfig.config_id)
                .outerjoin(PlotData)
                .filter(PlotData.plot_data_id == None)
            )
        )
    )
    db.session.commit()
    # user_plotconfig_map.query.filter(user_plotconfig_map.plot_config_id.in_(db.session.query(PlotConfig.plot_config_id).outerjoin(PlotData).filter(PlotData.plot_data_id==None))).delete(synchronize_session='fetch')
    PlotConfig.query.filter(
        PlotConfig.config_id.in_(
            db.session.query(PlotConfig.config_id)
            .outerjoin(PlotData)
            .outerjoin(PlotCategory, PlotCategory.config_id == PlotConfig.config_id)
            .filter(
                and_(
                    PlotData.plot_data_id == None, PlotCategory.plot_category_id == None
                )
            )
        )
    ).delete(synchronize_session="fetch")
    db.session.commit()
    SampleData.query.filter(SampleData.report_id == report_id).delete()
    db.session.commit()
    SampleDataType.query.filter(
        SampleDataType.sample_data_type_id.in_(
            db.session.query(SampleDataType.sample_data_type_id)
            .outerjoin(SampleData)
            .filter(SampleData.sample_data_id == None)
        )
    ).delete(synchronize_session="fetch")
    db.session.commit()
    ReportMeta.query.filter(ReportMeta.report_id == report_id).delete()
    db.session.commit()
    Sample.query.filter(Sample.report_id == report_id).delete()
    db.session.commit()
    Report.query.filter(Report.report_id == report_id).delete()
    db.session.commit()


def get_reports_data(count=False, user_id=None, filters=None):
    if not filters:
        filters = []
    if count:
        report_query = db.session.query(func.count(Report.report_id))
        return report_query.one()[0]
    else:
        reports_query = (
            db.session.query(Report, User.username)
            .join(User, Report.user_id == User.user_id)
            .order_by(Report.report_id)
        )
        if user_id:
            reports_query = reports_query.filter(Report.user_id == user_id)
        if filters:
            reports_query = reports_query.join(ReportMeta).filter(
                and_(
                    ReportMeta.report_meta_key == filters[0],
                    ReportMeta.report_meta_value == filters[1],
                )
            )
        reports = reports_query.all()
        ret_data = []
        for report in reports:
            ret = {
                "report_id": report[0].report_id,
                "report_hash": report[0].report_hash,
                "upload_date": report[0].created_at,
                "username": report[1],
            }
            # Get the metadata pairs for this report
            report_md_query = db.session.query(ReportMeta).filter(
                ReportMeta.report_id == report[0].report_id
            )
            report_md = report_md_query.all()
            for md in report_md:
                ret[md.report_meta_key] = md.report_meta_value

            ret_data.append(ret)
        return ret_data


def get_queued_uploads(count=False, filter_cats=None):
    if filter_cats is None:
        # Exclude "TREATED" by default
        filter_cats = ["NOT TREATED", "IN TREATMENT", "FAILED"]
    if count:
        uploads_query = db.session.query(func.count(Upload.upload_id)).filter(
            Upload.status.in_(filter_cats)
        )
        return uploads_query.one()[0]
    else:
        uploads_query = (
            db.session.query(Upload)
            .filter(Upload.status.in_(filter_cats))
            .order_by(Upload.created_at.desc())
        )
        uploads = uploads_query.all()
        ret_data = []
        for upload in uploads:
            status_class = "secondary"
            if upload.status == "TREATED":
                status_class = "success"
            elif upload.status == "NOT TREATED":
                status_class = "info"
            elif upload.status == "IN TREATMENT":
                status_class = "warning"
            elif upload.status == "FAILED":
                status_class = "danger"
            ret_data.append(
                {
                    "upload_id": upload.upload_id,
                    "status": upload.status,
                    "status_class": status_class,
                    "upload_date": upload.created_at,
                    "message": upload.message,
                }
            )
        return ret_data
