/**
 * One row of the newFilter dialogue
 **/

import React, { useEffect } from "react";
import { Field, connect, getIn } from "formik";
import { Button, FormGroup } from "reactstrap";
import BootstrapField from "./bootstrapField";
import BootstrapDateField from "./bootstrapDateField";
import Filter from "../util/filter";

function FilterRow(props) {
  const { sampleFields, reportFields, name, formik, innerArrayHelpers } = props;
  const currentType = getIn(formik.values, name + ".type");

  useEffect(() => {
    let newFilter;
    switch (currentType) {
      case "daterange":
        newFilter = {
          type: currentType,
          cmp: "in",
          key: null,
          value: [new Date(), new Date()]
        };
        break;
      case "timedelta":
        newFilter = {
          type: currentType,
          cmp: "in",
          key: null,
          value: [new Date()]
        };
        break;
      case "samplemeta":
        newFilter = {
          type: currentType,
          cmp: "eq",
          key: sampleFields[0],
          value: [""]
        };
        break;
      case "reportmeta":
        newFilter = {
          type: currentType,
          cmp: "eq",
          key: reportFields[0],
          value: [""]
        };
        break;
    }

    // Whenever the type changes, reset the select values
    formik.setFieldValue(name, newFilter);
  }, [currentType]);

  // Comparison operators for range types
  const rangeCmp = [
    <option value="in">In</option>,
    <option value="not in">Not In</option>
  ];

  // Comparison operators for value types
  const valCmp = [
    <option value="eq">=</option>,
    <option value="neq">&ne;</option>,
    <option value="le">&le;</option>,
    <option value="lt">&le;</option>,
    <option value="ge">&ge;</option>,
    <option value="gt">&gt;</option>
  ];

  // Generate the right fields for each column in the row
  let keyComponent, cmpComponent, valueComponent;
  switch (currentType) {
    case "daterange":
      keyComponent = null;
      cmpComponent = (
        <Field component={BootstrapField} name={`${name}.cmp`} type={"select"}>
          {rangeCmp}
        </Field>
      );
      valueComponent = (
        <>
          <Field
            component={BootstrapDateField}
            views={["year", "month", "date"]}
            openTo={"month"}
            format={"DD/MM/YYYY"}
            name={`${name}.value.0`}
            outputFormat={"YYYY-MM-DD"}
            type={"date"}
          />
          &nbsp;
          <Field
            component={BootstrapDateField}
            views={["year", "month", "date"]}
            openTo={"month"}
            format={"DD/MM/YYYY"}
            outputFormat={"YYYY-MM-DD"}
            name={`${name}.value.1`}
            type={"date"}
          />
        </>
      );
      break;
    case "timedelta":
      keyComponent = null;
      cmpComponent = (
        <Field component={BootstrapField} name={`${name}.cmp`} type={"select"}>
          {rangeCmp}
        </Field>
      );
      valueComponent = (
        <>
          <Field
            component={BootstrapField}
            name={`${name}.value.0`}
            type={"number"}
          />
        </>
      );
      break;
    case "samplemeta":
      keyComponent = (
        <Field component={BootstrapField} name={`${name}.key`} type={"select"}>
          {sampleFields.map(field => {
            return <option value={field}>{field}</option>;
          })}
        </Field>
      );
      cmpComponent = (
        <Field component={BootstrapField} name={`${name}.cmp`} type={"select"}>
          {valCmp}
        </Field>
      );
      valueComponent = (
        <>
          <Field component={BootstrapField} name={`${name}.value.0`} />
        </>
      );
      break;
    case "reportmeta":
      keyComponent = (
        <Field component={BootstrapField} name={`${name}.key`} type={"select"}>
          {reportFields.map(field => {
            return <option value={field}>{field}</option>;
          })}
        </Field>
      );
      cmpComponent = (
        <Field component={BootstrapField} name={`${name}.cmp`} type={"select"}>
          {valCmp}
        </Field>
      );
      valueComponent = (
        <>
          <Field component={BootstrapField} name={`${name}.value.0`} />
        </>
      );
      break;
  }

  return (
    <>
      <td>
        <FormGroup>
          <Field
            component={BootstrapField}
            name={`${name}.type`}
            type={"select"}
          >
            <option value="timedelta">Dynamic date range</option>
            <option value="daterange">Specific dates</option>
            <option value="reportmeta">Report metadata</option>
            <option value="samplemeta">Sample data</option>
          </Field>
        </FormGroup>
      </td>
      <td>
        <FormGroup>{keyComponent}</FormGroup>
      </td>
      <td>
        <FormGroup>{cmpComponent}</FormGroup>
      </td>
      <td>
        <FormGroup>{valueComponent}</FormGroup>
      </td>
      <td>
        <Button
          onClick={() => {
            innerArrayHelpers.push(new Filter());
          }}
          size={"sm"}
          color={"primary"}
        >
          <i className="fa fa-fw fa-plus-square" aria-hidden="true" />
          Add
        </Button>
      </td>
    </>
  );
}

export default connect(FilterRow);
