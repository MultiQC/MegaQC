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

from logger import get_logger


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


def create_multiqc_cfg(token):
    """
    Creates required multiqc_config.yaml file with given token, required to
    run megaqc upload command.
    """
    with open("/app/megaqc/multiqc_config.yaml") as fh:
        fh.write(f"megaqc_url: {os.environ.get('MEGAQC_URL')}\n")
        fh.write(f"megaqc_access_token: {token}")


def gather_mega_tokens():
    """
    Multiple auth tokens are stored in the config prefixed with MEGA_TOKEN_,
    gather all these into a dict to know which sequencer 'user' to attribute
    to upload to for filtering later by the key being in the run name

    Returns: tokens (dict): dict of all sequencers to tokens
    """
    tokens = {}
    for key, val in os.environ.items():
        if key.startswith("MEGAQC_TOKEN_"):
            tokens[key.replace("MEGAQC_TOKEN_", "")] = val

    return tokens


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
    if proc.stdout:
        LOG.info(proc.stdout.decode())
    if proc.stderr:
        LOG.error(proc.stderr.decode())

    if proc.returncode != 0:
        # error running megaqc upload, stop and notify via slack
        message = (
            f"Error running megaqc upload.\n Error code: {proc.returncode}"
            f"\nError: {proc.stderr.decode()}"
        )
        LOG.error(message)
        slack_notify(f"{message}", 'egg-alerts')
        sys.exit()
    else:
        # successfully uploaded
        LOG.info(f"Successfully uploaded {file} to megaqc database")


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
        # log file hasn't been created, make one
        print("Creating new megaqc full log")
        Path(os.environ['MEGAQC_FULL_LOG']).parent.mkdir(parents=True, exist_ok=True)
        open(os.environ['MEGAQC_FULL_LOG'], 'a').close()

    global LOG
    LOG = get_logger("main_log")

    # create download dir if doesn't exist already
    Path(os.environ['DOWNLOAD_DIR']).mkdir(parents=True, exist_ok=True)

    # authenticate with DNAnexus
    dx_login()

    # get all megaqc auth tokens from environment to attribute upload to
    # correct sequencer
    tokens = gather_mega_tokens()

    # find multiqc_data.jsons in 002 projects
    projects = find_002_projects()
    jsons = find_jsons()
    filtered_jsons = filter_jsons(projects, jsons)

    LOG.info(f"{len(filtered_jsons)} total JSON files in 002 projects")

    # generate list of downloaded JSONs to add to log file
    downloaded = []

    for json_file, run in filtered_jsons.items():
        if run not in " ".join(log_file) and run not in downloaded:
            # run name not logged or just downloaded => download
            get_json(json_file, run)
            downloaded.append(run)
            print(f"Downloaded {json_file} ({run})")
            LOG.info(f"Downloaded {json_file} ({run})")
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
            if os.path.getsize(file):
                # select token to the sequencer and upload, if no token for
                # sequencer drop back to admin token
                try:
                    # Illumina sequencers put ID as 2nd field, plus our 002 prefix
                    sequencer = file.split("_")[2]
                    seq_token = tokens[sequencer]
                except KeyError:
                    LOG.error(
                        f"Couldn't find auth token from config for sequencer "
                        f"{sequencer} from run {file}. Will use admin token."
                    )
                    seq_token = tokens["ADMIN"]

                # write multiqc config with correct token and upload
                create_multiqc_cfg(tokenn=seq_token)
                upload_json(file)

                fh.write(f'{file}\n')
                LOG.info(f"{file} imported to database")
            else:
                # file appears to be empty, notify and log
                message = (
                    f"megaqc upload error: {Path(file).name} appears to be an "
                    f"empty file and can't be imported\nCheck logs for details"
                )
                slack_notify(message, channel='egg-alerts')
                LOG.error(message)
                fh.write(f'{file}\n')  # adding to upload log to not pick it up again

        os.remove(file)
        LOG.info(f"Deleted file: {file}")


if __name__ == "__main__":
    main()
