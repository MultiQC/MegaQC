import React from "react";
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
        // What outlier detection (if any) to use
        // outlier: null,
        // The statistic plotted on the center line
        centerLine: "mean",
        // Whether or not to show control limits
        controlLimits: true,
        alpha: 0.0013499,
        statistic: "measurement",
      }}
      validationSchema={Yup.object().shape({
        fields: Yup.array().min(1).label("Data Types"),
        // Outlier has its own internal field validation
        statistic: Yup.string()
          .oneOf(["measurement", "iforest"])
          .label("Statistic"),
        centerLine: Yup.string()
          .oneOf(["mean", "median", "none"])
          .label("Center Line"),
        controlLimits: Yup.bool().label("Show Control Limits"),
        alpha: Yup.number().min(0).label("Significance Level"),
      })}
      onSubmit={onSubmit}
    >
      {({ setFieldValue }) => {
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
                  <Label>Center Line</Label>
                  <Field
                    component={BootstrapField}
                    name={"centerLine"}
                    type={"select"}
                  >
                    <option value="median">Median</option>
                    <option value="mean">Mean</option>
                    <option value="none">None</option>
                  </Field>
                </FormGroup>
                <FormGroup check>
                  <Label check>
                    <Field
                      component={BootstrapField}
                      name={"controlLimits"}
                      type={"checkbox"}
                    />
                    &nbsp; Show Control Limits
                  </Label>
                </FormGroup>
                <FormGroup>
                  <Label>Statistic</Label>
                  <Field
                    component={BootstrapField}
                    name={"statistic"}
                    type={"select"}
                  >
                    <option value="measurement">Raw Measurement</option>
                    <option value="iforest">Isolation Forest</option>
                  </Field>
                </FormGroup>
                <FormGroup>
                  <Label>Outlier Significance Level</Label>
                  <Field
                    component={BootstrapField}
                    name={"alpha"}
                    type={"number"}
                  />
                </FormGroup>
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
