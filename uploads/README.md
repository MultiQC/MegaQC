# MegaQC Uploads folder

This folder contains temporary MultiQC report data (gzipped JSON files).

As the process of saving data can take quite a long time, we don't want
to make the MultiQC user wait. Instead, we just save the file here and
continue with MultiQC execution. MegaQC then processes these files
asynchronously with a scheduled process.
