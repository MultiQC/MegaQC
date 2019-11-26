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
    BooleanField,
    BooleanInput
} from 'react-admin';
import {Field} from 'react-final-form';
import {renderJsonField} from './components/jsonField'

export const DashboardList = props => (
    <List {...props}>
        <Datagrid rowClick="show">
            <TextField source="id"/>
            <TextField source="title"/>
            <DateField source="created_at"/>
            <DateField source="modified_at"/>
            <BooleanField source="is_public"/>
        </Datagrid>
    </List>
);

export const DashboardShow = props => (
    <Show {...props}>
        <SimpleShowLayout>
            <TextField source="id"/>
            <TextField source="title"/>
            <DateField source="created_at"/>
            <DateField source="modified_at"/>
            <BooleanField source="is_public"/>
            <Field component={renderJsonField} name="data" label="Data"/>
        </SimpleShowLayout>
    </Show>
);

export const DashboardEdit = props => (
    <Edit {...props}>
        <SimpleForm>
            <TextInput source="id"/>
            <TextInput source="title"/>
            <DateInput source="created_at"/>
            <DateInput source="modified_at"/>
            <BooleanInput source="is_public"/>
            <Field component={renderJsonField} name="data" label="Data"/>
        </SimpleForm>
    </Edit>
);
