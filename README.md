# Blockapp

Blockapp blocks the apps you can't stop opening, on Windows.

- Pick the apps that steal your time
- Schedule focus sessions that lock them
- Get a Focus Score that shows how distracted you really are

## Status

Step 1 of 4 is done: the project skeleton. Blocking, scheduling and the Focus Score come next.

## Setup (Windows)

You need Python 3.10 or newer from [python.org](https://www.python.org/downloads/).
Everything installs into a local `.venv` folder inside the project, so it's easy to delete later.

```powershell
git clone --depth 1 https://github.com/gaurijain21/blockapp
cd blockapp
python -m venv .venv
.venv\Scripts\activate
pip install --no-cache-dir -r requirements.txt
python -m blockapp
```

`--depth 1` and `--no-cache-dir` keep the download and pip's cache small, which helps on a laptop that's short on storage.

## Running tests

```powershell
pip install --no-cache-dir pytest
python -m pytest
```
