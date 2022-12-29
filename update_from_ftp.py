#!/usr/bin/python3
import ftplib
from src.pillow_reports import generate_report
from src.sql_func import SqlManager
from src.utils import TimeAttribute, FileFolderManager, get_env


def import_ftp_sqldb():
    """
    To pull the SQL Table from the FTP servera
    Credentials are saved in /credentials/ftp.json
    """
    path = get_env("path")
    filename = get_env("file_name")
    PATH_SQL_DB = FileFolderManager(directory="datasets/SQL table", name_file=filename).file_dir
    ftp = ftplib.FTP(get_env("ip_adress"))
    ftp.login(get_env("login"), get_env("password"))
    ftp.cwd(path)
    ftp.retrbinary(f"RETR {filename}", open(PATH_SQL_DB, "wb").write)
    ftp.quit()

    print("FTP DB imported")


if __name__ == "__main__":
    """
    Pull the new SQL table from the FTP server
    Clean tables of today and yesterday
    Generate report of today and yesterday
    """
    date_attr = TimeAttribute()
    TODAY_DATE = date_attr.today
    YESTERDAY_DATE = date_attr.yesterday

    import_ftp_sqldb()

    sql_table = SqlManager()
    sql_table.clean_sql_table(TODAY_DATE)
    sql_table.clean_sql_table(YESTERDAY_DATE)

    generate_report(TODAY_DATE)
    generate_report(YESTERDAY_DATE)
