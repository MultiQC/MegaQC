import subprocess
import time
from pathlib import Path

import pytest
import requests


def raise_response(resp):
    if not str(resp.status_code).startswith("2"):
        raise Exception(
            "Request failed with status {} and body{}".format(
                resp.status_code, resp.text
            )
        )


@pytest.fixture(scope="module")
def compose_stack():
    deploy = (Path(__file__).parent.parent / "deployment").resolve()
    # Start the stack, and wait for it to start up
    subprocess.run(["docker-compose", "up", "-d"], cwd=deploy, check=True)
    time.sleep(15)
    yield
    # When we're done, stop the stack and cleanup the volumes
    subprocess.run(["docker-compose", "down", "-v"], cwd=deploy, check=True)


def test_docker():
    root = (Path(__file__).parent.parent).resolve()
    subprocess.run(["docker", "build", str(root)], check=True)


def test_compose(multiqc_data, compose_stack):
    # Initially we should have no reports
    result = requests.get(url="http://localhost/rest_api/v1/uploads")
    raise_response(result)
    assert len(result.json()["data"]) == 0

    # Create a user
    user = requests.post(
        "http://localhost/rest_api/v1/users",
        json={
            "data": {
                "type": "users",
                "attributes": {
                    "username": "foo",
                    "email": "foo@bar.com",
                    "password": "bar",
                },
            }
        },
    )
    raise_response(user)

    user.raise_for_status()
    token = user.json()["data"]["attributes"]["api_token"]

    # Upload the report
    report = requests.post(
        url="http://localhost/rest_api/v1/uploads",
        files={"report": multiqc_data},
        headers={"access_token": token},
    )
    raise_response(report)
    report.raise_for_status()

    # Finally, we should have 1 report
    result = requests.get(url="http://localhost/rest_api/v1/uploads")
    raise_response(result)
    assert len(result.json()["data"]) == 1
