#!/usr/bin/python3
# -*- coding: utf-8 -*-
import pymysql as mdb
import sys
import moviedb

try:
    moviedb.open ()
    moviedb.display_movie (429)
    moviedb.close_database ()
except mdb.Error as e:
    print (e)
    sys.exit(1)
except:
    moviedb.abort_database ()
    raise
