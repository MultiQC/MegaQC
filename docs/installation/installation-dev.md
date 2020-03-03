# MegaQC installation: Development

## Prerequisites
You will need:
* [node](https://nodejs.org/en/download/)
* [Python 3](https://www.python.org/downloads/)

## 1. Clone the repo
If you're doing development work, you need access to the source code
```bash
git clone git@github.com:ewels/MegaQC.git
```

## 2. Install the Python into a virtual environment
You should do your development in a virtual environment. You also need to install MegaQC
and all its dependencies there:
```bash
cd MegaQC
python3 -m venv venv
source venv/bin/activate
pip install -e .[dev]
```

## 3. Enable development mode:
Setting this bash variable runs MegaQC in development mode. This means
that it will show full Python exception tracebacks in the web browser
as well as additional Flask plugins which help with debugging and performance testing.

```bash
export FLASK_DEBUG=1
```

## 4. Set up the database
Running this command creates an empty SQLite MegaQC database file in the
installation directory called `megaqc.db`

```bash
megaqc initdb
```

## 5. Start megaqc
Start MegaQC:
```bash
megaqc run
```

You will have to run the rest of these commands **in another terminal window**, because
`megaqc run` blocks the terminal.

## 6. Setup your access key
* Login to MegaQC in your browser by browsing to <http://localhost:5000/register/> (the port might differ, it will depend on what was output in the `megaqc run` stage previously
* Once registered, visit <http://localhost:5000/users/multiqc_config> and follow the instructions there to configure your access token in `~/.multiqc_config.yaml`.
* Note: if you you'd rather not pollute your home directory, you can instead name the file `multiqc_config.yaml` and place it in the current (MegaQC) directory. However, you will then have to run `megaqc upload` from that directory each time

## 7. Load test data
In order to develop new features you need some data to test it with:

```bash
git clone https://github.com/TMiguelT/1000gFastqc
for report in $(find 1000gFastqc -name '*.json')
    do megaqc upload $report
done
```

## 8. Install the JavaScript and start compiling
This command will run until you cancel it, but will ensure that any changes to the 
JavaScript are compiled instantly:
```bash
npm install
npm run watch
```


You should now have a fully functional MegaQC test server running,
accessible on your localhost at http://127.0.0.1:5000

Now, head over to the [development docs](../README.md#contributing) for a description of the 
project structure.
