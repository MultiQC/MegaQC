import ReactDOM from 'react-dom';
import React, {useState, useEffect} from 'react';
import {
    Button,
    Form,
    FormGroup,
    Label,
    Input,
    FormText,
    Container,
    Row,
    Col,
    Card,
    CardBody,
    CardTitle,
    CardHeader,
} from 'reactstrap';
import Plot from 'react-plotly.js';
import MegaQcApi from './api';
import {SampleFilter} from './components/sample_filter';

function selectValue(select) {
    return Array.from(select.options).filter(o => o.selected).map(o => o.value)
}

class Trend extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            dataTypes: [],
            apiClient: new MegaQcApi(),
            selectedDataTypes: [],
            plotData: null
        };
    }

    componentDidUpdate(prevProps, prevState, snapshot) {
        if (prevState.selectedDataTypes !== this.state.selectedDataTypes) {
            this.state.apiClient.getTrendData(this.state.selectedDataTypes).then(data => {
                this.setState({
                    plotData: data
                })
            })
        }
    }

    componentDidMount() {
        this.state.apiClient.getDataTypes().then(response => {
            this.setState({
                dataTypes: response.types
            })
        })
    }

    render() {
        return (
            <div>
                <h1>Data Trends</h1>
                <Row>
                    <Col sm={{size: 6}}>
                        <SampleFilter qcApi={this.state.apiClient}/>
                    </Col>
                    <Col sm={{size: 6}}>
                        <Card>
                            <CardHeader>
                                <h2>
                                    Choose Fields to Plot
                                </h2>
                            </CardHeader>
                            <CardBody>
                                <FormGroup>
                                    <Label for="exampleSelectMulti">Select Multiple</Label>
                                    <Input
                                        type="select"
                                        value={this.state.selectedDataTypes}
                                        onChange={e => this.setState({
                                            selectedDataTypes: selectValue(e.target)
                                        })}
                                        name="selectMulti"
                                        id="exampleSelectMulti"
                                        multiple={true
                                        }>
                                        {this.state.dataTypes.map((type, i) => {
                                            return <option key={i}>{type}</option>
                                        })}
                                    </Input>
                                </FormGroup>
                            </CardBody>
                        </Card>
                    </Col>
                </Row>
                <Row>
                    <Col sm={12}>
                        <Card>
                            <CardHeader>
                                <h2>
                                    Trend Plot
                                </h2>
                            </CardHeader>
                            <CardBody>
                                <Plot
                                    data={this.state.plotData}
                                    useResizeHandler={true}
                                    layout={{
                                        autosize: true
                                    }}
                                    style={{
                                        width: '100%',
                                        height: '100%'
                                    }}
                                />
                            </CardBody>
                        </Card>
                    </Col>
                </Row>
            </div>
        );
    }
}


ReactDOM.render(
    <Trend/>,
    document.getElementById('react-trend')
);

