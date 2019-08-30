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
import getClient from './util/api';
import {SampleFilter} from './components/sampleFilter';

function selectValue(select) {
    return Array.from(select.options).filter(o => o.selected).map(o => o.value)
}

function Trend(props) {
    const [dataTypes, setDataTypes] = useState([]);
    const [selectedFilter, selectFilter] = useState(null);
    const [apiClient, setApiClient] = useState(getClient());
    const [selectedDataTypes, selectDataTypes] = useState([]);
    const [plotData, setPlotData] = useState(null);

    // Whenever the plot data type or filter changes, we have to re-calculate the plot data
    useEffect(() => {
        if (selectedDataTypes.length > 0) {
            apiClient.find('plots/trends/series', {fields: selectedDataTypes, filter: selectedFilter})
                .then(data => {
                    setPlotData(data);
                })
        }
    }, [selectedDataTypes, selectedFilter]);

    // When we first create the component, request the data types that could be plotted
    useEffect(() => {
        apiClient.find('')
            .then(response => {
                setDataTypes(response.types);
            })
    }, []);

    // The template
    return (
        <div>
            <h1>Data Trends</h1>
            <Row>
                <Col sm={{size: 6}}>
                    <SampleFilter
                        qcApi={apiClient}
                        onFilterChange={filter => {
                            selectFilter(filter);
                        }}
                    />
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
                                    value={selectedDataTypes}
                                    onChange={e => selectDataTypes(selectValue(e.target))}
                                    name="selectMulti"
                                    id="exampleSelectMulti"
                                    multiple={true
                                    }>
                                    {dataTypes.map((type, i) => {
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
                                data={plotData}
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


ReactDOM.render(
    <Trend/>,
    document.getElementById('react-trend')
);

