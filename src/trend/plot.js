import React, {useState} from 'react';
import {Button, Card, CardBody, CardHeader} from 'reactstrap';
import Plot from 'react-plotly.js';
import SavePlot from './savePlot';
import PropTypes from "prop-types";

export default function TrendPlot({currentUser, client, plotData, plotSettings, selectedFilter}) {
    const [saveBoxOpen, openSaveBox] = useState(false);
    return (
        <Card>
            <SavePlot
                user={currentUser}
                qcApi={client.current}
                plotData={{
                    // This is a bit of a hack to ensure the filters save in a format expected by the old parts of MegaQC
                    filters_id: plotSettings.selectedFilter || -1,
                    ...plotSettings
                }}
                plotType={'trend'}
                isOpen={saveBoxOpen}
                toggle={() => {
                    openSaveBox(open => !open)
                }}
            />
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
                    // revision={revision}
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
TrendPlot.propTypes = {
    currentUser: PropTypes.object,
    client: PropTypes.object.isRequired,

    // The plot series
    plotData: PropTypes.object.isRequired,

    // The settings, used for saving the plot
    plotSettings: PropTypes.object.isRequired,
    selectedFilter: PropTypes.object.isRequired,
};
