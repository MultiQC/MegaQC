import React, { useState, useEffect, useMemo } from "react";
import classnames from "classnames";
import PropTypes from "prop-types";
import {
  Row,
  Button,
  Col,
  Card,
  CardBody,
  ListGroup,
  ListGroupItem,
  ButtonGroup,
  PopoverHeader,
  PopoverBody,
  Popover
} from "reactstrap";
import groupBy from "lodash/groupBy";

import uniqueId from "lodash/uniqueId";
import NewFilter from "./newFilter";

/**
 * This renders a single item in the filter list, including edit and delete buttons
 * @param filter API object for the filter to render
 * @param active If this filter is currently selected
 * @param setSelected Set the currently selected filter
 * @param setEdit Set the current filter being edited
 * @param onDelete Delete the provided filter
 */
function FilterItem({ filter, active, setSelected, setEdit, onDelete }) {
  const [id] = useState(uniqueId("filter-item-"));
  const [popoverOpen, setPopoverOpen] = useState(false);

  const toggle = () => setPopoverOpen(!popoverOpen);
  return (
    <ListGroupItem
      className={classnames({
        "list-group-item-action": true,
        "sample-filter-btn": true,
        active: active
      })}
      onClick={() => {
        setSelected(filter._getUid());
      }}
      data-filterid={filter._getUid()}
    >
      {filter.get("name")}
      <ButtonGroup className="float-right">
        <Button
          onClick={() => {
            // Start editing this filter
            setEdit(filter._getUid());
          }}
          size={"sm"}
          color={"secondary"}
          outline={true}
        >
          <i className="fa fa-fw fa-edit" aria-hidden="true" />
          Edit
        </Button>
        <Button size={"sm"} color={"danger"} outline={true} id={id}>
          <i className="fa fa-fw fa-trash" aria-hidden="true" />
          Delete
        </Button>
      </ButtonGroup>
      <Popover
        placement="bottom"
        target={id}
        isOpen={popoverOpen}
        toggle={toggle}
      >
        <PopoverHeader>Are you sure?</PopoverHeader>
        <PopoverBody>
          <ButtonGroup>
            <Button
              onClick={() => {
                onDelete(filter);
                setPopoverOpen(false);
              }}
              color="danger"
            >
              Yes
            </Button>
            <Button
              outline
              onClick={() => setPopoverOpen(false)}
              color="secondary"
            >
              No
            </Button>
          </ButtonGroup>
        </PopoverBody>
      </Popover>
    </ListGroupItem>
  );
}

/**
 * This is a reusable filter selection and editing box, that should be used whenever we need to apply sample filters
 */
export function SampleFilter(props) {
  const { qcApi, onFilterChange, user } = props;

  const [sampleFilters, setSampleFilters] = useState([]);
  const [selectedFilter, setSelectedFilter] = useState(null);
  const [selectedGroup, setSelectedGroup] = useState("Global");
  const [modalOpen, setModalOpen] = useState(false);
  const [editFilter, setEditFilter] = useState(null);

  function updateFilters() {
    qcApi.find("filters").then(filters => {
      setSampleFilters(filters);
    });
  }

  function toggleModal(filterCreated = false) {
    setModalOpen(!modalOpen);

    if (filterCreated) updateFilters();
  }

  // The first time this is run, request the filters
  useEffect(() => {
    updateFilters();
  }, []);

  const filterGroups = useMemo(() => {
    return groupBy(sampleFilters, filter => filter.get("tag"));
  }, [sampleFilters]);

  // Whenever the filter selection changes, report back to anything listening for this event
  useEffect(() => {
    onFilterChange(selectedFilter);
  }, [selectedFilter]);

  return (
    <Card>
      <NewFilter
        qcApi={qcApi}
        isOpen={modalOpen}
        toggle={toggleModal}
        resourceId={editFilter}
        user={user}
      />
      <h4 className="card-header">
        Filter Samples
        <Button
          onClick={toggleModal}
          size={"sm"}
          color={"primary"}
          outline={true}
          className="float-right"
        >
          <i className="fa fa-fw fa-plus-square" aria-hidden="true" />
          Add
        </Button>
      </h4>
      <CardBody>
        <Row>
          <Col sm={3}>
            <nav
              className="nav flex-column nav-pills"
              id="sample-filter-group-select"
              role="tablist"
            >
              {Object.keys(filterGroups)
                .sort()
                .map((filterGroup, i) => {
                  return (
                    <a
                      className={classnames({
                        "nav-link": true,
                        active: filterGroup === selectedGroup
                      })}
                      href={`#sample_filter_group_${i}`}
                      key={i}
                      onClick={() => {
                        setSelectedGroup(filterGroup);
                      }}
                    >
                      {filterGroup}
                    </a>
                  );
                })}
            </nav>
          </Col>
          <Col sm={9}>
            <hr className="d-sm-none" />
            <div id="sample-filter-groups">
              <ListGroup>
                <ListGroupItem
                  onClick={() => {
                    setSelectedFilter(null);
                  }}
                  tag={"button"}
                  className={classnames({
                    "sample-filter-btn": true,
                    "list-group-item-action": true,
                    active: null === selectedFilter
                  })}
                >
                  None
                </ListGroupItem>
                {selectedGroup in filterGroups &&
                  filterGroups[selectedGroup].map((filter, i) => {
                    const active = filter._getUid() === selectedFilter;
                    return (
                      <FilterItem
                        filter={filter}
                        active={active}
                        setEdit={() => {
                          // Start editing this filter
                          setEditFilter(filter._getUid());
                          // Open the edit modal
                          toggleModal();
                        }}
                        setSelected={() => {
                          setSelectedFilter(filter._getUid());
                        }}
                        onDelete={filter => {
                          filter.delete().then(() => {
                            updateFilters();
                          });
                        }}
                      />
                    );
                  })}
              </ListGroup>
            </div>
          </Col>
        </Row>
      </CardBody>
    </Card>
  );
}

SampleFilter.propTypes = {
  qcApi: PropTypes.object,

  /**
   * Function to run when the user selects a filter. Calls the function with the
   */
  onFilterChange: PropTypes.func
};
