import ReactDOM from 'react-dom';
import React, {useEffect, useRef, useState} from 'react';
import {
    Button,
    Card,
    CardBody,
    CardHeader,
    Col,
    FormGroup,
    Input,
    Label,
    Row,
    Form
} from 'reactstrap';
import Plot from 'react-plotly.js';
import {getClient, getToken} from './util/api';
import {SampleFilter} from './components/sampleFilter';
import OutlierDetection from './components/outlierDetection';
import SavePlot from './components/savePlot';
import {MuiPickersUtilsProvider} from '@material-ui/pickers';
import MomentUtils from '@date-io/moment';
import {useFormik, Field, Formik} from 'formik';
import * as Yup from 'yup';
import BootstrapField from './components/bootstrapField';

export default function TrendPlot(props){
    return (
        <Card>
            <CardHeader className={'clearfix'}>
                <Button
                    className={'float-right'}
                    onClick={() => {
                        openSaveBox(true)
                    }}
                >
                    Save Plot Favourite
                </Button>
                <h2>
                    Trend Plot
                </h2>
            </CardHeader>
            <CardBody>
                <Plot
                    revision={revision}
                    data={plotData}
                    useResizeHandler={true}
                    layout={{
                        hovermode: 'closest',
                        autosize: true
                    }}
                    style={{
                        width: '100%',
                        height: '100%'
                    }}
                />
            </CardBody>
        </Card>
    );
}