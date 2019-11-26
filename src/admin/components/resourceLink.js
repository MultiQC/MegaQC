import {Button, Link} from "react-admin";
import {useForm, useField} from 'react-final-form';
import React from 'react';

/**
 *
 * @param reference The resource to link to
 * @param source The relationship key on the current resource which links to the
 * destination resource
 * @param dest The relationship key on the destination resource
 */
export default function ResourceLink({reference, source, dest, children}){
    // const form = useForm();
    // const localValue = form.getFieldState(source);
    const localValue = useField(source);
    const query = encodeURIComponent(JSON.stringify({
        [dest]: localValue.input.value
    }));
    return <Button
        component={Link}
        to={{
            pathname: `/${reference}/create`,
            search: `?defaults=${query}&source={}`
        }}
        label={`Add a ${reference}`}
    >
        {children}
    </Button>
};