import React from 'react';
import {Input} from 'reactstrap';

export default function BootstrapField(props) {
    const {field, form, ...rest} = props;
    return <Input {...field} {...rest}/>
}