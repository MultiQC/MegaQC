import ReactDOM from "react-dom";
import React, { useEffect, useRef, useState } from "react";
import { getClient } from "./util/api";
import { MuiPickersUtilsProvider } from "@material-ui/pickers";
import MomentUtils from "@date-io/moment";
import * as Yup from "yup";

import TrendForm from "./trend/form";
import TrendPlot from "./trend/plot";
import { Col, Row } from "reactstrap";
import { SampleFilter } from "./trend/sampleFilter";

function selectValue(select) {
  return Array.from(select.options)
    .filter((o) => o.selected)
    .map((o) => o.value);
}

const trendSchema = Yup.object().shape({
  field: Yup.string().label("Quality Field"),
  outlier: Yup.string().oneOf(["z"]),
});

function Trend(props) {
  const [dataTypes, setDataTypes] = useState([]);
  const [plotData, setPlotData] = useState({});
  const [selectedFilter, selectFilter] = useState(null);
  const [revision, setRevision] = useState(0);
  const [currentUser, setCurrentUser] = useState(null);
  const [plotSettings, setPlotSettings] = useState({});

  // Start with an unauthenticated client, then request a token ASAP
  const client = useRef(getClient());
  useEffect(() => {
    client.current.get("users", "current").then((user) => {
      // Update the API token, and also store the current user
      const token = user.toJSON().api_token;
      client.current._transport._auth.header = { access_token: token };
      setCurrentUser(user);
    });
  }, []);

  // When we first create the component, request the data types that could be plotted
  useEffect(() => {
    client.current
      .find("data_types", {
        "page[size]": 0,
      })
      .then((resources) => {
        setDataTypes(resources.map((resource) => resource.toJSON()));
      });
  }, []);

  // Whenever the form data changes, redraw the plot
  useEffect(() => {
    client.current
      .find("plots/trends/series", {
        // filter, unlike the Formik fields is special because it is
        // a reuseable component that isn't a field
        filter: selectedFilter,
        fields: JSON.stringify(plotSettings.fields),
        control_limits: {
          enabled: plotSettings.controlLimits,
          sigma: plotSettings.stdDevs,
        },
        center_line: plotSettings.centerLine,
      })
      .then((data) => {
        const newData = data.map((datum) => datum.toJSON());
        setPlotData(newData);
        setRevision((rev) => rev + 1);
      });
  }, [selectedFilter, plotSettings]);

  return (
    <>
      <h1>Data Trends</h1>
      <Row>
        <Col lg={{ size: 4 }}>
          <SampleFilter
            qcApi={client.current}
            onFilterChange={selectFilter}
            user={currentUser}
          />
        </Col>
        <Col lg={{ size: 8 }}>
          <TrendForm
            dataTypes={dataTypes}
            onSubmit={(props) => {
              setPlotSettings(props);
            }}
          />
        </Col>
      </Row>
      <Row
        style={{
          paddingTop: "20px",
        }}
      >
        <Col sm={12}>
          <TrendPlot
            currentUser={currentUser}
            client={client}
            plotData={plotData}
            plotSettings={plotSettings}
            selectedFilter={selectedFilter}
          />
        </Col>
      </Row>
    </>
  );
}

ReactDOM.render(
  <MuiPickersUtilsProvider utils={MomentUtils}>
    <Trend />
  </MuiPickersUtilsProvider>,
  document.getElementById("react")
);
