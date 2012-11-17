#!/usr/bin/python3
# -*- coding: utf-8 -*-
import pymysql as mdb
import sys
import moviedb

try:
    moviedb.open()
    dvd_id = moviedb.input_one_dvd_movie ()
    moviedb.close_dvd (dvd_id)
    moviedb.close_database ()
except mdb.Error as e:
    print (e)
    sys.exit(1)
except:
    moviedb.abort_database ()
    raise
