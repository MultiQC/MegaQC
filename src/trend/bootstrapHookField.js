import React from "react";
import { Input, FormFeedback } from "reactstrap";
import { ErrorMessage, getIn } from "formik";

/**
 * For use with Formik's useField()
 */
export default function BootstrapField({ input, meta, helper, ...rest }) {
  const invalid = meta.touched && meta.error;
  const valid = meta.touched && !meta.error;

  return (
    <>
      <Input valid={valid} invalid={invalid} {...rest} />
      <ErrorMessage name={input.name}>
        {msg => <FormFeedback valid={!invalid}>{msg}</FormFeedback>}
      </ErrorMessage>
    </>
  );
}
