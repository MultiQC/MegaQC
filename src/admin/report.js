import React from "react";
import {
  Datagrid,
  DateField,
  DateInput,
  Edit,
  EditButton,
  List,
  ReferenceField,
  ReferenceManyField,
  Show,
  ShowButton,
  SimpleForm,
  SimpleShowLayout,
  TextField,
  TextInput,
  DeleteButton,
} from "react-admin";
import ResourceLink from "./components/resourceLink";

export const ReportList = (props) => (
  <List {...props}>
    <Datagrid rowClick="show">
      <TextField source="id" />
      <DateField source="uploaded_at" />
      <DateField source="created_at" />
      <TextField source="hash" />
      <ReferenceField
        link="show"
        label="Owner"
        source="user.id"
        reference="users"
      >
        <TextField source="username" />
      </ReferenceField>
      <EditButton />
      <ShowButton />
      <DeleteButton />
    </Datagrid>
  </List>
);

export const ReportEdit = (props) => (
  <Edit {...props}>
    <SimpleForm redirect="show">
      <TextInput source="id" />
      <DateInput source="uploaded_at" />
      <TextInput source="hash" />
      <DateInput source="created_at" />
      <ReferenceField
        link="show"
        label="Owner"
        source="user.id"
        reference="users"
      >
        <TextField source="username" />
      </ReferenceField>
      <ReferenceManyField label="Samples" reference="samples" target="report">
        <Datagrid rowClick="show">
          <TextField source="id" />
          <TextField source="name" />
        </Datagrid>
      </ReferenceManyField>
      <ReferenceManyField
        label="Metadata"
        reference="report_meta"
        target="report"
      >
        <Datagrid rowClick="show">
          <TextField source="id" />
          <TextField source="key" />
          <TextField source="value" />
        </Datagrid>
      </ReferenceManyField>
      <ResourceLink reference="report_meta" source="id" dest="report.id" />
    </SimpleForm>
  </Edit>
);

export const ReportShow = (props) => (
  <Show {...props}>
    <SimpleShowLayout>
      <TextField source="id" />
      <DateField source="uploaded_at" />
      <TextField source="hash" />
      <DateField source="created_at" />
      <ReferenceField
        link="show"
        label="Owner"
        source="user.id"
        reference="users"
      >
        <TextField source="username" />
      </ReferenceField>
      <ReferenceManyField label="Samples" reference="samples" target="report">
        <Datagrid rowClick="show">
          <TextField source="id" />
          <TextField source="name" />
        </Datagrid>
      </ReferenceManyField>
      <ReferenceManyField
        label="Metadata"
        reference="report_meta"
        target="report"
      >
        <Datagrid rowClick="show">
          <TextField source="id" />
          <TextField source="key" />
          <TextField source="value" />
        </Datagrid>
      </ReferenceManyField>
    </SimpleShowLayout>
  </Show>
);
