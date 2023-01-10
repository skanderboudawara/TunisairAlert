"""
Pull the new SQL table from the FTP server
Clean tables of today and yesterday
Generate report of today and yesterday
"""
#!/usr/bin/python3
from data_analysis.pillow_reports import generate_report
from data_pipeline.sql_functions import SqlManager
from src.utils import TimeAttribute

if __name__ == "__main__":

    date_attr = TimeAttribute()
    TODAY_DATE = date_attr.today
    YESTERDAY_DATE = date_attr.yesterday

    sql_table = SqlManager()

    sql_table.import_ftp_sqldb()
    sql_table.clean_sql_table(TODAY_DATE)
    sql_table.clean_sql_table(YESTERDAY_DATE)

    generate_report(TODAY_DATE)
    generate_report(YESTERDAY_DATE)
