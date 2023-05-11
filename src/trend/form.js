import React from "react";
import { Card, CardBody, CardHeader, FormGroup, Label } from "reactstrap";
import OutlierDetection from "./outlierDetection";
import { Field, Formik } from "formik";
import BootstrapField from "./bootstrapField";
import PropTypes from "prop-types";
import validator from "@rjsf/validator-ajv8";
import Form from "@rjsf/bootstrap-4";
import schema from "./trendSchema.json";

const log = (type) => console.log.bind(console, type);

export default function TrendForm({ dataTypes, onSubmit }) {
  return (
    <Form
      schema={schema}
      validator={validator}
      onChange={log("changed")}
      onSubmit={log("submitted")}
      onError={log("errors")}
    />
  );
}
