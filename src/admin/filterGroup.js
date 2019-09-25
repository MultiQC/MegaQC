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
    TextInput
} from 'react-admin';

export const FilterGroupList = props => (
    <List {...props}>
        <Datagrid rowClick="edit">
            <TextField source="id" />
        </Datagrid>
    </List>
);
