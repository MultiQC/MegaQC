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
    Badge,
    ListGroup,
    ListGroupItem,
    Modal,
    ModalBody,
    ModalFooter,
    ModalHeader,
    Alert,
    Table
} from 'reactstrap';
import MegaQcApi from '../api';
import Input from "reactstrap/es/Input";

class Filter {
    constructor() {
        this.type = 'samplemeta';
        this.key = null;
        this.comparison = null;
        this.value = null;
    }
}

export default function NewFilter(props) {
    const {isOpen, toggle} = props;
    const [filterGroups, setFilterGroups] = useState([
        [new Filter()]
    ]);

    return (
        <Modal size={'xl'} isOpen={isOpen} toggle={toggle}>
            <ModalHeader toggle={toggle}>
                <h3>
                    Sample Filters: New Set
                </h3>
            </ModalHeader>
            <ModalBody>
                <p>Create a new sample filter set. You can use these filter sets when creating plots.
                    Remember to save at the bottom when you're finished!</p>

                <Alert color={'light'}>
                    <i className="fa fa-info-circle" aria-hidden="true"/>
                    Filters within a group are applied with <code>AND</code> logic.
                    Different filter groups have <code>OR</code> logic.
                </Alert>

                {filterGroups.map((filterGroup, i) => {
                    return (
                        <Card>
                            <CardHeader>
                                Filter Group {i+1}
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
                                    {filterGroup.map((filter, i) => {
                                        return (
                                            <tr key={i}>
                                                <td>
                                                    <Input type={'select'} value={filter.type}>
                                                        <option value="timedelta">Dynamic date range</option>
                                                        <option value="daterange">Specific dates</option>
                                                        <option value="reportmeta">Report metadata</option>
                                                        <option value="samplemeta">Sample data</option>
                                                    </Input>
                                                </td>
                                                <td>
                                                    <Input type={'select'}/>
                                                </td>
                                                <td>
                                                    <Input type={'select'}/>
                                                </td>
                                                <td>
                                                    <Input type={'select'}/>
                                                </td>
                                                <td>
                                                    <Button size={'sm'} color={'primary'}>
                                                        <i className="fa fa-fw fa-plus-square" aria-hidden="true"></i>
                                                        Add
                                                    </Button>
                                                </td>
                                            </tr>
                                        );
                                    })}
                                    </tbody>
                                </Table>
                            </CardBody>
                        </Card>
                    );
                })}
            </ModalBody>
            <ModalFooter>

            </ModalFooter>
        </Modal>
    );
}
