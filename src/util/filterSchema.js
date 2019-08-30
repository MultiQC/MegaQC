import * as Yup from 'yup';

const schema = Yup.object().shape({
    filterName: Yup.string().min(3).label('Filter name').required(),
    filterGroup: Yup.string().label('Filter group').required(),
    visibility: Yup.string().oneOf(['private', 'public']).label('Visibility').required(),
    filters: Yup.array().of(
        Yup.array().of(
            Yup.object().shape({
                type: Yup.string().oneOf(['timedelta', 'daterange', 'reportmeta', 'samplemeta']).label('Type').required(),
                key: Yup.string().label('Key').required(),
                comparison: Yup.string().oneOf([
                    "in",
                    "not in",
                    "eq",
                    "ne",
                    "le",
                    "lt",
                    "ge",
                    "gt"
                ]).label('Comparison').required(),
                value: Yup.mixed().label('Value').required()
            })
        )
    )
});
export default schema;