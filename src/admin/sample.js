import React from 'react';
import {
    Datagrid,
    Edit,
    EditButton,
    List,
    Show,
    ShowButton,
    SimpleForm,
    SimpleShowLayout,
    TextField,
    TextInput
} from 'react-admin';

export const SampleList = props => (
    <List {...props}>
    <Datagrid rowClick="edit">
    <TextField source="id" />
    <TextField source="name" />
    <EditButton/>
    <ShowButton/>
    </Datagrid>
    </List>
);

export const SampleShow = props => (
    <Show {...props}>
        <SimpleShowLayout>
            <TextField source="id" />
            <TextField source="name" />
        </SimpleShowLayout>
    </Show>
);

export const SampleEdit = props => (
    <Edit {...props}>
        <SimpleForm>
            <TextInput source="id" />
            <TextInput source="name" />
        </SimpleForm>
    </Edit>
);