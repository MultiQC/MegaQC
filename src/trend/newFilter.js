import React, { useEffect, useState } from "react";
import {
  Alert,
  Button,
  Card,
  CardBody,
  CardFooter,
  CardHeader,
  Col,
  Container,
  FormGroup,
  Label,
  Modal,
  ModalBody,
  ModalFooter,
  ModalHeader,
  Row,
  Table
} from "reactstrap";
import BootstrapField from "./bootstrapField";
import filterSchema from "../util/filterSchema";
import FilterRow from "./filterRow";
import Filter from "../util/filter";

import { Field, FieldArray, Form, Formik } from "formik";

export default function NewFilter(props) {
  const { isOpen, toggle, qcApi } = props;
  const [sampleFields, setSampleFields] = useState([]);
  const [reportFields, setReportFields] = useState([]);
  const [filterGroups, setFilterGroups] = useState([]);

  // Fetch the filter groups
  useEffect(() => {
    qcApi.find("filter_groups").then(groups => {
      setFilterGroups(groups.map(group => group._getUid()));
    });
  }, []);

  // Fetch the sample fields
  useEffect(() => {
    qcApi.find("data_types").then(groups => {
      setSampleFields(groups.map(group => group.get("key")));
    });
  }, []);

  // Fetch the report metadata fields
  useEffect(() => {
    qcApi.find("report_meta").then(groups => {
      setReportFields(groups.map(group => group._getUid()));
    });
  }, []);

  return (
    <Formik
      initialValues={{
        filters: [[new Filter()]],
        filterName: "",
        filterGroup: "Global",
        visibility: "private"
      }}
      validationSchema={filterSchema}
      onSubmit={(values, { setSubmitting }) => {
        // Note, this resource corresponds to SampleFilterSchema in the backend

        // Create the resource
        const filterResource = qcApi.create("filters");
        filterResource.set("tag", values.filterGroup);
        filterResource.set("name", values.filterName);
        filterResource.set("public", values.visibility === "public");
        filterResource.set("data", values.filters);

        // Save it
        filterResource
          .sync()
          .then(() => {
            toggle(true);
          })
          .finally(() => {
            setSubmitting(false);
          });
      }}
    >
      {({ values, isSubmitting }) => (
        <Modal size={"xl"} isOpen={isOpen} toggle={() => toggle(false)}>
          <Form>
            <ModalHeader tag={"h3"} toggle={toggle}>
              Sample Filters: New Set
            </ModalHeader>
            <ModalBody>
              <datalist id="filter_tags">
                {filterGroups.map(group => {
                  return <option value={group}>{group}</option>;
                })}
              </datalist>

              <p>
                Create a new sample filter set. You can use these filter sets
                when creating plots. Remember to save at the bottom when you're
                finished!
              </p>

              <Alert color={"light"}>
                <i className="fa fa-info-circle" aria-hidden="true" />
                Filters within a group are applied with <code>AND</code> logic.
                Different filter groups have <code>OR</code> logic.
              </Alert>
              <Row>
                <Col md={4}>
                  <FormGroup>
                    <Label>Filter Name</Label>
                    <Field component={BootstrapField} name="filterName" />
                  </FormGroup>
                </Col>
                <Col md={4}>
                  <FormGroup>
                    <Label>Filter Group</Label>
                    <Field
                      component={BootstrapField}
                      name="filterGroup"
                      list="filter_tags"
                    />
                  </FormGroup>
                </Col>
                <Col md={4}>
                  <FormGroup>
                    <Label>Visibility</Label>
                    <Field
                      type={"select"}
                      component={BootstrapField}
                      name="visibility"
                    >
                      <option value={"private"}>Just me</option>
                      <option value={"public"}>Everyone</option>
                    </Field>
                  </FormGroup>
                </Col>
              </Row>
              <FieldArray
                name="filters"
                render={outerArrayHelpers => (
                  <>
                    {values.filters.map((filterGroup, i) => {
                      return (
                        <Card
                          style={{
                            marginBottom: "1em"
                          }}
                          key={i}
                        >
                          <CardHeader>Filter Group {i + 1}</CardHeader>
                          <CardBody
                            style={{
                              padding: 0
                            }}
                          >
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
                                  render={innerArrayHelpers =>
                                    filterGroup.map((filter, j) => {
                                      return (
                                        <tr key={j}>
                                          <FilterRow
                                            sampleFields={sampleFields}
                                            reportFields={reportFields}
                                            name={`filters.${i}.${j}`}
                                            innerArrayHelpers={
                                              innerArrayHelpers
                                            }
                                          />
                                        </tr>
                                      );
                                    })
                                  }
                                />
                              </tbody>
                            </Table>
                          </CardBody>
                          <CardFooter>
                            <Button
                              onClick={() => {
                                outerArrayHelpers.remove(i);
                              }}
                              outline
                              color={"primary"}
                            >
                              Delete
                            </Button>
                          </CardFooter>
                        </Card>
                      );
                    })}

                    <Button
                      onClick={() => {
                        outerArrayHelpers.push([new Filter()]);
                      }}
                      outline
                      color={"primary"}
                    >
                      <i
                        className="fa fa-fw fa-plus-square"
                        aria-hidden="true"
                      />
                      Add new filter group
                    </Button>
                  </>
                )}
              />
            </ModalBody>
            <ModalFooter>
              <Container>
                <Row>
                  <Col
                    md={{
                      size: 6,
                      offset: 3
                    }}
                  >
                    <Button
                      type="submit"
                      disabled={isSubmitting}
                      color="primary"
                      block
                    >
                      Save Filter
                    </Button>
                  </Col>
                </Row>
              </Container>
            </ModalFooter>
          </Form>
        </Modal>
      )}
    </Formik>
  );
}
