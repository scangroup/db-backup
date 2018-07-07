#!/usr/bin/env python3
import os
import time
import argparse


###########################################
### Configuration
###########################################

# MySQL Config File
mysql_config = "mysql-backup.cnf"

# Where to save backup file
dst_dir = "/var/scripts/db-backup/out"

###########################################
### END: Configuration
###########################################


# Command-Line Arguments
parser = argparse.ArgumentParser()
parser.add_argument("--datestamp", help="Add date stamp to backup filename.", action="store_true")
parser.add_argument("--datetimestamp", help="Add datetime stamp to backup filename.", action="store_true")
args = parser.parse_args()

# No date stamp - Default
filestamp = ''

# Datetime stamp (YYYY-MM-DD-HH-MM)
if args.datetimestamp:
    filestamp = "_" + time.strftime('%Y-%m-%d-%H%M')

# Date stamp (YYYY-MM-DD)
elif args.datestamp:
    filestamp = "_" + time.strftime('%Y-%m-%d')


# Get a list of databases :
database_list_command = "mysql --defaults-extra-file=%s --silent -N -e 'show databases'" % (mysql_config)
for database in os.popen(database_list_command).readlines():
    database = database.strip()
    if database == 'information_schema':
        continue
    if database == 'performance_schema':
        continue
    
    # Set Filename
    filename = "%s/%s%s.sql" % (dst_dir, database, filestamp)
    os.popen("mysqldump --defaults-extra-file=%s -e --opt -c %s | gzip -c > %s.gz" % (mysql_config, database, filename))

