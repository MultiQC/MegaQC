import React, {useState, useEffect,} from 'react';
import classnames from 'classnames';
import PropTypes from 'prop-types';
import {
    Row,
    Col,
    Card,
    CardBody,
    ListGroup,
    ListGroupItem
} from 'reactstrap';
import MegaQcApi from '../api';

export function SampleFilter(props) {
    const {qcApi, onFilterChange} = props;

    const [numSamples, setNumSamples] = useState(0);
    const [sampleFilters, setSampleFilters] = useState([]);
    const [selectedFilter, setSelectedFilter] = useState(null);
    const [selectedGroup, setSelectedGroup] = useState(null);

    // The first time this is run, request the filters
    useEffect(() => {
        qcApi.getFilterData().then(filters => {
            setSampleFilters(filters);
        });
    }, []);

    // Whenever the filter selection changes, ask the server for the number of samples etc, and also report back
    // to anything listening to this
    useEffect(() => {
        onFilterChange(selectedFilter);

        if (selectedFilter !== null) {
            qcApi.reportFilterFields({
                filters_id: selectedFilter
            }).then(data => {
                const {num_samples, report_plot_types, success} = data;
                setNumSamples(num_samples);
            });
        }
    }, [selectedFilter]);

    return (
        <Card>
            <h4 className="card-header">
                Filter Samples
                <span
                    className={classnames({
                        'num_filtered_samples': true,
                        'badge': true,
                        'badge-pill': true,
                        'badge-danger': true,
                        'badge-warning': false,
                        'badge-success': false
                    })}> {numSamples} samples </span>
                <button className="btn btn-sm btn-outline-primary float-right" data-toggle="modal"
                        data-target="#create_filter_modal">
                    <i className="fa fa-fw fa-plus-square" aria-hidden="true"/>
                    Add
                </button>
            </h4>
            <CardBody>
                <Row>
                    <Col sm={3}>
                        <nav className="nav flex-column nav-pills" id="sample-filter-group-select" role="tablist">
                            {Object.keys(sampleFilters).sort().map((sfg, i) => {
                                return (
                                    <a className={classnames({
                                        'nav-link': true,
                                        'active': i === selectedGroup
                                    })}
                                       href={`#sample_filter_group_${i}`}
                                       key={i}
                                       onClick={() => {
                                           this.setState({
                                               selectedGroup: i
                                           });
                                       }}
                                    >{sfg}</a>

                                );
                            })}
                        </nav>
                    </Col>
                    <Col sm={8}>
                        <hr className="d-md-none"/>
                        <div id="sample-filter-groups">
                            {Object.keys(sampleFilters).sort().map((key, j) => {
                                return (
                                    <div
                                        key={j}
                                        className="sample-filters-group"
                                        id={`sample_filter_group_${j}`}
                                        data-filtergroup={{key}}>
                                        <ListGroup>
                                            {sampleFilters[key].map((sf, i) => {
                                                return <ListGroupItem
                                                    onClick={() => {
                                                        setSelectedFilter(sf.id);
                                                    }}
                                                    key={i}
                                                    tag={"button"}
                                                    className={classnames({
                                                        'sample-filter-btn': true,
                                                        'list-group-item-action': true,
                                                        'active': sf.id === selectedFilter
                                                    })}
                                                    data-filterid={sf.id}>
                                                    {sf.name}
                                                </ListGroupItem>

                                            })}
                                        </ListGroup>
                                    </div>
                                );
                            })}
                        </div>
                    </Col>
                </Row>
            </CardBody>
        </Card>
    );
}

SampleFilter.propTypes = {
    qcApi: PropTypes.instanceOf(MegaQcApi),

    /**
     * Function to run when the user selects a filter. Calls the function with the
     */
    onFilterChange: PropTypes.func
};

