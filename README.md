# Blockapp

Blockapp blocks the apps you can't stop opening, on Windows.

- Pick the apps that steal your time
- Schedule focus sessions that lock them
- Get a Focus Score that shows how distracted you really are

## Status

All 4 steps are done: app blocking, scheduled focus sessions and the Focus Score. An iPhone version is planned next.

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

## Scheduled focus sessions

```powershell
python -m blockapp schedule add --days weekdays --start 09:00 --end 12:00
python -m blockapp schedule add --days mon,wed --start 19:00 --end 21:00
python -m blockapp schedule list
python -m blockapp schedule remove 2
python -m blockapp run           # follows your schedules while this window is open
python -m blockapp startup on    # or: start quietly in the background every time you sign in
python -m blockapp skip          # end the current session early
```

`--days` takes `weekdays`, `weekends`, `everyday`, a range like `mon-fri`, or a list like `mon,wed,fri`. Times are 24-hour. Windows that cross midnight (like `22:00` to `06:00`) work too.
Changes to your block list or schedules apply right away, with no restart needed. `startup off` turns automatic start off again.

## Focus Score

```powershell
python -m blockapp score            # today's score and what cost you points
python -m blockapp score --days 7   # your last week
```

Every day starts at 100. You lose points for:

- each time you open a blocked app during a focus session: 5 points (up to 40)
- each session you end early with `skip`: 10 points (up to 20)
- each minute you spend in your distracting apps outside sessions: 0.5 points (up to 40)

Distracted time is counted while `blockapp run` (or `startup on`) is running, using the app in the front window.

## Dashboard

```powershell
python -m blockapp dashboard
```

This opens http://localhost:8765 in your browser. There you can start a 25, 50 or 90 minute focus session right away, see your Focus Score and the last 7 days, block and unblock apps, add or remove focus sessions, and end a session early.
While the dashboard is open, it also follows your schedules, so you don't need `run` as well. It only uses Python's standard library, so it doesn't install anything extra.
