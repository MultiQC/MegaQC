# MegaQC Usage: Setup

## Submitting data

Before you can do anything useful in MegaQC, you need to submit some data
to the database. You do this by configuring and then running MultiQC.

### MultiQC configuration

MultiQC needs a couple of configuration variables to know how to send data to MegaQC.
To find these, log into MegaQC and use the navigation dropdown to get to the
_MultiQC Configuration_ page. Copy the specified text into `~/.multiqc_config.yaml`.

Note that this `megaqc_access_token` is specific to your MegaQC user, so shouldn't be
shared (it's effectively a password). All data uploaded using that token will be attributed
to your user.

### Running MultiQC

Once configured, run MultiQC as you would normally. You should see a couple of additional
log messages under the `megaqc` namespace as follows:

```
$ multiqc .

[INFO   ]         multiqc : This is MultiQC v1.3
[INFO   ]         multiqc : Template    : default
[INFO   ]         multiqc : Searching './'
Searching 63 files..  [####################################]  100%
[INFO   ]  feature_counts : Found 6 reports
[INFO   ]            star : Found 6 reports
[INFO   ]        cutadapt : Found 6 reports
[INFO   ]    fastq_screen : Found 6 reports
[INFO   ]          fastqc : Found 6 reports
[INFO   ]         multiqc : Compressing plot data
[INFO   ]          megaqc : Sending data to MegaQC
[INFO   ]          megaqc : Data upload successful
[INFO   ]         multiqc : Report      : multiqc_report.html
[INFO   ]         multiqc : Data        : multiqc_data
[INFO   ]         multiqc : MultiQC complete
```

**NB: You need MultiQC v1.3 or later for MegaQC integration to work.**
