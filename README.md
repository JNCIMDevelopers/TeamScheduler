# TeamScheduler
A program that builds a schedule for the JNCIM worship and sunday school ministries.


## Table of Contents
* [Role Assignment](#role-assignment)
* [Assignment Eligibility Criteria](#assignment-eligibility-criteria)
* [Roles Priority](#roles-priority)
* [Special Considerations](#special-considerations)

--

## Role Assignment
Each role is assigned randomly while considering only from the eligible persons based on the Assignment Eligibility Criteria.

## Assignment Eligibility Criteria
- No more than 1 person assigned to each role
- No more than 1 role assigned to each person
- A person can't be assigned to a role not specified in their list of capable roles
- A person on-leave cannot be assigned
- A person can't be assigned more than 3 sundays in a row
- A person can't be assigned on a blockout date
- A person can't be assigned on a preaching date
- A person can't be assigned the same role 3 consecutive weeks to allow for rotation among team
- A person can't be assigned to a Worship Leader role if:
    - They are preaching within the next 2 Sundays
    - They were assigned to that role within the last 4 weeks
    - They are teaching the youth the same week
- A person can't be assigned to a Sunday School Teacher role for 2 consecutive weeks to allow for rotation among team

**NOTE:** There could be additional custom conditions.

## Roles Priority
- WORSHIP LEADER
- EMCEE
- ACOUSTIC GUITAR
- KEYS
- DRUMS
- BASS
- AUDIO
- LIVE
- LYRICS
- SUNDAY SCHOOL TEACHER
- BACKUP
- ELECTRIC GUITAR

## Special Considerations
There are cases where no one is available for a role (ex. Worship Leader)
- Manual triage is required to shuffle the assignments.
- This may cause the revised schedule to break at least one of the assignment eligiblity criterias.

## Setup Instructions
Make sure you're using `Python 3.12`

Clone this repo:
```sh
git clone https://github.com/JNCIMDevelopers/TeamScheduler.git
```
CD into the project:
```sh
cd TeamScheduler
```
Setup virtual environment:
```sh
python -m venv venv
```
Activate your virtual environment:
```sh
# Linux and MacOS:
source venv/bin/activate

# Windows
.\venv\Scripts\activate
```
Install required packages:
```sh
pip install -r requirements.txt
```

Make sure you have the following files in the root directory:
- team.json
- preaching.json
- rotation.json

## Execution Instructions
To run the program:
```sh
python main.py
```
To run the tests:
```sh
python -m pytest
```