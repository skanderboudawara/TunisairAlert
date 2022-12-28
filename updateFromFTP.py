#!/usr/bin/python3
import ftplib
from utils.pillow_reports import generate_report
from utils.sql_func import clean_sql_table
from utils.utility import TimeAttribute, FileFolderManager


def import_ftp_sqldb():
    """_summary_
    To pull the SQL Table from the FTP servera
    Credentials are saved in /credentials/ftp.json
    """
    ftp_json = FileFolderManager(directory="credentials", name_file="ftp.json").read_json()
    path = ftp_json["path"]
    filename = ftp_json["file_name"]
    PATH_SQL_DB = FileFolderManager(directory="datasets/SQL table", name_file="tunisair_delay.db").file_dir
    ftp = ftplib.FTP(ftp_json["ip_adress"])
    ftp.login(ftp_json["login"], ftp_json["password"])
    ftp.cwd(path)
    ftp.retrbinary(f"RETR {filename}", open(PATH_SQL_DB, "wb").write)
    ftp.quit()

    print("FTP DB imported")


if __name__ == "__main__":
    """_summary_
    Pull the new SQL table from the FTP server
    Clean tables of today and yesterday
    Generate report of today and yesterday
    """
    TODAY_DATE = TimeAttribute().today
    YESTERDAY_DATE = TimeAttribute().yesterday

    import_ftp_sqldb()

    clean_sql_table(TODAY_DATE)
    clean_sql_table(YESTERDAY_DATE)

    generate_report(TODAY_DATE)
    generate_report(YESTERDAY_DATE)
