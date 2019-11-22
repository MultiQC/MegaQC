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
    TextInput,
    ReferenceField
} from 'react-admin';

export const DataList = props => (
    <List {...props}>
        <Datagrid rowClick="show">
            <TextField source="id" />
            <TextField source="value" />
            <EditButton/>
            <ShowButton/>
        </Datagrid>
    </List>
);

export const DataShow = props => (
    <Show {...props}>
        <SimpleShowLayout>
            <TextField source="id" />
            <TextField source="value" />
            <ReferenceField label="Type" source="relationships.data_type.id" reference="data_types">
                <TextField source="key"/>
            </ReferenceField>
        </SimpleShowLayout>
    </Show>
);

export const DataEdit = props => (
    <Edit {...props}>
        <SimpleForm>
            <TextInput source="id"/>
            <TextInput source="value"/>
        </SimpleForm>
    </Edit>
);