import debounce from "just-debounce-it";
import React, { useState, useEffect, useCallback } from "react";
import { connect } from "formik";

const AutoSave = ({ debounceMs, formik }) => {
  const [lastSaved, setLastSaved] = useState(null);
  const debouncedSubmit = useCallback(
    debounce(
      () =>
        formik.submitForm().then(() => setLastSaved(new Date().toISOString())),
      debounceMs
    ),
    [debounceMs, formik.submitForm]
  );

  useEffect(() => {
    debouncedSubmit();
  }, [debouncedSubmit, formik.values]);

  return null;
};

export default connect(AutoSave);
