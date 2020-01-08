from megaqc.model import models
from datetime import datetime, timedelta
from sqlalchemy.orm import Query
from megaqc.database import db
from sqlalchemy.dialects import postgresql

DATE_FORMAT = "%Y-%m-%d"


def add_operator(lhs, op, rhs):
    """
    Returns an SQLAlchemy expression comparing two values
    """
    if op == 'eq':
        return lhs == rhs
    elif op == 'ne':
        return lhs != rhs
    elif op == 'le':
        return lhs <= rhs
    elif op == 'lt':
        return lhs < rhs
    elif op == 'ge':
        return lhs >= rhs
    elif op == 'gt':
        return lhs > rhs
    else:
        raise ValueError('"op" must have a valid value.')


def concat_clauses(clauses, operator):
    """
    Combines a list of SQL clauses using the provided operator
    :type clauses: list
    :type operator: str
    :param operator: "and" or "or"
    """
    concat = None

    for clause in clauses:
        if concat is None:
            # If this is the first clause, use it as the basis for the rest of the query
            concat = clause
        elif operator == 'and':
            concat &= clause
        elif operator == 'or':
            concat |= clause
        else:
            raise Exception('Operator must be "and" or "or", not "{}"'.format(operator))

    return concat


def round_date(date, direction):
    if direction == 'up':
        date = date + timedelta(days=1)

    return date.replace(hour=0, minute=0, second=0, microsecond=0)


def build_filter_query(filters):
    """
    Returns an SQLAlchemy query with the provided filters applied. Note that this query will not actually select any
    data by itself, so you will likely want to add .with_entities().all() to the result of this function
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
            if filter['type'] == 'daterange':
                # Finding all reports between two fixed dates

                # Select reports between the two dates
                clause = models.Report.created_at.between(

                    # Set the left boundary to midnight on the day indicated, so it covers that entire day
                    round_date(datetime.strptime(filter['value'][0], DATE_FORMAT), 'down'),

                    # Set the right boundary to midnight on the day after indicated
                    round_date(datetime.strptime(filter['value'][1], DATE_FORMAT), 'up')
                )

                # Negate the clause if we want those not in the range
                if filter['cmp'] == 'not in':
                    and_filters.append(~clause)
                else:
                    and_filters.append(clause)

            elif filter['type'] == 'date':
                # Finding all reports produced on this date
                and_filters.append(add_operator(
                    models.Report.created_at,
                    filter['cmp'],
                    filter['value'][0]
                ))

            elif filter['type'] == 'timedelta':
                # Finding all reports produced between now and some amount of days prior to now
                clause = models.Report.created_at.between(
                    round_date(datetime.now() - timedelta(days=filter['value'][0]), 'down'),
                    round_date(datetime.now(), 'up')
                )

                # Negate the clause if we want those not in the range
                if filter['cmp'] == 'not in':
                    and_filters.append(~clause)
                else:
                    and_filters.append(clause)

            elif filter['type'] == 'reportmeta':
                # Finding all samples with the given metadata
                and_filters.append(
                    # The report metadata is stored as rows of key, value pairs, so we need to select both
                    (models.ReportMeta.report_meta_key == filter['key'])
                    & add_operator(models.ReportMeta.report_meta_value, filter['cmp'], filter['value'][0])
                )

            elif filter['type'] == 'samplemeta':
                # Finding all samples with the given data
                and_filters.append(
                    # The report metadata is stored as rows of key, value pairs, so we need to select both
                    (models.SampleDataType.data_key == filter['key'])
                    & add_operator(models.SampleData.value, filter['cmp'], filter['value'][0])
                )
            else:
                raise Exception('Unsupported filter type "{}"'.format(filter['type']))

        or_filters.append(concat_clauses(and_filters, 'and'))

    query = db.session.query(
        models.Sample
    ).join(
        models.SampleData,
        isouter=True
    ).join(
        models.SampleDataType, models.SampleData.sample_data_type_id == models.SampleDataType.sample_data_type_id,
        isouter=True
    ).join(
        models.Report, models.Report.report_id == models.Sample.report_id,
        isouter=True
    ).join(
        models.ReportMeta, models.ReportMeta.report_id == models.Report.report_id,
        isouter=True
    )

    # A unified clause that does all the filtering demanded by the user
    filter_clause = concat_clauses(or_filters, 'or')
    if filter_clause is not None:
        return query.filter(filter_clause)
    else:
        return query
