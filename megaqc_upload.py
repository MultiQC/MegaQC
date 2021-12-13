"""
Script to download all multiqc_data.jsons from 002 projects in DNAnexus, then
runs megaqc upload to import into megaqc database

Writes runs downloaded to log file to ensure they aren't downloaded twice

Required env variables:
- DOWNLOAD_DIR: dir to download jsons to
- SLACK_TOKEN: slack api token to send notifications
- AUTH_TOKEN: DNAnexus authorisation token
- MEGAQC_FULL_LOG: verbose log file to write all running messages to
- MEGAQC_UPLOAD_LOG: file to write imported runs to, used to record whats uploaded
"""
import os
from pathlib import Path
import requests
import subprocess
import sys

import dxpy as dx

from logger import LOG_FILE, get_logger


def dx_login():

    """
    dxpy login user for dxpy function either by .env file or docker env

    Returns: None

    Raises: dx.exceptions.InvalidAuthentication - raised if token is invalid
    """

    # try to get auth token from env (i.e. run in docker)
    try:
        AUTH_TOKEN = os.environ["AUTH_TOKEN"]
    except Exception as e:
        LOG.error('No dnanexus auth token detected')
        slack_notify(
            "megaqc upload: Error: no dx auth token found", "egg-alerts"
        )
        LOG.info('----- Stopping script -----')
        sys.exit()

    # env variable for dx authentication
    DX_SECURITY_CONTEXT = {
        "auth_token_type": "Bearer",
        "auth_token": AUTH_TOKEN
    }

    # set token to env
    LOG.info('dxpy login initiated')
    dx.set_security_context(DX_SECURITY_CONTEXT)

    try:
        # test auth token is valid and user authorised
        dx.api.system_whoami()
    except dx.exceptions.InvalidAuthentication as e:
        LOG.error(f"DNAnexus token invalid: {e}")
        slack_notify(
            f"megaqc upload: Error DNAnexus token appears to be invalid:\n{e}",
            "egg-alerts"
        )


def create_multiqc_cfg():
    """
    Checks for presence of multiqc_config.yaml file, this contains the upload
    URL and token required for uploading data. We create it dynamically from
    env varibales if not already present to only need to pass one config file
    to docker image
    """
    if not os.path.isfile("/app/megaqc/multiqc_config.yaml"):
        if os.environ.get("MEGAQC_URL") and os.environ.get("MEGAQC_ACCESS_TOKEN"):
            with open("/app/megaqc/multiqc_config.yaml", "w") as fh:
                # no config file present but env variables set => create one
                fh.write(f"megaqc_url: {os.environ.get('MEGAQC_URL')}\n")
                fh.write(f"megaqc_access_token: {os.environ.get('MEGAQC_ACCESS_TOKEN')}")
                print("Created multiqc config yaml file")
                LOG.info(
                    "Created required multiqc config file in "
                    "/app/megaqc/multiqc_config.yaml"
                )
        else:
            # config file doesn't exist and env variables not set => exit
            LOG.error(
                f"No multiqc yaml config file present in megaqc dir and "
                "required env variables not set. This should contain the "
                "upload URL and access token. Exiting now."
            )


def find_002_projects():
    """
    Searches for all 002_ DNAnexus projects

    Returns dict of project-id: project-name
    """
    projects = dx.search.find_projects(
        name="002_*", describe=True, name_mode="glob"
    )
    projects = dict([
        (x["describe"]["id"], x["describe"]["name"]) for x in projects
    ])
    LOG.info(f'Found {len(projects)} 002 projects')

    return projects


def find_jsons():
    """
    Searches for all multiqc_data.json filesin any DNAnexus project

    Returns dict of project-id: file-id
    """
    jsons = dx.search.find_data_objects(
        name="multiqc_data.json", describe=True
    )
    jsons = dict([
        (x["describe"]["project"], x["describe"]["id"]) for x in jsons
    ])

    LOG.info(f"Found {len(jsons)} multiqc_data.json files")

    return jsons


def filter_jsons(projects, jsons):
    """
    Filter JSONs to only retain those in 002 projects

    Returns list of tuples as (file-id, json-name)
    """
    return dict([
        (jsons[x], projects[x]) for x in jsons if x in projects
    ])


def get_json(file_id, run_name):
    """
    Downloads given JSON to specified dir

    Returns: None
    """
    dx.bindings.dxfile_functions.download_dxfile(
        file_id, f"{os.environ['DOWNLOAD_DIR']}/{run_name}-multiqc_data.json"
    )


def upload_json(file):
    """
    Runs megaqc upload to import json to megaqc database

    Args: file (PosixPath): path to file to upload

    Returns: None
    """
    proc = subprocess.run(
        f"megaqc upload {file}", shell=True, stderr=subprocess.PIPE
    )

    if proc.returncode != 0:
        # error running megaqc upload, stop and notify via slack
        message = (
            f"Error running megaqc upload.\n Error code: {proc.returncode}"
            f"\nError: {proc.stderr}"
        )
        LOG.error(message)
        slack_notify(message, 'egg-alerts')
        sys.exit()
    else:
        # successfully uploaded, log and delete
        LOG.info(f"Successfully uploaded {file} to megaqc database")
        os.remove(file)
        LOG.info(f"Deleted file: {file}")


def slack_notify(message, channel):
    """
    Sends notification to slack, either to egg-alerts or egg-logs.
    Handles both error in http request and exceptions being raised

    Args:
        - message (str): message to send to Slack
        - channel (str): Slack channel to send to (egg-logs / egg-alerts)

    Returns: None
    """
    try:
        response = requests.post('https://slack.com/api/chat.postMessage', {
            'token': os.environ['SLACK_TOKEN'],
            'channel': f'#{channel}',
            'text': message
        }).json()

        if not response['ok']:
            LOG.error((
                f"Error sending POST reuqest to {channel}.\n"
                f"Original message: {message}"
            ))
            sys.exit()
    except Exception as e:
        LOG.error(f"Error in POST request to {channel}.\n{e}")
        sys.exit()


def main():

    if os.path.isfile(os.environ['MEGAQC_UPLOAD_LOG']):
        with open(os.environ['MEGAQC_UPLOAD_LOG']) as fh:
            # read in log file, used to check if a run has been prev uploaded
            log_file = fh.read().splitlines()
    else:
        # no log file, likely first time running
        # create new one and set to empty list => download everything
        print("Creating new megaqc upload log")
        Path(os.environ['MEGAQC_UPLOAD_LOG']).parent.mkdir(parents=True, exist_ok=True)
        open(os.environ['MEGAQC_UPLOAD_LOG'], 'a').close()
        log_file = []

    if not os.path.isfile(os.environ['MEGAQC_FULL_LOG']):
        # log file hasn't been create, make one
        print("Creating new megaqc full log")
        Path(os.environ['MEGAQC_FULL_LOG']).parent.mkdir(parents=True, exist_ok=True)
        open(os.environ['MEGAQC_FULL_LOG'], 'a').close()

    global LOG
    LOG = get_logger("main_log")

    # create download dir if doesn't exist already
    Path(os.environ['DOWNLOAD_DIR']).mkdir(parents=True, exist_ok=True)

    # authenticate with DNAnexus
    dx_login()

    # check for multiqc config, create if doesn't exist
    create_multiqc_cfg()

    # find multiqc_data.jsons in 002 projects
    projects = find_002_projects()
    jsons = find_jsons()
    filtered_jsons = filter_jsons(projects, jsons)

    LOG.info(f"{len(filtered_jsons)} total JSON files in 002 projects")

    # generate list of downloaded JSONs to add to log file
    downloaded = []

    count = 0

    for json_file, run in filtered_jsons.items():
        count+=1
        if run not in log_file or run not in downloaded:
            # run name not logged or just downloaded => download
            get_json(json_file, run)
            downloaded.append(run)
            print(f"Downloaded {json_file} ({run})")
            LOG.info(f"Downloaded {json_file} ({run})")
            if count == 5:
                break
        else:
            print(f"Run {run} already imported, skipping...")
            LOG.info(f"Run {run} already imported, skipping...")

    LOG.info(f"Downloaded {len(downloaded)} JSONs to import")

    # megaqc upload needs to be run from /app/megaqc
    os.chdir("/app/megaqc/")

    # import each file into database using megaqc upload, then delete files
    # write each run file imported to log
    with open(os.environ['MEGAQC_UPLOAD_LOG'], 'a') as fh:
        for file in Path(os.environ['DOWNLOAD_DIR']).glob('*.json'):
            upload_json(file)
            fh.write(f'{file}\n')
            LOG.info(f"{file} imported to database")

if __name__ == "__main__":
    main()
