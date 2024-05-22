# call-scheduler
Specialized on-call scheduler for UOttawa Ophthalmology 

Requires Python >= 3.9

## What this tool does
This tool makes a call-schedule for the year starting July 1, 2024 to June 30, 2025. We are scheduling based on the following rules:

1. There is always 1 jr resident and 1 sr resident on call I.e pool of 7 sr residents (year 4 and 5) and 6 jr residents (year 2 and 3) .
2. During week days residents cannot be scheduled on consecutive days (exception Friday)
3. Friday, Saturday, and Sunday are consecutive call days
4. Residents cannot work 2 consecutive weekends (friday, sat, sunday as above)
5. During the first month ideally year 2nd year residents are not scheduled on weekends
6. Residents cannot be scheduled during vacation dates or no call request weekends
7. Residents cannot be scheduled for more than 9 calls a month (fri,sat,sun counts as 3)
8. Jr residents should do fairly equal call amongst each other
9. Sr. Residents should do fairly equal call amongst each other
10. Long weekends are pre-assigned (4 day consecutive usually, ~with Exceptions for easter long weekend~). These include: Canada day long weekend (mon included), civic (during 3 week summer exception see below), labour day long (mon included), thanksgiving (mon included), remembrance day (mon included), family day (mon included), easter long (friday and Mon included, 1 person scheduled thurs-sat, 1 sun-mon), Victoria day (mon included)
11. Exceptions:
  - ~3 weeks during July and August, Jr call schedule will remain following the above rules, however, Sr call schedule will differ. Srs will take 3-4 consecutive days of call (i.e. from July 21-Aug 11). This may just need to be input manually~
  - ~3 weeks during Dec - Jan, Jr and Sr will be operating on a 3-5 day consecutive schedule over this period~
  - During the 2nd half of the year (starting in Feb - July), year 3 junior residents can take jr or sr call, and year 5 residents will not be included in scheduling for a 3 month period. When jr residents take sr call (and keep taking jr call), they cannot work 2 consecutive call days as either sr or jr.

**Note: this tool does not accommodate for splitting up Easter long weekend or Exceptions 11.a and 11.b**

## Setup

These setup instructions are for Macs.

### Check Python installation

1. Open up the Terminal (cmd + space, type in terminal)
2. Check what version of Python is currently the default on your machine
```
$ python3 --version
Python 3.11.6
```
3. If it is less than Python 3.9, you will need to install it either from [Python's website](https://www.python.org/downloads/macos/), or via [homebrew](https://docs.brew.sh/Homebrew-and-Python).

### Setup before running this tool

1. Clone this repository to your local machine. If downloading the zip, unzip it
2. Change to the dir
```
$ cd <path>/call-scheduler
```
3. Install `virtualenv`
```
$ pip install virtualenv
```
4. Create and activate a virtualenv
```
$ python3 -m venv venv
$ source ./venv/bin/activate
```
5. Install the requirements into your virtualenv
```
./venv/bin/python -m pip install -r requirements.txt
```

### Using this tool

1. Configure the resident YAML files in the `residents/` folder. There is a template there, feel free to copy it and be sure to provide a `name`, `year` and `vacation_days`.
```
name: Vicky CantCode
year: 2
vacation_days:
  - 2024-01-01
  - 2024-01-02
  - 2024-01-03
  - 2024-01-04
  - 2024-01-05
```
2. Double check the `hospital_information.yaml` file. This is already pre-configured with long-weekend days, but double check these
3. Run the tool (the tool is hard-coded to create a schedule for July 1st, 2024 to June 30, 2025)
```
$ .venv/bin/python runner.py
```

#### TODO: currently this program outputs the date and call-assignments to console. Will configure this to output to a .csv file later (i.e. so you can import into Excel or Google Sheets)
