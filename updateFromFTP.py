import ftplib
import os
from datetime import datetime, timedelta
import pytz
from utils.pillow_reports import generateReport
from utils.sql_func import clean_SQL_table
import time

tz = "Africa/Tunis"
current_time = datetime.now().astimezone(pytz.timezone(tz))


def importFTP_db():
    path = "/mnt/applications/iocage/jails/tunisairalert/root/root/datasets/SQL table/"
    filename = "tunisair_delay.db"
    sql_table_loc = os.path.join(
        os.path.abspath(os.curdir), "datasets/SQL table/tunisair_delay.db"
    )
    ftp = ftplib.FTP("192.168.1.200")
    ftp.login("root", "hkZ1M!^5ta")
    ftp.cwd(path)
    ftp.retrbinary("RETR " + filename, open(sql_table_loc, "wb").write)
    ftp.quit()
    print("FTP DB imported")


if __name__ == "__main__":
    importFTP_db()
    clean_SQL_table(current_time)
    yesterday = (datetime.now() - timedelta(days=1)).astimezone(
        pytz.timezone(tz)
    )  # To be used for yesterday
    clean_SQL_table(yesterday)

    generateReport(current_time)
    generateReport(yesterday)
