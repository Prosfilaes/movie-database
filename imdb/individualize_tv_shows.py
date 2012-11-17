#!/usr/bin/python3.3
import gzip
import pickle
import pymysql as mdb
import moviedb

con = None
cur = None

def open ():
    '''Open the database connection'''
    global con, cur
    con = mdb.connect('localhost', 'dvdeug', '', 'DVDs', use_unicode=True, charset="utf8")
    cur = con.cursor()
    cur.execute ("SET NAMES 'utf8'")

def shows_display (name, season, have_watched, movie_id):
    # show_with_episodes format
    # (tv_show, year, version, (title, season, episode_num))
    if name in show_with_episodes:
        for i in show_with_episodes[name]:
            if i[3][1] != '' and int (i[3][1]) == season:
                print (i)
                full_name = '"' + name + '": ' + i[3][0]
                cur.execute ("INSERT INTO movie VALUES (NULL, {}, {}, 0, {}, {});".format (con.escape (full_name), i[1], have_watched, moviedb.mangle_name_for_sort (full_name)))
                new_id = con.insert_id ()
                cur.execute ("INSERT INTO tv_show VALUES ({}, {}, {}, {}, {});".format (new_id, con.escape (name), con.escape (i[3][0]), i[3][1], i[3][2]))
    return

with gzip.open ("show_pickle1.gz", "rb") as f:
#with gzip.open ("short_act_pickle.gz", "rb") as f:
    show_names = pickle.load (f)
    show_with_episodes = pickle.load (f)
    show_actor = pickle.load (f)
    show_director = pickle.load (f)
open()
cur.execute ("SELECT DISTINCT tv.name, season_num, have_watched, tv.movie_id FROM tv_show_old tv JOIN movie on movie.movie_id = tv.movie_id WHERE is_season = 1;")
shows = cur.fetchall()

for s in shows:
    shows_display (s[0], s[1], s[2], s[3])
con.commit()
