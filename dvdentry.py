#!/usr/bin/python3
# -*- coding: utf-8 -*-
import mysql as mdb
import sys
import moviedb

try:
    moviedb.open ()
    dvd_id = moviedb.new_dvd ()
    moviedb.preload_movie_values ()
    movie_id = 0
    while not movie_id == None:
        movie_id = moviedb.input_one_movie (dvd_id)
    moviedb.close_dvd (dvd_id)
    moviedb.close_database ()
except mdb.connector.Error as e:
    print (e)
    sys.exit(1)
except:
    moviedb.abort_database ()
    raise
