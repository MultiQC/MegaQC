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
    ReferenceField,
    ReferenceManyField,
} from 'react-admin';

export const ReportList = props => (
    <List {...props}>
        <Datagrid rowClick="show">
            <TextField source="id"/>
            <DateField source="uploaded_at"/>
            <DateField source="created_at"/>
            <TextField source="hash"/>
            <EditButton/>
            <ShowButton/>
        </Datagrid>
    </List>
);

export const ReportEdit = props => (
    <Edit {...props}>
        <SimpleForm>
            <TextInput source="id"/>
            <DateInput source="uploaded_at"/>
            <TextInput source="hash"/>
            <DateInput source="created_at"/>
            <ReferenceField link="show" label="Owner" source="relationships.user.id" reference="users">
                <TextField source="username"/>
            </ReferenceField>
        </SimpleForm>
    </Edit>
);

export const ReportShow = props => (
    <Show {...props}>
        <SimpleShowLayout>
            <TextField source="id"/>
            <DateField source="uploaded_at"/>
            <TextField source="hash"/>
            <DateField source="created_at"/>
            <ReferenceField link="show" label="Owner" source="relationships.user.id" reference="users">
                <TextField source="username"/>
            </ReferenceField>
             <ReferenceManyField label="Samples" reference="samples" target="report">
                <Datagrid rowClick="show">
                    <TextField source="id"/>
                    <TextField source="name"/>
                </Datagrid>
            </ReferenceManyField>
        </SimpleShowLayout>
    </Show>
);
