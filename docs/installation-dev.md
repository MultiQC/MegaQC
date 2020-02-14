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
pip install -e .
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

## 5. Load test data
In order to develop new features you need some data to test it with:

```
git clone https://github.com/TMiguelT/1000gFastqc
for report in $(find . -name '*.json')
    do megaqc upload $report
done
```

## 6. Install the JavaScript and start compiling
This command will run until you cancel it, but will ensure that any changes to the 
JavaScript are compiled instantly:
```bash
npm install
npm run watch
```

## 7. Start megaqc
In another terminal window, start MegaQC:
```bash
megaqc run
```

You should now have a fully functional MegaQC test server running,
accessible on your localhost at http://127.0.0.1:5000

Now, head over to the [development docs](development.md) for a description of the 
project structure.
