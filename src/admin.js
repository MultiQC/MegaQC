import ReactDOM from "react-dom";
import React, { useEffect, useRef, useState } from "react";
import { Admin, Resource } from "react-admin";
import jsonapiClient from "ra-jsonapi-client";
import { ReportEdit, ReportList, ReportShow } from "./admin/report";
import { SampleEdit, SampleList, SampleShow } from "./admin/sample";
import { UploadEdit, UploadList, UploadShow } from "./admin/upload";
import {
  ReportMetaList,
  ReportMetaShow,
  ReportMetaEdit,
  ReportMetaCreate,
} from "./admin/meta";
import { FilterGroupList } from "./admin/filterGroup";
import {
  DataTypeList,
  DataTypeEdit,
  DataTypeShow,
  DataTypeCreate,
} from "./admin/dataType";
import { FavouriteList, FavouriteEdit, FavouriteShow } from "./admin/favourite";
import {
  DashboardList,
  DashboardEdit,
  DashboardShow,
} from "./admin/dashboards";
import { DataList, DataEdit, DataShow, DataCreate } from "./admin/sampleData";
import { UserList, UserEdit, UserShow } from "./admin/user";
import { getClient, getToken } from "./util/api";

import { MegaQcLayout } from "./admin/components/layout";

/**
 * Constructs a JSON API Serializer options object for the list of provided relationships
 */
function relationships(rels = []) {
  const ret = {
    keyForAttribute: (attr) => attr,
  };
  for (let rel of rels) {
    ret[rel] = {
      ref: (outer, inner) => inner.id,
    };
  }
  return ret;
}

function App() {
  // Start with a client that has no auth, but immediately request an auth token
  const [token, setToken] = useState(null);

  const provider = jsonapiClient("/rest_api/v1", {
    total: "count",
    arrayFormat: "comma",
    serializerOpts: {
      sample_data: relationships(["report", "sample", "data_type"]),
      samples: relationships(["report", "data", "data_type"]),
      filters: relationships(["user"]),
      filter_groups: relationships(),
      reports: relationships(["meta", "samples", "user"]),
      uploads: relationships(["user"]),
      report_meta: relationships(["report"]),
      favourites: relationships(["user"]),
      dashboards: relationships(["user"]),
      report_meta_types: relationships(),
      users: relationships(["reports"]),
    },
    deserializerOpts: {
      sample_data: { keyForAttribute: (attr) => attr },
      samples: { keyForAttribute: (attr) => attr },
      filters: { keyForAttribute: (attr) => attr },
      filter_groups: { keyForAttribute: (attr) => attr },
      reports: { keyForAttribute: (attr) => attr },
      uploads: { keyForAttribute: (attr) => attr },
      report_meta: { keyForAttribute: (attr) => attr },
      favourites: { keyForAttribute: (attr) => attr },
      dashboards: { keyForAttribute: (attr) => attr },
      report_meta_types: { keyForAttribute: (attr) => attr },
      users: { keyForAttribute: (attr) => attr },
    },
    headers: {
      access_token: token,
      Accept: "application/vnd.api+json",
    },
  });

  useEffect(() => {
    const client = getClient();
    getToken(client).then((token) => {
      setToken(token);
    });
  }, []);

  if (token === null) return null;
  else
    return (
      <Admin layout={MegaQcLayout} dataProvider={provider}>
        <Resource
          name="reports"
          list={ReportList}
          show={ReportShow}
          edit={ReportEdit}
        />
        <Resource
          name="samples"
          list={SampleList}
          show={SampleShow}
          edit={SampleEdit}
        />
        <Resource
          name="uploads"
          list={UploadList}
          show={UploadShow}
          edit={UploadEdit}
        />
        <Resource
          name="report_meta"
          list={ReportMetaList}
          show={ReportMetaShow}
          edit={ReportMetaEdit}
          create={ReportMetaCreate}
        />
        <Resource
          name="data_types"
          list={DataTypeList}
          show={DataTypeShow}
          edit={DataTypeEdit}
          create={DataTypeCreate}
        />
        <Resource
          name="users"
          list={UserList}
          show={UserShow}
          edit={UserEdit}
        />
        <Resource name="filter_groups" list={FilterGroupList} />
        <Resource
          name="favourites"
          list={FavouriteList}
          show={FavouriteShow}
          edit={FavouriteEdit}
        />
        <Resource
          name="dashboards"
          list={DashboardList}
          show={DashboardShow}
          edit={DashboardEdit}
        />
        <Resource
          name="sample_data"
          create={DataCreate}
          list={DataList}
          show={DataShow}
          edit={DataEdit}
        />
      </Admin>
    );
}

ReactDOM.render(<App />, document.getElementById("react"));
