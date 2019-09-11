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
import {client} from './util/api';
import {SampleFilter} from './components/sampleFilter';
import OutlierDetection from './components/outlierDetection';
import SavePlot from './components/savePlot';
import {MuiPickersUtilsProvider} from '@material-ui/pickers';
import MomentUtils from '@date-io/moment';

function selectValue(select) {
    return Array.from(select.options).filter(o => o.selected).map(o => o.value)
}

function Trend(props) {
    const [dataTypes, setDataTypes] = useState([]);
    const [selectedFilter, selectFilter] = useState(null);
    const [selectedDataTypes, selectDataTypes] = useState([]);
    const [plotData, setPlotData] = useState([]);
    const [revision, setRevision] = useState(0);
    const [outlier, setOutlier] = useState(null);
    const [saveBoxOpen, openSaveBox] = useState(false);

    // Whenever the plot data type or filter changes, we have to re-calculate the plot data
    useEffect(() => {
        if (selectedDataTypes.length > 0) {
            client.find('plots/trends/series', {
                fields: JSON.stringify(selectedDataTypes),
                filter: selectedFilter,
                outliers: outlier
            })
                .then(data => {
                    const newData = data.map(datum => datum.toJSON());
                    setPlotData(newData);
                    setRevision(rev => rev + 1);
                })
        }
    }, [selectedDataTypes, selectedFilter, outlier]);


    // When we first create the component, request the data types that could be plotted
    useEffect(() => {
        client.find('data_types')
            .then(resources => {
                setDataTypes(resources.map(resource => resource.toJSON()));
            })
    }, []);

    // The template
    return (
        <div>
            <SavePlot
                qcApi={client}
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
                        qcApi={client}
                        onFilterChange={filter => {
                            selectFilter(filter);
                        }}
                    />
                </Col>
                <Col sm={{size: 4}}>
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
                                >
                                    {dataTypes.map((type, i) => {
                                        return <option key={i} value={type.id}>{type.key}</option>
                                    })}
                                </Input>
                            </FormGroup>
                        </CardBody>
                    </Card>
                </Col>
                <Col sm={{size: 4}}>
                    <Card>
                        <CardHeader>
                            <h2>
                                Outlier Detection
                            </h2>
                        </CardHeader>
                        <CardBody>
                            <OutlierDetection
                                onChange={setOutlier}
                            />
                        </CardBody>
                    </Card>
                </Col>
            </Row>
            <Row style={{
                paddingTop: '20px'
            }}>
                <Col sm={12}>
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
                </Col>
            </Row>
        </div>
    );
}


ReactDOM.render(
    <MuiPickersUtilsProvider utils={MomentUtils}>
        <Trend/>
    </MuiPickersUtilsProvider>,
    document.getElementById('react-trend')
);

