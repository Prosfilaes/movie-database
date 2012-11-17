#!/usr/bin/python3
# -*- coding: utf-8 -*-
import pymysql as mdb
import sys
import moviedb

try:
    moviedb.open ()
    dvd_id = None
    while dvd_id == None:
        dvd_id_string = input ("DVD ID for a DVD to add shows to: ");
        if str.isdigit (dvd_id_string):
            dvd_id = int (dvd_id_string)
    moviedb.display_dvd (dvd_id)
    moviedb.add_new_tvshow ()
    moviedb.preload_movie_values ()
    moviedb.input_one_show (dvd_id)
    moviedb.close_dvd (dvd_id)
    moviedb.close_database ()
except mdb.Error as e:
    print (e)
    sys.exit(1)
except:
    moviedb.abort_database ()
    raise
