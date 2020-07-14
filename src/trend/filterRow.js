/**
 * One row of the newFilter dialogue
 **/

import React, { useEffect, useState, useRef } from "react";
import { Field, connect, getIn } from "formik";
import {
  Button,
  FormGroup,
  Popover,
  PopoverHeader,
  PopoverBody,
  InputGroup,
  InputGroupAddon,
  InputGroupText,
  Input
} from "reactstrap";
import BootstrapField from "./bootstrapField";
import DateRangeField from "./DateRangeField";
import { format, parse } from "date-fns";
import { DATE_FORMAT } from "../util/filter";

function FilterRow(props) {
  const {
    sampleFields,
    reportFields,
    name,
    formik,
    innerArrayHelpers,
    index
  } = props;

  const rowError = getIn(formik.errors, name);
  const errorMsg = rowError instanceof String ? rowError : "";

  const prevType = useRef();
  const [popoverOpen, setPopoverOpen] = useState(false);
  const toggle = () => setPopoverOpen(!popoverOpen);
  const currentType = getIn(formik.values, name + ".type");
  prevType.current = currentType;

  useEffect(() => {
    let newFilter;
    switch (currentType) {
      case "daterange":
        newFilter = {
          type: currentType,
          cmp: "in",
          key: null,
          value: [new Date(), new Date()].map(d => format(d, DATE_FORMAT))
        };
        break;
      case "timedelta":
        newFilter = {
          type: currentType,
          cmp: "in",
          key: null,
          value: [1]
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

  if (currentType !== prevType.current) {
    // If the type has changed, rendering is going to be messy, so don't bother
    return null;
  }

  // Comparison operators for range types
  const dateRangeCmp = [
    <option key="in" value="in">
      inside range
    </option>,
    <option key="not in" value="not in">
      outside range
    </option>
  ];

  const dynamicDateCmp = [
    <option key="in" value="in">
      within
    </option>,
    <option key="not in" value="not in">
      outside
    </option>
  ];

  // Comparison operators for value types
  const valCmp = [
    <option value="eq">=</option>,
    <option value="neq">&ne;</option>,
    <option value="le">&le;</option>,
    <option value="lt">&lt;</option>,
    <option value="ge">&ge;</option>,
    <option value="gt">&gt;</option>,
    <option value="like">matches</option>,
    <option value="contains">contains</option>,
    <option value="startswith">starts with</option>,
    <option value="endswith">ends with</option>,
    <option value="notlike">doesn't match</option>,
    <option value="notcontains">doesn't contain</option>,
    <option value="notstartswith">doesn't start with</option>,
    <option value="notendswith">doesn't end with</option>
  ];

  // Generate the right fields for each column in the row
  let keyComponent, cmpComponent, valueComponent;
  switch (currentType) {
    case "daterange":
      keyComponent = null;
      cmpComponent = (
        <Field component={BootstrapField} name={`${name}.cmp`} type={"select"}>
          {dateRangeCmp}
        </Field>
      );
      valueComponent = (
        <>
          <Field
            component={DateRangeField}
            // views={["year", "month", "date"]}
            // openTo={"month"}
            dateFormat={"dd/MM/yyyy"}
            name={`${name}.value`}
            // outputFormat={"YYYY-MM-DD"}
            // type={"date"}
          />
        </>
      );
      break;
    case "timedelta":
      keyComponent = null;
      cmpComponent = (
        <Field component={BootstrapField} name={`${name}.cmp`} type={"select"}>
          {dynamicDateCmp}
        </Field>
      );
      valueComponent = (
        <InputGroup>
          <Field
            component={BootstrapField}
            name={`${name}.value[0]`}
            type={"number"}
          />
          <InputGroupAddon addonType="append">
            <InputGroupText>days</InputGroupText>
          </InputGroupAddon>
        </InputGroup>
      );
      break;
    case "samplemeta":
      keyComponent = (
        <Field component={BootstrapField} name={`${name}.key`} type={"select"}>
          {sampleFields.map(field => {
            return (
              <option key={field} value={field}>
                {field}
              </option>
            );
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
          <Field component={BootstrapField} name={`${name}.value[0]`} />
        </>
      );
      break;
    case "reportmeta":
      keyComponent = (
        <Field component={BootstrapField} name={`${name}.key`} type={"select"}>
          {reportFields.map(field => {
            return (
              <option key={field} value={field}>
                {field}
              </option>
            );
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
          <Field component={BootstrapField} name={`${name}.value[0]`} />
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
      <td style={{ maxWidth: "35%" }}>
        <FormGroup>{keyComponent}</FormGroup>
      </td>
      <td>
        <InputGroup>{cmpComponent}</InputGroup>
      </td>
      <td>
        <FormGroup>{valueComponent}</FormGroup>
      </td>
      <td>
        <Button
          onClick={() => {
            innerArrayHelpers.remove(index);
          }}
          size={"sm"}
          color={"primary"}
        >
          <i className="fa fa-fw fa-trash" aria-hidden="true" />
          Delete
        </Button>
        {errorMsg && (
          <Button
            onClick={() => {
              toggle();
            }}
            id="errorPopover"
            size={"sm"}
            color={"error"}
          >
            Errors
          </Button>
        )}
      </td>
      {errorMsg && (
        <Popover
          placement="bottom"
          isOpen={popoverOpen}
          toggle={toggle}
          target="errorPopover"
        >
          <PopoverHeader>Row Errors</PopoverHeader>
          <PopoverBody>{errorMsg}</PopoverBody>
        </Popover>
      )}
    </>
  );
}

export default connect(FilterRow);
