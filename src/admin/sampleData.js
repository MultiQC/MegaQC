import React from "react";
import {
  Create,
  Datagrid,
  Edit,
  EditButton,
  List,
  ReferenceField,
  ReferenceInput,
  SelectInput,
  Show,
  ShowButton,
  SimpleForm,
  SimpleShowLayout,
  TextField,
  TextInput
} from "react-admin";
import DefaultForm from "./components/defaultForm";

export const DataList = props => (
  <List {...props}>
    <Datagrid rowClick="show">
      <TextField source="id" />
      <TextField source="value" />
      <ReferenceField
        link="show"
        label="Type"
        source="data_type.id"
        reference="data_types"
      >
        <TextField source="key" />
      </ReferenceField>
      <ReferenceField
        link="show"
        label="Sample"
        source="sample.id"
        reference="samples"
      >
        <TextField source="name" />
      </ReferenceField>
      <EditButton />
      <ShowButton />
    </Datagrid>
  </List>
);

export const DataShow = props => (
  <Show {...props}>
    <SimpleShowLayout>
      <TextField source="id" />
      <TextField source="value" />
      <ReferenceField
        link="show"
        label="Type"
        source="data_type.id"
        reference="data_types"
      >
        <TextField source="key" />
      </ReferenceField>
      <ReferenceField
        link="show"
        label="Sample"
        source="sample.id"
        reference="samples"
      >
        <TextField source="name" />
      </ReferenceField>
    </SimpleShowLayout>
  </Show>
);

export const DataEdit = props => (
  <Edit {...props}>
    <SimpleForm redirect="show">
      <TextInput source="id" />
      <TextInput source="value" />
      <ReferenceInput
        filterToQuery={() => {}}
        label="Type"
        source="data_type.id"
        reference="data_types"
      >
        <SelectInput optionValue="id" optionText="key" />
      </ReferenceInput>
      <ReferenceInput
        filterToQuery={() => {}}
        label="Sample"
        source="sample.id"
        reference="samples"
      >
        <SelectInput optionValue="id" optionText="name" />
      </ReferenceInput>
    </SimpleForm>
  </Edit>
);

export const DataCreate = props => (
  <Create {...props}>
    <DefaultForm location={props.location} redirect="show">
      <TextInput source="value" />
      <ReferenceInput
        filterToQuery={() => {}}
        label="Type"
        source="data_type.id"
        reference="data_types"
      >
        <SelectInput optionValue="id" optionText="key" />
      </ReferenceInput>
      <ReferenceInput
        filterToQuery={() => {}}
        label="Sample"
        source="sample.id"
        reference="samples"
      >
        <SelectInput optionValue="id" optionText="name" />
      </ReferenceInput>
    </DefaultForm>
  </Create>
);
