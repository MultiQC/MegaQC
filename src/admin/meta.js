import React from "react";
import {
  AutocompleteInput,
  Create,
  Datagrid,
  Edit,
  List,
  ReferenceField,
  ReferenceInput,
  Show,
  SimpleForm,
  SimpleShowLayout,
  TextField,
  TextInput
} from "react-admin";

import DefaultForm from "./components/defaultForm";

export const ReportMetaList = props => (
  <List {...props}>
    <Datagrid rowClick="show">
      <TextField source="id" />
      <TextField source="key" />
      <TextField source="value" />
      <ReferenceField
        link="show"
        label="Report"
        source="report.id"
        reference="reports"
      >
        <TextField source="id" />
      </ReferenceField>
    </Datagrid>
  </List>
);

export const ReportMetaShow = props => (
  <Show {...props}>
    <SimpleShowLayout>
      <TextField source="id" />
      <TextField source="key" />
      <TextField source="value" />
      <ReferenceField
        link="show"
        label="Report"
        source="report.id"
        reference="reports"
      >
        <TextField source="id" />
      </ReferenceField>
    </SimpleShowLayout>
  </Show>
);

export const ReportMetaEdit = props => (
  <Edit {...props}>
    <SimpleForm redirect="show">
      <TextField source="id" />
      <TextInput source="key" />
      <TextInput source="value" />
      <ReferenceInput
        filterToQuery={() => {}}
        label="Report"
        source="report.id"
        reference="reports"
      >
        <AutocompleteInput optionValue="id" optionText="hash" />
      </ReferenceInput>
    </SimpleForm>
  </Edit>
);

export const ReportMetaCreate = props => (
  <Create {...props}>
    <DefaultForm location={props.location} redirect="show">
      <TextInput source="key" />
      <TextInput source="value" />
      <ReferenceInput
        filterToQuery={() => {}}
        label="Report"
        source="report.id"
        reference="reports"
      >
        <AutocompleteInput optionValue="id" optionText="hash" />
      </ReferenceInput>
    </DefaultForm>
  </Create>
);
