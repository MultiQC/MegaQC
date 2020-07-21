from datetime import datetime, timedelta

from megaqc.model.models import *
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Query

DATE_FORMAT = "%Y-%m-%d"


def add_operator(lhs, op, rhs):
    """
    Returns an SQLAlchemy expression comparing two values.
    """
    if op[:3] == "not":
        op = op[3:]
        invert = True
    else:
        invert = False

    if op == "eq":
        ret = lhs == rhs
    elif op == "ne":
        ret = lhs != rhs
    elif op == "le":
        ret = lhs <= rhs
    elif op == "lt":
        ret = lhs < rhs
    elif op == "ge":
        ret = lhs >= rhs
    elif op == "gt":
        ret = lhs > rhs
    elif op == "like":
        ret = lhs.ilike(rhs)
    elif op == "contains":
        ret = lhs.contains(rhs, autoescape=True)
    elif op == "startswith":
        ret = lhs.startswith(rhs, autoescape=True)
    elif op == "endswith":
        ret = lhs.endswith(rhs, autoescape=True)
    else:
        raise ValueError('"op" must have a valid value.')

    if invert:
        return ~ret
    else:
        return ret


def concat_clauses(clauses, operator):
    """
    Combines a list of SQL clauses using the provided operator.

    :type clauses: list
    :type operator: str
    :param operator: "and" or "or"
    """
    concat = None

    for clause in clauses:
        if concat is None:
            # If this is the first clause, use it as the basis for the rest of the query
            concat = clause
        elif operator == "and":
            concat &= clause
        elif operator == "or":
            concat |= clause
        else:
            raise Exception('Operator must be "and" or "or", not "{}"'.format(operator))

    return concat


def round_date(date, direction):
    if direction == "up":
        date = date + timedelta(days=1)

    return date.replace(hour=0, minute=0, second=0, microsecond=0)


def build_filter_query(filters):
    """
    Returns an SQLAlchemy query with the provided filters applied. This filter
    will only select Sample IDs that meet the filter, so you should only use
    this as a subquery.

    :param filters: Array of filters in the MegaQC filter format (each filter is a dictionary)
    :type filters: list
    :rtype: Query
    """
    # The outermost group are joined by boolean OR
    or_filters = []
    for filter_group in filters:

        # The innermost group are joined by boolean AND
        and_filters = []
        for filter in filter_group:
            if filter["type"] == "daterange":
                # Finding all reports between two fixed dates

                # Select reports between the two dates
                clause = Report.created_at.between(
                    # Set the left boundary to midnight on the day indicated, so it covers that entire day
                    round_date(
                        datetime.strptime(filter["value"][0], DATE_FORMAT), "down"
                    ),
                    # Set the right boundary to midnight on the day after indicated
                    round_date(
                        datetime.strptime(filter["value"][1], DATE_FORMAT), "up"
                    ),
                )

                # Negate the clause if we want those not in the range
                if filter["cmp"] == "not in":
                    and_filters.append(~clause)
                else:
                    and_filters.append(clause)

            elif filter["type"] == "date":
                # Finding all reports produced on this date
                and_filters.append(
                    add_operator(Report.created_at, filter["cmp"], filter["value"][0])
                )

            elif filter["type"] == "timedelta":
                # Finding all reports produced between now and some amount of days prior to now
                clause = Report.created_at.between(
                    round_date(
                        datetime.now() - timedelta(days=filter["value"][0]), "down"
                    ),
                    round_date(datetime.now(), "up"),
                )

                # Negate the clause if we want those not in the range
                if filter["cmp"] == "not in":
                    and_filters.append(~clause)
                else:
                    and_filters.append(clause)

            elif filter["type"] == "reportmeta":
                # Finding all samples with the given metadata
                and_filters.append(
                    # The report metadata is stored as rows of key, value pairs, so we need to select both
                    (ReportMeta.report_meta_key == filter["key"])
                    & add_operator(
                        ReportMeta.report_meta_value, filter["cmp"], filter["value"][0]
                    )
                )

            elif filter["type"] == "samplemeta":
                # Finding all samples with the given data
                and_filters.append(
                    # The report metadata is stored as rows of key, value pairs, so we need to select both
                    (SampleDataType.data_key == filter["key"])
                    & add_operator(SampleData.value, filter["cmp"], filter["value"][0])
                )
            else:
                raise Exception('Unsupported filter type "{}"'.format(filter["type"]))

        or_filters.append(concat_clauses(and_filters, "and"))

    query = (
        db.session.query(Sample)
        .join(SampleData, isouter=True)
        .join(
            SampleDataType,
            SampleData.sample_data_type_id == SampleDataType.sample_data_type_id,
            isouter=True,
        )
        .join(Report, Report.report_id == Sample.report_id, isouter=True)
        .join(ReportMeta, ReportMeta.report_id == Report.report_id, isouter=True)
        .with_entities(Sample.sample_id)
    )

    # A unified clause that does all the filtering demanded by the user
    filter_clause = concat_clauses(or_filters, "or")
    if filter_clause is not None:
        return query.filter(filter_clause)
    else:
        return query
