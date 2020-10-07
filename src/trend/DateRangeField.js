import React from "react";
import { Input, FormFeedback } from "reactstrap";
import { ErrorMessage, getIn } from "formik";
import { format, parse } from "date-fns";
import DatePicker from "react-datepicker";
import { DATE_FORMAT } from "../util/filter";

import "react-datepicker/dist/react-datepicker.css";

export default function DateRangeField(props) {
  const { field, form, type, outputFormat, ...rest } = props;
  const touched = getIn(form.touched, field.name);
  const errors = getIn(form.errors, field.name);
  const invalid = touched && errors;
  const valid = touched && !errors;

  // We're storing the date in the form in this format, so we have to parse it out first
  const [startDate, endDate] = field.value.map((d) => {
    const parsed = parse(d, DATE_FORMAT, new Date());
    if (isNaN(parsed)) return new Date();
    else return parsed;
  });

  // // Fail if either date is invalid
  // for (let date of [startDate, endDate]){
  //     if (!date || isNaN(date))
  //         return null;
  // }

  return (
    <div
      className="d-inline-flex"
      style={{
        alignItems: "center",
      }}
    >
      <DatePicker
        selected={startDate}
        onChange={(date) =>
          form.setFieldValue(`${field.name}.0`, format(date, DATE_FORMAT), true)
        }
        selectsStart
        startDate={startDate}
        endDate={endDate}
        customInput={<Input />}
        {...rest}
      />
      &nbsp;to&nbsp;
      <DatePicker
        selected={endDate}
        onChange={(date) =>
          form.setFieldValue(`${field.name}.1`, format(date, DATE_FORMAT), true)
        }
        selectsEnd
        startDate={startDate}
        endDate={endDate}
        minDate={startDate}
        customInput={<Input />}
        {...rest}
      />
      {/*<MuiPickersUtilsProvider utils={MomentUtils}>*/}
      {/*  <KeyboardDatePicker*/}
      {/*    onError={error => {*/}
      {/*        if (errors !== error) {*/}
      {/*            form.setFieldError(field.name, error);*/}
      {/*        }*/}
      {/*    }}*/}
      {/*    valid={valid}*/}
      {/*    invalid={invalid}*/}
      {/*    {...field}*/}
      {/*    {...rest}*/}
      {/*    onChange={date => {*/}
      {/*      // Then, when the date is changed, we need to output in that same format*/}
      {/*      form.setFieldValue(field.name, date.format(outputFormat), true);*/}
      {/*    }}*/}
      {/*    value={value}*/}
      {/*  />*/}
      {/*</MuiPickersUtilsProvider>*/}
      <ErrorMessage name={field.name}>
        {(msg) => <FormFeedback valid={!invalid}>{msg}</FormFeedback>}
      </ErrorMessage>
    </div>
  );
}
