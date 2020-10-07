import subprocess
from pathlib import Path

import requests


def test_compose(multiqc_data):
    # Start the stack
    deploy = (Path(__file__).parent.parent / "deployment").resolve()
    subprocess.run(["docker-compose", "up"], cwd=deploy)

    # Create a user
    requests.post("localhost/users", json={"username": "foo", "email": "foo@bar.com"})

    # Upload the report
    requests.post(url="localhost/uploads", files={"report": multiqc_data})

    # Request the report back
    result = requests.get(url="localhost/uploads").json()
