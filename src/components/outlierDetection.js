import React from 'react';
import {FormGroup, Label} from 'reactstrap';
import BootstrapField from './bootstrapField';
import AutoSave from './autoSave';

import {Field, Formik} from 'formik';


export default function OutlierDetection(props) {
    const {onChange} = props;

    return <Formik
        initialValues={{
            type: 'none',
            threshold: '0.05'
        }}
        onSubmit={(values, {setSubmitting}) => {
            onChange(values)
        }}
    >
        {({
              values,
              isSubmitting,
          }) => {

            let thresholdName, showThreshold;
            switch (values.type) {
                case 'none':
                    thresholdName = '';
                    showThreshold = false;
                    break;
                case 'grubbs':
                    thresholdName = 'Alpha value';
                    showThreshold = true;
                    break;
                case 'z':
                    thresholdName = 'Z-score';
                    showThreshold = true;
                    break;
                default:
                    showThreshold = false;
                    thresholdName = '';
                    break;
            }

            return <>
                <AutoSave debounceMs={300}/>

                <FormGroup>
                    <Label>Outlier Detection Method</Label>
                    <Field
                        component={BootstrapField}
                        name={`type`}
                        type={'select'}
                    >
                        <option value={'none'}>None</option>
                        <option value={'grubbs'}>Grubbs test</option>
                        <option value={'z'}>Z-score</option>
                    </Field>
                </FormGroup>
                {showThreshold && <FormGroup>
                    <Label>{thresholdName}</Label>
                    <Field
                        component={BootstrapField}
                        name={`threshold`}
                        type={'number'}
                    />
                </FormGroup>}
            </>
        }}
    </Formik>;
}
