import React from "react";
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
  TextInput,
  ReferenceField,
  EditButton,
  ShowButton,
  BooleanField,
  DeleteButton,
  BooleanInput,
} from "react-admin";
import { JsonInput, JsonField } from "./components/jsonField";

export const FilterList = (props) => (
  <List {...props}>
    <Datagrid rowClick="show">
      <TextField source="id" />
      <TextField source="name" />
      <TextField source="tag" />
      <BooleanField source="public" />
      <ReferenceField
        link="show"
        label="Owner"
        source="user.id"
        reference="users"
      >
        <TextField source="username" />
      </ReferenceField>
      <TextField source="data" />
      <EditButton />
      <ShowButton />
      <DeleteButton />
    </Datagrid>
  </List>
);

export const FilterShow = (props) => (
  <Show {...props}>
    <SimpleShowLayout>
      <TextField source="id" />
      <TextField source="name" />
      <TextField source="tag" />
      <BooleanField source="public" />
      <ReferenceField
        link="show"
        label="Owner"
        source="user.id"
        reference="users"
      >
        <TextField source="username" />
      </ReferenceField>
      <TextField source="data" />
    </SimpleShowLayout>
  </Show>
);

export const FilterEdit = (props) => (
  <Edit {...props}>
    <SimpleForm redirect="show">
      <TextInput source="id" />
      <TextInput source="name" />
      <TextInput source="tag" />
      <BooleanInput source="public" />
      <ReferenceField
        link="show"
        label="Owner"
        source="user.id"
        reference="users"
      >
        <TextField source="username" />
      </ReferenceField>
      <JsonInput source="data" />
    </SimpleForm>
  </Edit>
);
