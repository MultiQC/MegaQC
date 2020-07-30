import React from "react";
import { JsonEditor as Editor } from "jsoneditor-react";
import "jsoneditor-react/es/editor.min.css";
import get from "lodash/get";
import { Labeled } from "react-admin";
import { useField } from "react-final-form";

export function JsonInput({ source, record, resource, basePath, editorProps }) {
  const {
    input: { onChange, value },
    meta: { touched, error }
  } = useField(source);
  const finalEditorProps = Object.assign(
    {
      search: false,
      mode: "code",
      statusBar: false,
      allowedModes: ["tree", "code"]
    },
    editorProps
  );
  return (
    <Labeled
      record={record}
      resource={resource}
      basePath={basePath}
      fullWidth={true}
      source={source}
      disabled={false}
    >
      <Editor value={value} onChange={onChange} {...finalEditorProps} />
    </Labeled>
  );
}

export function JsonField({
  source,
  record,
  resource,
  basePath,
  editorProps = {}
}) {
  const finalEditorProps = Object.assign(
    {
      search: false,
      statusBar: false,
      mode: "view"
    },
    editorProps
  );

  const value = get(record, source);
  return (
    <Labeled
      record={record}
      resource={resource}
      basePath={basePath}
      fullWidth={true}
      source={source}
      disabled={false}
    >
      <Editor value={value} {...finalEditorProps} />
    </Labeled>
  );
}
