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
    EmailField,
    BooleanField,
    BooleanInput
} from 'react-admin';


export const UserList = props => (
    <List {...props}>
        <Datagrid rowClick="show">
            <TextField source="id" />
            <TextField source="username" />
            <TextField source="first_name" />
            <TextField source="api_token" />
            <TextField source="last_name" />
            <EmailField source="email" />
            <BooleanField source="active" />
            <DateField source="created_at" />
            <TextField source="salt" />
            <TextField source="password" />
            <BooleanField source="admin" />
        </Datagrid>
    </List>
);

export const UserEdit = props => (
    <Edit {...props}>
        <SimpleForm>
            <TextInput source="id" />
            <TextInput source="username" />
            <TextInput source="first_name" />
            <TextInput source="api_token" />
            <TextInput source="last_name" />
            <TextInput source="email" />
            <BooleanInput source="active" />
            <DateInput source="created_at" />
            <TextInput source="salt" />
            <TextInput source="password" />
            <BooleanInput source="admin" />
        </SimpleForm>
    </Edit>
);

export const UserShow = props => (
    <Show {...props}>
        <SimpleShowLayout>
            <TextField source="id" />
            <TextField source="username" />
            <TextField source="first_name" />
            <TextField source="api_token" />
            <TextField source="last_name" />
            <EmailField source="email" />
            <BooleanField source="active" />
            <DateField source="created_at" />
            <TextField source="salt" />
            <TextField source="password" />
            <BooleanField source="admin" />
        </SimpleShowLayout>
    </Show>
);

