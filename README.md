# Blockapp

Blockapp blocks the apps you can't stop opening, on Windows.

- Pick the apps that steal your time
- Schedule focus sessions that lock them
- Get a Focus Score that shows how distracted you really are

## Status

Steps 1 and 2 of 4 are done: the project skeleton and app blocking. Scheduled focus sessions and the Focus Score come next.

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

## Blocking apps

```powershell
python -m blockapp running            # see what's open, to find app names
python -m blockapp add discord chrome # block apps (".exe" is optional)
python -m blockapp list               # your block list
python -m blockapp remove chrome      # unblock one
python -m blockapp block --minutes 25 # block for 25 minutes (leave out --minutes to block until Ctrl+C)
```

While blocking is on, Blockapp closes those apps within about a second of them opening, and keeps a record of each attempt for the Focus Score.
Windows system processes and your terminal can't be added, so you can't lock yourself out.
Settings and history live in `%APPDATA%\Blockapp`.
