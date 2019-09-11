import React from 'react';
import {Button, Container, FormGroup, Label, Modal, ModalBody, ModalFooter, ModalHeader, Row} from 'reactstrap';
import BootstrapField from './bootstrapField';
import filterSchema from '../util/filterSchema';
import * as Yup from 'yup';

import {Field, Form, Formik} from 'formik';


export default function SavePlot(props) {
    const {isOpen, toggle, qcApi, plotData, plotType} = props;

    return <Formik
        initialValues={{
            title: '',
            description: ''
        }}
        validationSchema={Yup.object().shape({
            title: Yup.string().min(3).label('Title').required(),
            description: Yup.string().label('Description').required()
        })}
        onSubmit={(values, {setSubmitting}) => {
            // Note, this resource corresponds to SampleFilterSchema in the backend

            // Create the resource
            const resource = qcApi.create('favourites');
            resource.set('title', values.title);
            resource.set('description', values.description);
            resource.set('plot_type', plotType);
            resource.set('data', plotData);

            // Save it
            resource.sync()
                .then(() => {
                    toggle(true);
                }).finally(() => {
                setSubmitting(false);
            });
        }}
    >
        {({
              values,
              isSubmitting
          }) => (
            <Modal size={'sm'} isOpen={isOpen} toggle={() => toggle(false)}>
                <Form>
                    <ModalHeader tag={'h3'} toggle={toggle}>
                        Save as Favourite
                    </ModalHeader>
                    <ModalBody>
                        <Container>
                            <Row>
                                <FormGroup>
                                    <Label>Plot Name</Label>
                                    <Field component={BootstrapField} name='title'/>
                                </FormGroup>
                            </Row>
                            <Row>
                                <FormGroup>
                                    <Label>Description</Label>
                                    <Field component={BootstrapField} name='description'/>
                                </FormGroup>
                            </Row>
                        </Container>
                    </ModalBody>
                    <ModalFooter>
                        <Button type="submit" disabled={isSubmitting} color="primary" block>Save
                            Filter</Button>
                    </ModalFooter>
                </Form>
            </Modal>
        )}
    </Formik>;
}
