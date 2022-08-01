import ftplib
import os
from datetime import datetime, timedelta
import pytz
from utils.pillow_reports import generate_report
from utils.sql_func import clean_sql_table

TZ = "Africa/Tunis"
TODAY_DATE = datetime.now().astimezone(pytz.timezone(TZ))
YESTERDAY_DATE = (datetime.now() - timedelta(days=1)).astimezone(pytz.timezone(TZ))


def import_ftp_sqldb():
    path = "/mnt/applications/iocage/jails/tunisairalert/root/root/datasets/SQL table/"
    filename = "tunisair_delay.db"
    PATH_SQL_DB = os.path.join(
        os.path.abspath(os.curdir), "datasets/SQL table/tunisair_delay.db"
    )
    ftp = ftplib.FTP("192.168.1.200")
    ftp.login("root", "hkZ1M!^5ta")
    ftp.cwd(path)
    ftp.retrbinary("RETR " + filename, open(PATH_SQL_DB, "wb").write)
    ftp.quit()
    print("FTP DB imported")


if __name__ == "__main__":
    # import_ftp_sqldb()

    # clean_sql_table(TODAY_DATE)
    # clean_sql_table(YESTERDAY_DATE)

    generate_report(TODAY_DATE)
    generate_report(YESTERDAY_DATE)
