import React from 'react';
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

export class SampleFilter extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            numSamples: 0,
            sampleFilters: []
        };
    }

    componentDidMount() {
        this.props.qcApi.getFilterData().then(filters => {
            this.setState({sampleFilters: filters});
        });
    }

    render() {
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
                        })}> {this.state.numSamples} samples </span>
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
                                {Object.keys(this.state.sampleFilters).sort().map((sfg, i) => {
                                    return (
                                        <a className={classnames({
                                            'nav-link': true,
                                            'active': i === 0
                                        })}
                                           href={`#sample_filter_group_${i}`}
                                           key={i}
                                        >{sfg}</a>

                                    );
                                })}
                            </nav>
                        </Col>
                        <Col sm={8}>
                            <hr className="d-md-none"/>
                            <div id="sample-filter-groups">
                                {Object.keys(this.state.sampleFilters).sort().map((key, j) => {
                                    if (j === 0) {
                                        return (
                                            <div
                                                key={j}
                                                className="sample-filters-group"
                                                id={`sample_filter_group_${j}`}
                                                data-filtergroup={{key}}>
                                                <ListGroup>
                                                    {this.state.sampleFilters[key].map((sf, i) => {
                                                        return <ListGroupItem
                                                            key={i}
                                                            tag={"button"}
                                                            className={classnames({
                                                                'sample-filter-btn': true,
                                                                'list-group-item-action': true,
                                                                'active': j === 0
                                                            })}
                                                            data-filterid={sf.id}>
                                                            {sf.name}
                                                        </ListGroupItem>

                                                    })}
                                                </ListGroup>
                                            </div>
                                        );
                                    }
                                })}
                            </div>
                        </Col>
                    </Row>
                </CardBody>
            </Card>
        );
    }
}

SampleFilter.propTypes = {
    qcApi: PropTypes.instanceOf(MegaQcApi)
};

