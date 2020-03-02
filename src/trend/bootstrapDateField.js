import React from 'react';
import {Input, FormFeedback} from 'reactstrap';
import {ErrorMessage, getIn} from 'formik';
import MomentUtils from '@date-io/moment';
import Moment from 'moment';
import {
    KeyboardDatePicker,
    MuiPickersUtilsProvider
} from "@material-ui/pickers";

export default function BootstrapDateField(props) {
    const {field, form, type, outputFormat, ...rest} = props;
    const touched = getIn(form.touched, field.name);
    const errors = getIn(form.errors, field.name);
    const invalid = touched && errors;
    const valid = touched && !errors;

    // We're storing the date in the form in this format, so we have to parse it out first
    const value = Moment(field.value, outputFormat);

    return <>
        <MuiPickersUtilsProvider utils={MomentUtils}>
            <KeyboardDatePicker
                onError={error => {
                    form.setFieldError(field.name, error);
                }}
                valid={valid}
                invalid={invalid}
                {...field}
                {...rest}
                onChange={date => {
                    // Then, when the date is changed, we need to output in that same format
                    form.setFieldValue(field.name, date.format(outputFormat), true);
                }}
                value={value}
            />
        </MuiPickersUtilsProvider>
        <ErrorMessage name={field.name}>
            {msg => <FormFeedback valid={!invalid}>{msg}</FormFeedback>}
        </ErrorMessage>
    </>
}