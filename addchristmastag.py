#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pymysql as mdb
import sys
import readline

con = None

try:

    con = mdb.connect('localhost', 'dvdeug', '', 'DVDs', use_unicode=True, charset="utf8")
    cur = con.cursor()
    cur.execute ("SET NAMES 'utf8'")

    cur.execute ("SELECT dvd_contents.movie_id FROM dvd_contents "
                 "WHERE dvd_contents.dvd_id in (99, 109, 101);")
    xmas_movies = cur.fetchall ()
#    xmas_movies = ((169,),)
    for xmovie in xmas_movies:
        print (xmovie)
        cur.execute ("Insert into tags (movie_id, tag) VALUES ({}, \"classic animation\")".format (xmovie[0]));

    con.commit ()
    
except mdb.Error as e:
  
    print (e)
    sys.exit(1)
    
finally:    
        
    if con:
        con.rollback ()
        con.close()

