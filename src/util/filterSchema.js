import * as Yup from "yup";

const schema = Yup.object().shape({
  filterName: Yup.string().min(3).label("Filter name").required(),
  filterGroup: Yup.string().label("Filter group").required(),
  visibility: Yup.string()
    .oneOf(["private", "public"])
    .label("Visibility")
    .required(),
  filters: Yup.array().of(
    Yup.array()
      .strict()
      .of(
        Yup.object().shape({
          type: Yup.string()
            .oneOf([
              "timedelta",
              "daterange",
              "reportmeta",
              "samplemeta",
              "samplelist",
            ])
            .label("Type")
            .required(),
          key: Yup.mixed()
            .label("Key")
            .when("type", {
              is: (val) => ["samplemeta", "reportmeta"].includes(val),
              then: Yup.string().required(),
              otherwise: Yup.mixed().notRequired(),
            }),
          cmp: Yup.string()
            .label("Comparison")
            .required()
            .when("type", {
              is: (val) => ["samplemeta", "reportmeta"].includes(val),
              then: Yup.string().oneOf([
                "eq",
                "ne",
                "le",
                "lt",
                "ge",
                "gt",
                "contains",
                "like",
                "startswith",
                "endswith",
                "notcontains",
                "notlike",
                "notstartswith",
                "notendswith",
              ]),
              otherwise: Yup.string().oneOf(["in", "not in"]),
            }),
          value: Yup.array().label("Value").required(),
        })
      )
  ),
});
export default schema;
