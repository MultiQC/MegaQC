# MegaQC

#### A web-based tool to collect and visualise data from multiple MultiQC reports.

MegaQC is a Flask web application that lets you easily set up a MegaQC
website for your group or facility. Once running, MultiQC can be configured to
automatically save data to the website every time it runs. This data can then
be explored on the website, allowing visualisation of long-term trends.

## Installation
To see how to install MegaQC, see the [installation docs](docs/installation-prod.md).

This describe a typical setup for users of MegaQC. If you want to do
development work with the MegaQC code, see the
[development installation docs](docs/installation-dev.md).

## User Authentication
By default, MegaQC uses built-in user registration and authentication.
If you would prefer, you can log in using Google OAuth instead - simply set
the following environment variables in your `.bashrc` file:

```bash
export MEGAQC_GAUTH
export GOOGLE_LOGIN_CLIENT_ID='[ Client ID ]'
export GOOGLE_LOGIN_CLIENT_SECRET='[ Client Secret ]'
export GOOGLE_LOGIN_CLIENT_SCOPES='[ Default scopes ]'
export GOOGLE_LOGIN_REDIRECT_URI='[ Default redirect URI ]'
```

These values can be obtained at
[https://code.google.com/apis/console](https://code.google.com/apis/console).

### User permissions
MegaQC has three levels of authentication - _administrators_,
_users_ and _visitors_. Visitors require no authentication. The default
permissions for each group are as follows (in addition to the role above):

* _Visitors_
  * View basic website description page
* _Users_
  * View plots and data on MegaQC website
  * Submit data when running MultiQC
  * Save plot configs and dashboards
  * Delete own data submissions
* _Administrators_
  * Delete other people's data submissions
  * Create, edit and remove user profiles
  * Enable and disable user registration

### Submitting data to MegaQC
Once your MegaQC website is up and running, you will find a page on the
website describing how to configure the main [MultiQC](http://multiqc.info)
tool so that it submits data to your website.

In brief - MultiQC needs to know the address where the website is hosted, so
that it can submit data to the MegaQC API. If authentication is required
for submission (recommended), each user will need to set their username and
a authentication token.
