import React from "react";
import {
  Datagrid,
  List,
  TextField,
  EditButton,
  ShowButton,
  DeleteButton,
} from "react-admin";

export const FilterGroupList = (props) => (
  <List {...props}>
    <Datagrid rowClick="show">
      <TextField source="id" />
      <EditButton />
      <ShowButton />
      <DeleteButton />
    </Datagrid>
  </List>
);
