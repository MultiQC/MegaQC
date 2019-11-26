import React from 'react';
import {JsonEditor as Editor} from 'jsoneditor-react';
import {InputLabel, Typography} from "@material-ui/core";
import 'jsoneditor-react/es/editor.min.css';

export const renderJsonField = React.forwardRef(({input, label, meta: {touched, error}, editorProps, ...custom}, ref) => {
    const finalEditorProps = Object.assign({
        search: false,
        navigationBar: false,
        statusBar: false,
        mainMenuBar: false
    }, editorProps);
    return (
        <>
            <InputLabel>
                <Typography variant={"subtitle2"}>
                    {label}
                </Typography>
            </InputLabel>
            <Editor
                innerRef={ref}
                value={input.value}
                onChange={input.onChange}
                {...finalEditorProps}
            />
        </>
    );
});
