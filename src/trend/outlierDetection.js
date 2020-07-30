import React from "react";
import { FormGroup, Label } from "reactstrap";
import BootstrapField from "./bootstrapField";
import * as Yup from "yup";
import BootstrapHookField from "./bootstrapHookField";
import AutoSave from "../util/autoSave";

import { Field, Formik, useField } from "formik";

/**
 * Converts a yup schema to a function that can be used to validate a formik field
 * @param yup
 */
function yupToMessage(yup) {
  return value => {
    return yup
      .validate(value)
      .then(() => {
        // If the promise succeeded, then the validation succeeded, so return no
        // error
        return undefined;
      })
      .catch(err => {
        // If the promise failed, then convert it into a message
        return err.join(",");
      });
  };
}

export default function OutlierDetection(
  outlierType = "outlierType",
  outlierThreshold = "outlierThreshold"
) {
  let thresholdName, showThreshold;
  const [typeField, typeMeta, typeHelpers] = useField({
    name: outlierType,
    validate: yupToMessage(
      Yup.string()
        .oneOf(["z", "none"])
        .label("Outlier Detection Method")
    ),
    type: "select",
    label: "Outlier Detection Method"
  });
  const [thresholdField, thresholdMeta, thresholdHelpers] = useField({
    name: outlierThreshold,
    validate: yupToMessage(Yup.number().label("Outlier Detection Threshold")),
    type: "number",
    label: "Outlier Detection Threshold"
  });

  switch (typeField.value) {
    case "none":
      thresholdName = "";
      showThreshold = false;
      break;
    case "grubbs":
      thresholdName = "Alpha value";
      showThreshold = true;
      break;
    case "z":
      thresholdName = "Z-score";
      showThreshold = true;
      break;
    default:
      showThreshold = false;
      thresholdName = "";
      break;
  }

  return (
    <>
      <AutoSave debounceMs={300} />

      <FormGroup>
        <Label>Outlier Detection Method</Label>
        <BootstrapHookField
          input={typeField}
          meta={typeMeta}
          helpers={typeHelpers}
          type={"select"}
        >
          <option value={"none"}>None</option>
          <option value={"grubbs"}>Grubbs test</option>
          <option value={"z"}>Z-score</option>
        </BootstrapHookField>
      </FormGroup>
      {showThreshold && (
        <FormGroup>
          <Label>{thresholdName}</Label>
          <BootstrapField
            input={thresholdField}
            meta={thresholdMeta}
            helpers={thresholdHelpers}
            type={"number"}
          />
        </FormGroup>
      )}
    </>
  );
}
