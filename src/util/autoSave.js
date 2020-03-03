import debounce from "just-debounce-it";
import React, { useState, useEffect, useCallback } from "react";
import { useFormikContext } from "formik";

export const AutoSave = ({ debounceMs }) => {
  const formik = useFormikContext();
  const debouncedSubmit = useCallback(debounce(formik.submitForm, debounceMs), [
    debounceMs,
    formik.submitForm
  ]);

  useEffect(debouncedSubmit, [debouncedSubmit, formik.values]);

  return null;
};
export default AutoSave;
