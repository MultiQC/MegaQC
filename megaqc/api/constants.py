
from megaqc.model.models import *
from collections import OrderedDict

type_to_tables_fields={
        'daterange': {Report:['created_at','created_at']},
        'timedelta':{Report:['created_at']},
        'samplenames':{Sample:['sample_name']},
        'reportmeta':{ReportMeta:['report_meta_value', 'report_meta_key']},
        'samplemeta':OrderedDict([(SampleData,['value']), (SampleDataType,['data_key', 'data_section'])])
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
        'inlist':'in_',
        'ne':'__ne__',
        '!=':'__ne__',
        'not in':'notlike'
}
