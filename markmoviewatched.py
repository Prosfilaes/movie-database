#!/usr/bin/python3
# -*- coding: utf-8 -*-
import pymysql as mdb
import sys
import moviedb

try:
    moviedb.open ()
    movie_id = -1
    while movie_id == -1:
        movie_id = moviedb.get_movie_id ()
    moviedb.markwatched (movie_id)
    moviedb.close_database ()
except mdb.Error as e:
    print (e)
    sys.exit(1)
except:
    moviedb.abort_database ()
    raise
