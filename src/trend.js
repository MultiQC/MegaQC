import ReactDOM from 'react-dom';
import React, {useEffect, useRef, useState} from 'react';
import {getClient} from './util/api';
import {MuiPickersUtilsProvider} from '@material-ui/pickers';
import MomentUtils from '@date-io/moment';
import * as Yup from 'yup';

import TrendForm from "./trend/form";
import TrendPlot from "./trend/plot";

function selectValue(select) {
    return Array.from(select.options).filter(o => o.selected).map(o => o.value)
}

const trendSchema = Yup.object().shape({
    field: Yup.string().label('Quality Field'),
    outlier: Yup.string().oneOf(['z'])
});

function Trend(props) {
    const [dataTypes, setDataTypes] = useState([]);
    const [selectedDataTypes, selectDataTypes] = useState([]);
    const [selectedFilter, selectFilter] = useState(null);
    const [plotData, setPlotData] = useState([]);
    const [revision, setRevision] = useState(0);
    const [saveBoxOpen, openSaveBox] = useState(false);
    const [currentUser, setCurrentUser] = useState(null);

    // Start with an unauthenticated client, then request a token ASAP
    const client = useRef(getClient());

    useEffect(() => {
        client.current.get('users', 'current').then(user => {
            // Update the API token, and also store the current user
            const token = user.toJSON().api_token;
            client.current._transport._auth.header = {access_token: token};
            setCurrentUser(user);
        })
    }, []);


    // When we first create the component, request the data types that could be plotted
    useEffect(() => {
        client.current.find('data_types')
            .then(resources => {
                setDataTypes(resources.map(resource => {
                    const dType = resource.toJSON();
                    dType.niceName = dType.section.replace(/_/g, ' ')
                        + ': '
                        + dType.key.replace(/_/g, ' ');
                    return dType;
                }));
            })
    }, []);

    useEffect(() => {
        if (selectedDataTypes.length > 0) {
            client.current.find('plots/trends/series', {
                // filter, unlike the Formik fields is special because it is
                // a reuseable component that isn't a field
                filter: selectedFilter,
                fields: JSON.stringify(values.fields),
                outliers: values.outlier
            })
                .then(data => {
                    const newData = data.map(datum => datum.toJSON());
                    setPlotData(newData);
                    setRevision(rev => rev + 1);
                })
        }
    }, [values, values.fields, values.outlier, selectedFilter]);
    // The template

    return (
        <>
            <TrendForm/>
            <TrendPlot/>
        </>
    );
}


ReactDOM.render(
    <MuiPickersUtilsProvider utils={MomentUtils}>
        <Trend/>
    </MuiPickersUtilsProvider>,
    document.getElementById('react')
);

