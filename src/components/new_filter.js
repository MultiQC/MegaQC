import React, {useState, useEffect,} from 'react';
import classnames from 'classnames';
import PropTypes from 'prop-types';
import {
    Row,
    Col,
    Button,
    Card,
    CardBody,
    CardHeader,
    CardFooter,
    Container,
    Badge,
    Input,
    Label,
    ListGroup,
    ListGroupItem,
    Modal,
    ModalBody,
    ModalFooter,
    ModalHeader,
    Alert,
    Table,
    FormGroup
} from 'reactstrap';
import BootstrapField from './BootstrapField';
import MegaQcApi from '../api';

import {Formik, Form, FieldArray, Field} from 'formik';

class Filter {
    constructor() {
        this.type = 'samplemeta';
        this.key = '';
        this.comparison = '';
        this.value = '';
    }
}

export default function NewFilter(props) {
    const {isOpen, toggle, qcApi} = props;

    return <Formik
        initialValues={{
            filters: [
                [new Filter()]
            ],
            filterName: '',
            filterGroup: 'Global',
            visibility: 'Just me'
        }}
        validate={values => {
            let errors = {};
            return errors;
        }}
        onSubmit={(values, {setSubmitting}) => {
            qcApi.saveFilters(values).then(() => {
                setSubmitting(false);
            });
        }}
    >
        {({
              values,
              isSubmitting
          }) => (
            <Modal size={'xl'} isOpen={isOpen} toggle={toggle}>
                <Form>
                    <ModalHeader tag={'h3'} toggle={toggle}>
                        Sample Filters: New Set
                    </ModalHeader>
                    <ModalBody>
                        <p>Create a new sample filter set. You can use these filter sets when creating plots.
                            Remember to save at the bottom when you're finished!</p>

                        <Alert color={'light'}>
                            <i className="fa fa-info-circle" aria-hidden="true"/>
                            Filters within a group are applied with <code>AND</code> logic.
                            Different filter groups have <code>OR</code> logic.
                        </Alert>
                        <Row>
                            <Col md={4}>
                                <FormGroup>
                                    <Label>Filter Name</Label>
                                    <Field component={BootstrapField} name='filterName'/>
                                </FormGroup>
                            </Col>
                            <Col md={4}>
                                <FormGroup>
                                    <Label>Filter Group</Label>
                                    <Field component={BootstrapField} name='filterGroup'/>
                                </FormGroup>
                            </Col>
                            <Col md={4}>
                                <FormGroup>
                                    <Label>Visibility</Label>
                                    <Field component={BootstrapField} name='visibility'/>
                                </FormGroup>
                            </Col>
                        </Row>
                        <FieldArray
                            name="filters"
                            render={outerArrayHelpers => (<>
                                    {
                                        values.filters.map((filterGroup, i) => {
                                            return (
                                                <Card style={{
                                                    marginBottom: '1em'
                                                }} key={i}>
                                                    <CardHeader>
                                                        Filter Group {i + 1}
                                                    </CardHeader>
                                                    <CardBody style={{
                                                        padding: 0
                                                    }}>
                                                        <Table responsive={true}>
                                                            <thead>
                                                            <tr>
                                                                <th>Type</th>
                                                                <th>Key</th>
                                                                <th>Comparison</th>
                                                                <th>Value</th>
                                                                <th>Actions</th>
                                                            </tr>
                                                            </thead>
                                                            <tbody>

                                                            <FieldArray
                                                                name={`filters.${i}`}
                                                                render={innerArrayHelpers => (
                                                                    filterGroup.map((filter, j) => {
                                                                        return (
                                                                            <tr key={j}>
                                                                                <td>
                                                                                    <Field
                                                                                        component={BootstrapField}
                                                                                        name={`filters.${i}.${j}.type`}
                                                                                        type={'select'}
                                                                                    >
                                                                                        <option
                                                                                            value="timedelta">
                                                                                            Dynamic date
                                                                                            range
                                                                                        </option>
                                                                                        <option
                                                                                            value="daterange">
                                                                                            Specific dates
                                                                                        </option>
                                                                                        <option
                                                                                            value="reportmeta">
                                                                                            Report metadata
                                                                                        </option>
                                                                                        <option
                                                                                            value="samplemeta">
                                                                                            Sample data
                                                                                        </option>
                                                                                    </Field>
                                                                                </td>
                                                                                <td>
                                                                                    <Field
                                                                                        name={`filters.${i}.${j}.key`}
                                                                                        component={BootstrapField}
                                                                                    >
                                                                                    </Field>
                                                                                </td>
                                                                                <td>
                                                                                    <Field
                                                                                        name={`filters.${i}.${j}.comparison`}
                                                                                        component={BootstrapField}
                                                                                        type={'select'}
                                                                                    >
                                                                                    </Field>
                                                                                </td>
                                                                                <td>
                                                                                    <Field
                                                                                        name={`filters.${i}.${j}.value`}
                                                                                        component={BootstrapField}>
                                                                                    </Field>
                                                                                </td>
                                                                                <td>
                                                                                    <Button
                                                                                        onClick={() => {
                                                                                            innerArrayHelpers.push(new Filter())
                                                                                        }}
                                                                                        size={'sm'}
                                                                                        color={'primary'}>
                                                                                        <i className="fa fa-fw fa-plus-square"
                                                                                           aria-hidden="true"/>
                                                                                        Add
                                                                                    </Button>
                                                                                </td>
                                                                            </tr>
                                                                        );
                                                                    })
                                                                )}/>
                                                            </tbody>
                                                        </Table>
                                                    </CardBody>
                                                    <CardFooter>
                                                        <Button onClick={() => {
                                                            outerArrayHelpers.remove(i)
                                                        }} outline color={'primary'}>
                                                            Delete
                                                        </Button>
                                                    </CardFooter>
                                                </Card>
                                            );
                                        })
                                    }

                                    <Button onClick={() => {
                                        outerArrayHelpers.push([new Filter()])
                                    }} outline color={'primary'}>
                                        <i className="fa fa-fw fa-plus-square" aria-hidden="true"/>
                                        Add new filter group
                                    </Button>
                                </>
                            )}/>
                    </ModalBody>
                    <ModalFooter>
                        <Container>
                            <Row>
                                <Col md={{
                                    size: 6,
                                    offset: 3
                                }}>
                                    <Button type="submit" disabled={isSubmitting} color="primary" block>Save
                                        Filter</Button>
                                </Col>
                            </Row>
                        </Container>
                    </ModalFooter>
                </Form>
            </Modal>
        )}
    </Formik>;
}
