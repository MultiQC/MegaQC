import React from 'react';
import {
    AutocompleteInput,
    Datagrid,
    Edit,
    EditButton,
    List,
    Pagination,
    ReferenceField,
    ReferenceInput,
    ReferenceManyField,
    Show,
    ShowButton,
    SimpleForm,
    SimpleShowLayout,
    TextField,
    TextInput
} from 'react-admin';

import ResourceLink from './components/resourceLink'

export const SampleList = props => (
    <List {...props}>
        <Datagrid rowClick="show">
            <TextField source="id"/>
            <TextField source="name"/>
            <ReferenceField
                link="show"
                label="Report"
                source="report.id"
                reference="reports"
            >
                <TextField source="hash"/>
            </ReferenceField>
            <EditButton/>
            <ShowButton/>
        </Datagrid>
    </List>
);

export const SampleShow = props => {
    return (
        <Show {...props}>
            <SimpleShowLayout>
                <TextField source="id"/>
                <TextField source="name"/>
                <ReferenceField
                    link="show"
                    label="Report"
                    source="report.id"
                    reference="reports"
                >
                    <TextField source="hash"/>
                </ReferenceField>
                <ReferenceManyField
                    label="Data"
                    reference="sample_data"
                    target="sample"
                    pagination={<Pagination/>}
                >
                    <Datagrid rowClick="show">
                        <TextField source="id"/>
                        <TextField source="value"/>
                        <ReferenceField
                            link="show"
                            label="Type"
                            source="data_type.id"
                            reference="data_types"
                        >
                            <TextField source="key"/>
                        </ReferenceField>
                        <EditButton/>
                        <ShowButton/>
                    </Datagrid>
                </ReferenceManyField>
            </SimpleShowLayout>
        </Show>
    );
};

export const SampleEdit = props => (
    <Edit {...props}>
        <SimpleForm>
            <TextInput source="id"/>
            <TextInput source="name"/>
            <ReferenceInput
                filterToQuery={() => {}}
                label="Report"
                source="report.id"
                reference="reports"
            >
                <AutocompleteInput optionValue="id" optionText="hash"/>
            </ReferenceInput>
            <ReferenceManyField label="Data" reference="sample_data" target="sample">
                <Datagrid rowClick="show">
                    <TextField source="id"/>
                    <TextField source="value"/>
                    <ReferenceField
                        link="show"
                        label="Type"
                        source="data_type.id"
                        reference="data_types"
                    >
                        <TextField source="key"/>
                    </ReferenceField>
                    <EditButton/>
                    <ShowButton/>
                </Datagrid>
            </ReferenceManyField>
            <ResourceLink
                reference="sample_data"
                source="id"
                dest="sample.id"
            />
        </SimpleForm>
    </Edit>
);
