import dash_html_components as html
import dash_core_components as dcc
import dash
import plotly.graph_objs as go
from numpy import std, mean, repeat, concatenate, flip

from megaqc.dash import MegaQcDash
from megaqc.extensions import db
from megaqc.api.utils import get_sample_metadata_fields
from megaqc.model.models import Sample, SampleData, SampleDataType, Report


def get_field_options():
    with app.server.app_context():
        fields = get_sample_metadata_fields()
        print(fields)
    return [{'label': d['nicename'], 'value': d['type_id']} for d in fields]


def get_plot(fields=[]):
    plots = []
    for field in fields:
        data = db.session.query(
            Report.created_at,
            SampleData.value
        ).select_from(
            Sample
        ).join(
            SampleData, Sample.sample_id == SampleData.sample_id
        ).join(
            SampleDataType, SampleData.sample_data_type_id == SampleDataType.sample_data_type_id
        ).join(
            Report, Report.report_id == Sample.report_id
        ).filter(
            SampleDataType.sample_data_type_id == field
        ).order_by(
            Report.created_at.asc(),
        ).all()

        x, y = zip(*data)
        y = [float(num) for num in y]

        # Add the raw data
        plots.append(go.Scatter(
            x=x,
            y=y,
            line=dict(color='rgb(0,100,80)'),
            mode='markers',
            name=field,
        ))

        # Add the mean
        y2 = repeat(mean(y), len(x))
        plots.append(go.Scatter(
            x=x,
            y=y2,
            line=dict(color='rgb(0,100,80)'),
            mode='lines',
            showlegend=False,
        ))

        # Add the stdev
        x3 = concatenate((x, flip(x, axis=0)))
        stdev = repeat(std(y), len(x))
        upper = y2 + stdev
        lower = y2 - stdev
        y3 = concatenate((lower, upper))
        plots.append(go.Scatter(
            x=x3,
            y=y3,
            fill='tozerox',
            fillcolor='rgba(0,100,80,0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            # line=dict(color='rgb(0,100,80)'),
            # mode='lines',
            showlegend=False,
        ))

    return go.Figure(
        data=plots,
        layout=go.Layout(
            title='Data Trend',
            # showlegend=True,
            # legend=go.layout.Legend(
            #     x=0,
            #     y=1.0
            # ),
            # margin=go.layout.Margin(l=40, r=0, t=40, b=30)
        )
    )


def layout():
    if app.server is not None and 'SQLALCHEMY_TRACK_MODIFICATIONS' in app.server.config:
        fields = get_field_options()
    else:
        fields = []

    return html.Div(children=[
        dcc.Location(id='url', refresh=False),

        html.H1(children='Trends'),

        dcc.Dropdown(
            options=fields,
            id='field_select',
            multi=True,
        ),

        dcc.Graph(
            id='trend',
            figure=get_plot()
        )
    ])


app = MegaQcDash(routes_pathname_prefix='/dash/trend/', server=False)
app.layout = layout


@app.callback(
    dash.dependencies.Output('trend', 'figure'),
    [dash.dependencies.Input('field_select', 'value')]
)
def update_fields(field):
    if field is None:
        field = []
    return get_plot(field)
