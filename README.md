✈️ Tunisair airlines flight performance
============

This repository contains the data pipeline and analysis to generate a daily key performance indicator report on Tunisair flight delays.

The generated report target to illustrate the following:
- The count of departure delays that Tunisair has made
- The min, max, and average delays for departures and arrival  (in minutes) 
- A bar chart to compare performance between Tunisair, Nouvelair, Airfrance (& Transavia)
- The report will be published daily at 9 a.m _Europe/Paris timezone_ on the Twitter account [@Tunisairalert](https://twitter.com/Tunisairalert) 

![Tunisair alert report Preview](https://i.ibb.co/n0sgBB4/01-08-2022-report.png)

---
<!--Programming languages-->
<p>
  <br>
  <img alt="Python" src="https://img.shields.io/badge/python-306998.svg?style=for-the-badge&logo=python&logoColor=white"/>
  <img alt="PyTest" src="https://img.shields.io/badge/Pytest-0A9EDC.svg?style=for-the-badge&logo=Pytest&logoColor=white"/>
  <img alt="Pandas" src="https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white"/>
  <img alt="Matplotlib" src="https://img.shields.io/badge/Matplotlib-%23ffffff.svg?style=for-the-badge&logo=Matplotlib&logoColor=black"/>
  <img alt="SQLite" src="https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white"/>
  <img alt="Json" src="https://img.shields.io/badge/JSON-000000.svg?style=for-the-badge&logo=JSON&logoColor=white"/>
  <img alt="API" src="https://img.shields.io/badge/FastAPI-009688.svg?style=for-the-badge&logo=FastAPI&logoColor=white"/>
</p>

---

## Features
### Data ingestion
The tasks will be CRON TABBED each hour from 7. am to midnight.
- An API request will be performed on [Airlabs](https://airlabs.co/) API to get the data in JSON format
- The JSON data will be cleaned, and enriched then saved into `tunisair_delay.db` (Sqlite3)
- The airport data with be enriched with [pyairpots](https://github.com/NICTA/pyairports) module. Thanks to [NICTA](https://github.com/NICTA)

### Data Analysis
The tasks will be CRON TABBED every day at 9 a.m Paris/Timezone.
- A daily query will be performed on the SQL Table to create the needed plots using `Pandas` and `Matplotlib` frameworks
- Once the plots are ready, with `Pillow` package the daily report will be 
  
### Twitter posting
- Once the report generated a tweet will be posted on Tunisair performance

### Server Management
- Since the script will be hosted on a personal server using `FreeBSD`, a FTP script is made to update local `.db` data
- CRON JOB for `api_job.py`
`0 0,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23 * * * root python daily_cron.py`
- CRON JOB for `twitter_job.py`
`0 9 * * * root python twitter_job.py`

---
## Configuration
- You need to grab a Token from airlabs.co and past it into `.env` located in the root folder
- You also need to grab Twitter API codes [See tutorial](https://www.mattcrampton.com/blog/step_by_step_tutorial_to_post_to_twitter_using_python_part_two-posting_with_photos/) and past the information in `.env`

The `.env` file will loke like this
```
consumer_key=
consumer_secret=
access_token=
access_token_secret=
path=
file_name=tunisair_delay.db
ip_adress=
login=
password=U$
token_airlab=
```
---
## Folder Structure
```
📁|- data-analysis : containing all pandas, and matplotlib features
📁|- data-pipeline : containing the api requests, sql queries and the table.db
📁|- src : containing media, utils and consts
📁|- test : containing some function test
🐍.api_job.py : will be used daily for data scrapping
🐍.post_to_twitter.py : will be used daily to post on twitter
```
___
## Setup
- Install the packages in `requirements.txt`
- `api_job.py` is the module that will ingest the data from Airlabs API
- `twitter_job.py` is the module that will post the report on Twitter
___
## 📫 Contact me
<p>
<a href="https://www.linkedin.com/in/skanderboudawara/">
<img alt="LinkedIn" src="https://img.shields.io/badge/linkedin-%230077B5.svg?style=for-the-badge&logo=linkedin&logoColor=white"/>
</a> 
<br>
</p>
---

## License
>You can check out the full license [here](https://github.com/skanderboudawara/TunisairAlert/blob/master/LICENSE)

This project is open source and has no buisness intent.
