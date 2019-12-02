import React from 'react';
import {
    Button,
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
    ReferenceManyField,
    ReferenceField,
    ReferenceInput,
    ReferenceArrayInput,
    SelectInput,
    AutocompleteInput,
    AutocompleteArrayInput,
    Link
} from 'react-admin';

import ResourceLink from './components/resourceLink'
import DefaultForm from "./components/DefaultForm";

export const SampleList = props => (
    <List {...props}>
        <Datagrid rowClick="show">
            <TextField source="id"/>
            <TextField source="name"/>
            <ReferenceField link="show" label="Report" source="relationships.report.id"
                            reference="reports">
                <TextField source="id"/>
            </ReferenceField>
            <EditButton/>
            <ShowButton/>
        </Datagrid>
    </List>
);

export const SampleShow = props => (
    <Show {...props}>
        <SimpleShowLayout>
            <TextField source="id"/>
            <TextField source="name"/>
            <ReferenceField link="show" label="Report" source="relationships.report.id"
                            reference="reports">
                <TextField source="id"/>
            </ReferenceField>
            <ReferenceManyField label="Data" reference="sample_data" target="sample">
                <List
                    location={props.location}
                    hasCreate={false}
                    hasEdit={false}
                    hasList={false}
                    hasShow={false}
                    resource="sample_data"
                >
                    <Datagrid rowClick="show">
                        <TextField source="id"/>
                        <TextField source="value"/>
                        <ReferenceField link="show" label="Type"
                                        source="relationships.data_type.id"
                                        reference="data_types">
                            <TextField source="key"/>
                        </ReferenceField>
                        <EditButton/>
                        <ShowButton/>
                    </Datagrid>
                </List>
            </ReferenceManyField>
        </SimpleShowLayout>
    </Show>
);

export const SampleEdit = props => (
    <Edit {...props}>
        <SimpleForm>
            <TextInput source="id"/>
            <TextInput source="name"/>
            <ReferenceInput
                filterToQuery={() => {
                }}
                label="Report"
                source="relationships.report.id"
                reference="reports"
            >
                <AutocompleteInput optionValue="id" optionText="id"/>
            </ReferenceInput>
            <ReferenceManyField label="Data" reference="sample_data" target="sample">
                <Datagrid rowClick="show">
                    <TextField source="id"/>
                    <TextField source="value"/>
                    <ReferenceField link="show" label="Type"
                                    source="relationships.data_type.id"
                                    reference="data_types">
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
            {/*<ReferenceArrayInput*/}
            {/*    filterToQuery={() => {}}*/}
            {/*    label="Data"*/}
            {/*    target="sample"*/}
            {/*    reference="sample_data"*/}
            {/*>*/}
            {/*    <AutocompleteArrayInput*/}
            {/*    optionValue=""*/}
            {/*    />*/}
            {/*</ReferenceArrayInput>*/}
        </SimpleForm>
    </Edit>
);