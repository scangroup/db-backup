#!/usr/bin/env python3
import os
import sys
import subprocess
import time
import argparse
import errno




########################################################################################################
### Configuration
########################################################################################################


# MySQL Config File
mysql_config = "/etc/mysql/debian.cnf"

# Base directory to save backups to
dst_base_dir = "./backups"


########################################################################################################
### END: Configuration
########################################################################################################




# Command-Line Arguments
########################################################################################################
parser = argparse.ArgumentParser()
parser.add_argument("--hourly", help="(int) Store file in 'hourly' directory and add hour to filename.  Specify number of backups to keep.", type=int)
parser.add_argument("--daily", help="(int) Store file in 'daily' directory and add day of month to filename.  Specify number of backups to keep.", type=int)
parser.add_argument("--weekly", help="(int) Store file in 'weekly' directory and add day of week abbrev name to filename.  Specify number of backups to keep.", type=int)
parser.add_argument("--monthly", help="(int) Store file in 'monthly' directory and add day of month to filename.  Specify number of backups to keep.", type=int)
parser.add_argument("--notimestamp", help="(boolean) Don't add full date/time stamp to filename", action="store_true")
args = parser.parse_args()


# ------------------------------------------------------------------------------------------------------
# --hourly, --daily, --weekly, --monthly & <none> options are exclusive. Only one may be specified.
# --datestamp can be specified with any other option.
# ------------------------------------------------------------------------------------------------------


# Hourly Backup
# ------------------------------------------------------------------------------------------------------
if args.hourly:
    backup_type = '.hourly'
    files_to_keep = args.hourly

# Daily Backup
# ------------------------------------------------------------------------------------------------------
elif args.daily:
    backup_type = '.daily'
    files_to_keep = args.daily

# Weekly Backup
# ------------------------------------------------------------------------------------------------------
elif args.weekly:
    backup_type = '.weekly'
    files_to_keep = args.weekly

# Monthly Backup
# ------------------------------------------------------------------------------------------------------
elif args.monthly:
    backup_type = '.monthly'
    files_to_keep = args.monthly

# Error
# --------------------------------------------------------------
else:
    sys.exit('Error: You must specify one of --hourly, --daily, --weekly, --monthly')


# Add Date/Time Stamp to filename
# ------------------------------------------------------------------------------------------------------
if args.notimestamp:
    datestamp = ""
else:
    datestamp = "." + time.strftime('%Y-%m-%d_%H%M')




# Backup each Database
########################################################################################################
database_list_command = "mysql --defaults-extra-file=%s --silent -N -e 'show databases'" % (mysql_config)
for database in os.popen(database_list_command).readlines():
    database = database.strip()
    if database == 'information_schema':
        continue
    if database == 'performance_schema':
        continue
    if database == 'sys':
        continue


    # Set Backup Path & Filename
    # --------------------------------------------------------------------------------------------------
    db_dst_path = "%s/%s" % (dst_base_dir, database)
    filename = "%s/%s%s%s.sql.gz" % (db_dst_path, database, backup_type, datestamp)


    # Check if output Path Exists, otherwise try to create it
    # --------------------------------------------------------------------------------------------------
    if not os.path.exists(db_dst_path):
        try:
            os.makedirs(db_dst_path)
            os.chmod(db_dst_path, 0o777)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise


    # Dump DB & CHMOD File
    # --------------------------------------------------------------------------------------------------
    dump_cmd = "mysqldump --defaults-extra-file=%s -e --opt -c %s | gzip -c > %s && chmod 0777 %s" % (mysql_config, database, filename, filename)
    subprocess.run(dump_cmd, shell=True, check=True) # Waits for cmd to finish, popen() does not


    # Cleanup Old Files
    # https://stackoverflow.com/questions/25785/delete-all-but-the-most-recent-x-files-in-bash
    # --------------------------------------------------------------------------------------------------
    if files_to_keep > 0 and not args.notimestamp:
        search_path = "%s/%s%s.*.sql.gz" % (db_dst_path, database, backup_type)
        os.popen("ls -tp %s | grep -v '/$' | tail -n +%d | xargs -I {} rm -- {}" % (search_path, (files_to_keep + 1)))

