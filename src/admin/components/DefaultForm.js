// A copy of SimpleForm, but loads default form values from the query string
import React from 'react';
import {SimpleForm} from 'react-admin';
import {parse} from "query-string";
import set from 'lodash/set';

export default function DefaultForm(props) {
    const search = parse(props.location.search);
    const parsed = JSON.parse(search.defaults);
    const defaults = {};
    for (let key of Object.keys(parsed)){
        set(defaults, key, parsed[key]);
    }
    return <SimpleForm initialValues={defaults} {...props}/>
}