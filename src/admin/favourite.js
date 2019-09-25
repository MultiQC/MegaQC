import React from 'react';
import {
    Datagrid,
    DateField,
    DateInput,
    Edit,
    EditButton,
    List,
    Show,
    ShowButton,
    SimpleForm,
    SimpleShowLayout,
    TextField,
    TextInput,
} from 'react-admin';
import {Field} from 'redux-form';
import {renderJsonField} from './jsonField'

export const FavouriteList = props => (
    <List {...props}>
        <Datagrid rowClick="edit">
            <TextField source="id"/>
            <TextField source="title"/>
            <TextField source="description"/>
            <TextField source="plot_type"/>
            <DateField source="created_at"/>
        </Datagrid>
    </List>
);

export const FavouriteShow = props => (
    <Show {...props}>
        <SimpleShowLayout>
            <TextField source="id"/>
            <TextField source="title"/>
            <TextField source="description"/>
            <TextField source="plot_type"/>
            <DateField source="created_at"/>
            <Field component={renderJsonField} name="data" label="Data"/>
        </SimpleShowLayout>
    </Show>
);

export const FavouriteEdit = props => (
    <Edit {...props}>
        <SimpleForm>
            <TextInput source="id"/>
            <TextInput source="title"/>
            <TextInput source="description"/>
            <TextInput source="plot_type"/>
            <DateInput source="created_at"/>
            <Field component={renderJsonField} name="data" label="Data"/>
        </SimpleForm>
    </Edit>
);

