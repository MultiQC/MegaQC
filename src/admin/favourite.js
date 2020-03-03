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
  TextInput
} from "react-admin";
import { JsonInput, JsonField } from "./components/jsonField";

export const FavouriteList = props => (
  <List {...props}>
    <Datagrid rowClick="show">
      <TextField source="id" />
      <TextField source="title" />
      <TextField source="description" />
      <TextField source="plot_type" />
      <DateField source="created_at" />
    </Datagrid>
  </List>
);

export const FavouriteShow = props => (
  <Show {...props}>
    <SimpleShowLayout>
      <TextField source="id" />
      <TextField source="title" />
      <TextField source="description" />
      <TextField source="plot_type" />
      <DateField source="created_at" />
      <JsonField source="data" />
    </SimpleShowLayout>
  </Show>
);

export const FavouriteEdit = props => (
  <Edit {...props}>
    <SimpleForm redirect="show">
      <TextInput source="id" />
      <TextInput source="title" />
      <TextInput source="description" />
      <TextInput source="plot_type" />
      <DateInput source="created_at" />
      <JsonInput source="data" />
    </SimpleForm>
  </Edit>
);
