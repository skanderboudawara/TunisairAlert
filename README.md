Tunisair daily ingestion KPI
============

This tool is developed to create a daily ingest report of Tunisair flight performance. 
The report will show:
- Tunisair made how many arrival and departure delays
- The min, max, and average delays for departures and arrival
- A bar chart performance comparison between Tunisair, Nouvelair, Airfrance (& Transavia)
Once the daily report is generated, it will be published on the Twitter account [@Tunisairalert](https://twitter.com/Tunisairalert) at 9 a.m Europe/Paris timezone.

![Tunisair alert report Preview](https://i.ibb.co/n0sgBB4/01-08-2022-report.png)

---
## Check my linkedIn account

Whether you use this project, have learned something from it, or just like it, please consider endorsing me on linkedIN, so I can dedicate more time on open-source projects like this :)

👉 [LinkedIn](https://www.linkedin.com/in/skanderboudawara/)

---

## Features
- Grab the JSON data needed from the [Airlabs](https://airlabs.co/) API
- Save, clean and enrich the data into SQL Table (Sqlite3)
- Enrich airport name and country with [pyairpots](https://github.com/NICTA/pyairports) module. thanks to [NICTA](https://github.com/NICTA)
- Create the needed plots using pandas and matplotlib
- Generate the report via Pillow 
- The tasks will be CRON TABBED each hour from 7.am to midnight
- Each day at 9 a.m Paris/Timezone a tweet will be post on yesterday Tunisair performance

---
## Configuratin
- You need to grab a Token from airlabs.co and past it into `token.txt' located in the root folder
- You also need to grab Twitter API codes [See tutorial](https://www.mattcrampton.com/blog/step_by_step_tutorial_to_post_to_twitter_using_python_part_two-posting_with_photos/) and past the information in `credential.json` located in `root/pytwitter/`

---

## Setup
- `daily_cron.py` is the module that will ingest the data from Airlabs API
- `postToTwitter.py` is the module that will post the report on Twitter

---

## Usage
- CRON JOB for `daily_cron.py`
`0 0,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23 * * * root python daily_cron.py`
- CRON JOB for `postToTwitter.py`
`0 9 * * * root python postToTwitter.py`

---

## License
>You can check out the full license [here](https://github.com/skanderboudawara/TunisairAlert/blob/master/LICENSE)

This project is open source and has no buisness intent.

