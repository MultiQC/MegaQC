import React from 'react';
import {Datagrid, List, TextField} from 'react-admin';

export const FilterGroupList = props => (
    <List {...props}>
        <Datagrid rowClick="show">
            <TextField source="id" />
        </Datagrid>
    </List>
);
