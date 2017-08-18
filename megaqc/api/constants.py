
from megaqc.model.models import *

type_to_fields={
        'daterange': [Report.created_at,Report.created_at],
        'timedelta':[Report.created_at],
        'reportmeta':[ReportMeta.report_meta_value, ReportMeta.report_meta_key],
        'samplemeta':[SampleData.value, SampleDataType.data_key]
}
comparators={
        'gt':'__gt__',
        '>':'__gt__',
        '<':'__lt__',
        'lt':'__lt__',
        'ge':'__ge__',
        '>=':'__ge__',
        '<=':'__le__',
        'le':'__le__',
        'eq':'__eq__',
        '==':'__eq__',
        '=':'__eq__',
        'in':'contains',
        'ne':'__ne__',
        '!=':'__ne__',
        'not in':'notlike'
}
