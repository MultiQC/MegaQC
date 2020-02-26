import React from 'react';
import {Input, FormFeedback} from 'reactstrap';
import {ErrorMessage, getIn} from 'formik';

/**
 * For use with Formik's Field
 */
export default function BootstrapField(props) {
    const {field, form, type, ...rest} = props;
    const touched = getIn(form.touched, field.name);
    const errors = getIn(form.errors, field.name);
    const invalid = touched && errors;
    const valid = touched && !errors;

    return <>
        <Input valid={valid} invalid={invalid} type={type} {...field} {...rest}/>
        <ErrorMessage name={field.name}>
            {msg => <FormFeedback valid={!invalid}>{msg}</FormFeedback>}
        </ErrorMessage>
    </>
}