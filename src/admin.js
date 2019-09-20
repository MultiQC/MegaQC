import ReactDOM from 'react-dom';
import React, {useState, useEffect} from 'react';
import {Admin, Resource} from 'react-admin';
import jsonapiClient from "ra-jsonapi-client";
import {
    List,
    Datagrid,
    Edit,
    Create,
    SimpleForm,
    DateField,
    TextField,
    EditButton,
    ShowButton,
    DisabledInput,
    TextInput,
    LongTextInput,
    DateInput,
    ListGuesser,
    ShowGuesser,
    EditGuesser,
    ReferenceField,
    ReferenceManyField,
    SingleFieldList,
    ChipField
} from 'react-admin';

const dataProvider = jsonapiClient('/rest_api/v1', {total: null});

const ReportList = props => (
    <List {...props}>
        <Datagrid rowClick="edit">
            <TextField source="id" />
            <DateField source="uploaded_at" />
            <DateField source="created_at" />
            <TextField source="hash" />
            <EditButton/>
            <ShowButton/>
        </Datagrid>
    </List>
);

export const SampleList = props => (
    <List {...props}>
        <Datagrid rowClick="edit">
            <TextField source="id" />
            <TextField source="name" />
             <ReferenceField label="Report" source="report_id" reference="reports">
                <TextField source="id" />
            </ReferenceField>
            <EditButton/>
            <ShowButton/>
        </Datagrid>
    </List>
);

const App = () => (
    <Admin dataProvider={dataProvider}>
        <Resource name="reports" list={ReportList} show={ShowGuesser} edit={EditGuesser}/>
        <Resource name="samples" list={SampleList} show={ShowGuesser} edit={EditGuesser}/>
    </Admin>
);

ReactDOM.render(
    <App/>,
    document.getElementById('react')
);

