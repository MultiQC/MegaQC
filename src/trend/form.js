import React, { useEffect } from "react";
import { Card, CardBody, CardHeader, Form, FormGroup, Label } from "reactstrap";
import OutlierDetection from "./outlierDetection";
import { Field, Formik } from "formik";
import BootstrapField from "./bootstrapField";
import PropTypes from "prop-types";
import * as Yup from "yup";
import AutoSave from "../util/autoSave";

export default function TrendForm({ dataTypes, onSubmit }) {
  return (
    <Formik
      initialValues={{
        // Which field to plot
        fields: [],
        controlLimits: true,
        statistic: "measurement",
        statisticOptions: {
          centerLine: "mean",
        },
      }}
      validationSchema={Yup.object().shape({
        fields: Yup.array().min(1).label("Data Types"),
        // Outlier has its own internal field validation
        statistic: Yup.string()
          .oneOf(["measurement", "iforest"])
          .label("Statistic"),
        statisticOptions: Yup.object().shape({
          centerLine: Yup.string()
            .oneOf(["mean", "median", "none"])
            .label("Center Line")
            .optional(),
          contamination: Yup.number()
            .min(0)
            .label("Significance Level")
            .optional(),
        }),
      })}
      onSubmit={onSubmit}
    >
      {({ setFieldValue, values }) => {
        // Dynamically change defaults
        useEffect(() => {
          if (values.statistic === "iforest") {
            setFieldValue("statisticOptions", {
              contamination: 0.05,
            });
          } else {
            setFieldValue("statisticOptions", {
              centerLine: "mean",
            });
          }
        }, [values.statistic]);
        // Whenever the plot data type or filter changes, we have to re-calculate the plot data

        return (
          <Card>
            <AutoSave debounceMs={100} />
            <CardHeader>
              <h2>Options</h2>
            </CardHeader>
            <CardBody>
              <Form>
                <FormGroup>
                  <Label>Data Types</Label>
                  <Field
                    component={BootstrapField}
                    name={"fields"}
                    type={"select"}
                    multiple={true}
                    onChange={(e) => {
                      setFieldValue(
                        "fields",
                        Array.from(e.target.selectedOptions).map(
                          (opt) => opt.value
                        )
                      );
                    }}
                  >
                    {dataTypes.map((type, i) => {
                      return (
                        <option key={i} value={type.id}>
                          {type.nice_name}
                        </option>
                      );
                    })}
                  </Field>
                </FormGroup>
                <FormGroup>
                  <Label>Statistic</Label>
                  <Field
                    component={BootstrapField}
                    name={"statistic"}
                    type={"select"}
                    on
                  >
                    <option value="measurement">Raw Measurement</option>
                    <option value="iforest">Isolation Forest</option>
                  </Field>
                </FormGroup>
                {values.statistic == "measurement" && (
                  <FormGroup>
                    <Label>Center Line</Label>
                    <Field
                      component={BootstrapField}
                      name={"statisticOptions.centerLine"}
                      type={"select"}
                    >
                      <option value="median">Median</option>
                      <option value="mean">Mean</option>
                      <option value="none">None</option>
                    </Field>
                  </FormGroup>
                )}
                {values.statistic == "iforest" && (
                  <FormGroup>
                    <Label>Contamination Level</Label>
                    <Field
                      component={BootstrapField}
                      name={"statisticOptions.contamination"}
                      type={"number"}
                      step="0.01"
                      min="0.01"
                    />
                  </FormGroup>
                )}
              </Form>
            </CardBody>
          </Card>
        );
      }}
    </Formik>
  );
}

TrendForm.propTypes = {
  dataTypes: PropTypes.array.isRequired,
  onSubmit: PropTypes.func.isRequired,
};
