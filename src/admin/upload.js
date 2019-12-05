import React from 'react';
import {
    Datagrid,
    DateField,
    DateInput,
    Edit,
    List,
    Show,
    SimpleForm,
    SimpleShowLayout,
    TextField,
    TextInput
} from 'react-admin';


export const UploadList = props => (
    <List {...props}>
        <Datagrid rowClick="show">
            <TextField source="id"/>
            <TextField source="message"/>
            <TextField source="path"/>
            <DateField source="created_at"/>
            <DateField source="modified_at"/>
            <TextField source="status"/>
        </Datagrid>
    </List>
);

export const UploadShow = props => (
    <Show {...props}>
        <SimpleShowLayout>
            <TextField source="id"/>
            <TextField source="message"/>
            <TextField source="path"/>
            <DateField source="created_at"/>
            <DateField source="modified_at"/>
            <TextField source="status"/>
        </SimpleShowLayout>
    </Show>
);

export const UploadEdit = props => (
    <Edit {...props}>
        <SimpleForm>
            <TextField source="id"/>
            <TextInput source="message"/>
            <TextInput source="path"/>
            <DateInput source="created_at"/>
            <DateInput source="modified_at"/>
            <TextInput source="status"/>
        </SimpleForm>
    </Edit>
);
