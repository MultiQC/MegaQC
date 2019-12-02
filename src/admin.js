import ReactDOM from 'react-dom';
import React, {useEffect, useRef, useState} from 'react';
import {Admin, Resource, EditGuesser, ListGuesser, ShowGuesser} from 'react-admin';
import jsonapiClient from "ra-jsonapi-client";
import {ReportEdit, ReportList, ReportShow} from "./admin/report";
import {SampleEdit, SampleList, SampleShow} from "./admin/sample";
import {UploadEdit, UploadList, UploadShow} from "./admin/upload";
import {ReportMetaList} from "./admin/meta";
import {FilterGroupList} from "./admin/filterGroup";
import {DataTypeList, DataTypeEdit, DataTypeShow} from "./admin/dataType";
import {FavouriteList, FavouriteEdit, FavouriteShow} from "./admin/favourite";
import {DashboardList, DashboardEdit, DashboardShow} from "./admin/dashboards";
import {DataList, DataEdit, DataShow, DataCreate} from "./admin/sampleData";
import {UserList, UserEdit, UserShow} from "./admin/user";
import {getClient, getToken} from './util/api';

/**
 * Constructs a JSON API Serializer options object for the list of provided relationships
 */
function relationships(rels){
    const ret = {
        keyForAttribute: attr => attr
    };
    for (let rel of rels){
        ret[rel] = {
            ref: (outer, inner) => inner.id,
        }
    }
    return ret
}

function App() {
    // Start with a client that has no auth, but immediately request an auth token
    const [token, setToken] = useState(null);

    const provider = jsonapiClient('/rest_api/v1', {
        total: 'count',
        arrayFormat: 'comma',
        serializerOpts: {
            sample_data: relationships(['report', 'sample', 'data_type'])
        },
        deserializerOpts: {
            keyForAttribute: attr => attr
        },
        headers: {
            access_token: token,
            Accept: 'application/vnd.api+json'
        }
    });

    useEffect(() => {
        const client = getClient();
        getToken(client).then(token => {
            setToken(token);
        })
    }, []);

    if (token === null)
        return null;
    else
        return (
            <Admin dataProvider={provider}>
                <Resource name="reports" list={ReportList} show={ReportShow} edit={ReportEdit}/>
                <Resource name="samples" list={SampleList} show={SampleShow} edit={SampleEdit}/>
                <Resource name="uploads" list={UploadList} show={UploadShow} edit={UploadEdit}/>
                <Resource name="report_meta" list={ReportMetaList}/>
                <Resource name="data_types" list={DataTypeList} show={DataTypeShow} edit={DataTypeEdit}/>
                <Resource name="users" list={UserList} show={UserShow} edit={UserEdit}/>
                <Resource name="filter_groups" list={FilterGroupList}/>
                <Resource name="favourites" list={FavouriteList} show={FavouriteShow} edit={FavouriteEdit}/>
                <Resource name="dashboards" list={DashboardList} show={DashboardShow} edit={DashboardEdit}/>
                <Resource name="sample_data" create={DataCreate} list={DataList} show={DataShow} edit={DataEdit}/>
            </Admin>
        );
}

ReactDOM.render(
    <App/>,
    document.getElementById('react')
);

