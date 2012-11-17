#!/usr/bin/python3
# -*- coding: utf-8 -*-
import pymysql as mdb
import sys
import moviedb

try:
    moviedb.open ()
    dvd_id = None
    while dvd_id == None:
        dvd_id_string = input ("DVD ID for a DVD to add movies to: ");
        if str.isdigit (dvd_id_string):
            dvd_id = int (dvd_id_string)
    moviedb.display_dvd (dvd_id)
#    moviedb.preload_movie_values ()
    movie_id = -1
    while True:
        movie_id = moviedb.input_one_show (dvd_id)
        if movie_id == None:
           break 
        moviedb.display_movie (movie_id)
        moviedb.commit_data ()
            
#    moviedb.close_dvd (dvd_id)
    moviedb.close_database ()
except mdb.Error as e:
    print (e)
    sys.exit(1)
except:
    moviedb.abort_database ()
    raise
