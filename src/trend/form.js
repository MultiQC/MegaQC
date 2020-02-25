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

export default function TrendForm(props){
    return <Formik
        initialValues={{
            // Which field to plot
            fields: [],
            // What outlier detection (if any) to use
            outlier: null,
            // The statistic plotted on the center line
            centerLine: 'mean',
            // Whether or not to show control limits
            controlLimits: true,
            // Number of standard deviations to use as the control limit
            stdDevs: 3
        }}
    >{({handleSubmit, handleChange, handleBlur, values, errors}) => {
        // Whenever the plot data type or filter changes, we have to re-calculate the plot data

        return (
            <div>
                <SavePlot
                    user={currentUser}
                    qcApi={client.current}
                    plotData={{
                        // This is a bit of a hack to ensure the filters save in a format expected by the old parts of MegaQC
                        filters_id: selectedFilter || -1,
                        fields: selectedDataTypes
                    }}
                    plotType={'trend'}
                    isOpen={saveBoxOpen}
                    toggle={() => {
                        openSaveBox(open => !open)
                    }}
                />
                <h1>Data Trends</h1>
                <Row>
                    <Col sm={{size: 4}}>
                        <SampleFilter
                            qcApi={client.current}
                            onFilterChange={filter => {
                                selectFilter(filter);
                            }}
                        />
                    </Col>
                    <Col sm={{size: 8}}>
                        <Card>
                            <CardHeader>
                                <h2>
                                    Options
                                </h2>
                            </CardHeader>
                            <CardBody>
                                <Form>
                                    <FormGroup>
                                        <Label for="exampleSelectMulti">Data
                                            Types</Label>
                                        <Input
                                            multiple={true}
                                            type="select"
                                            value={selectedDataTypes}
                                            onChange={e => selectDataTypes(selectValue(e.target))}
                                            name="selectMulti"
                                            id="exampleSelectMulti"
                                        >
                                            {dataTypes.map((type, i) => {
                                                return <option
                                                    key={i}
                                                    value={type.id}
                                                >{type.niceName}</option>
                                            })}
                                        </Input>
                                    </FormGroup>
                                    <FormGroup>
                                        <Label>Center Line</Label>
                                        <Field
                                            component={BootstrapField}
                                            name={`centerLine`}
                                            type={'select'}
                                        >
                                            <option value="median">Median</option>
                                            <option value="mean">Mean</option>
                                        </Field>
                                    </FormGroup>
                                    <FormGroup check>
                                        <Label check>
                                            <Field
                                                component={BootstrapField}
                                                name={`controlLimits`}
                                                type={'checkbox'}
                                            />
                                            &nbsp; Show Control Limits
                                        </Label>
                                    </FormGroup>
                                    <FormGroup>
                                        <Label>Control Limits</Label>
                                        <Field
                                            component={BootstrapField}
                                            name={`stdDevs`}
                                            type={'number'}
                                        />
                                    </FormGroup>
                                    <OutlierDetection/>
                                </Form>
                            </CardBody>
                        </Card>
                    </Col>
                </Row>
                <Row
                    style={{
                        paddingTop: '20px'
                    }}
                >
                    <Col sm={12}>
                    </Col>
                </Row>
            </div>
        );
    }}
    </Formik>
}