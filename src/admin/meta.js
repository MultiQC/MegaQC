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
    ReferenceInput,
    SelectInput,
    AutocompleteInput,
    Create
} from 'react-admin';

import DefaultForm from "./components/DefaultForm";

export const ReportMetaList = props => (
    <List {...props}>
        <Datagrid rowClick="show">
            <TextField source="id"/>
            <TextField source="key"/>
            <TextField source="value"/>
            <ReferenceField
                link="show"
                label="Report"
                source="report.id"
                reference="reports"
            >
                <TextField source="id"/>
            </ReferenceField>
        </Datagrid>
    </List>
);

export const ReportMetaShow = props => (
    <Show {...props}>
        <SimpleShowLayout>
            <TextField source="id"/>
            <TextField source="key"/>
            <TextField source="value"/>
            <ReferenceField
                link="show"
                label="Report"
                source="report.id"
                reference="reports"
            >
                <TextField source="id"/>
            </ReferenceField>
        </SimpleShowLayout>
    </Show>
);

export const ReportMetaEdit = props => (
    <Edit {...props}>
        <SimpleForm>
            <TextField source="id"/>
            <TextInput source="key"/>
            <TextInput source="value"/>
            <ReferenceInput
                filterToQuery={() => {}}
                label="Report"
                source="report.id"
                reference="reports"
            >
                <AutocompleteInput optionValue="id" optionText="hash"/>
            </ReferenceInput>
        </SimpleForm>
    </Edit>
);

export const ReportMetaCreate = props => (
    <Create {...props}>
        <DefaultForm location={props.location}>
            <TextInput source="key"/>
            <TextInput source="value"/>
            <ReferenceInput
                filterToQuery={() => {}}
                label="Report"
                source="report.id"
                reference="reports"
            >
                <AutocompleteInput optionValue="id" optionText="hash"/>
            </ReferenceInput>
        </DefaultForm>
    </Create>
);
