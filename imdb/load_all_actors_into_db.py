#!/usr/bin/python3.3
import gzip
import pickle
import pymysql as mdb

con = None
cur = None

def open ():
    '''Open the database connection'''
    global con, cur
    con = mdb.connect('localhost', 'dvdeug', '', 'DVDs', use_unicode=True, charset="utf8")
    cur = con.cursor()
    cur.execute ("SET NAMES 'utf8'")

def movie_actor_insert (movie_id, name, years):
    possible_matches = []
    movie = name
    if movie in movie_names:
        movie_list = movie_names [movie]
        # there's movies with variant forms and non-variant forms
        # delete non-variant forms and resolve not to trust variant forms
        delete_list = set ()
        for i in movie_list:
            for j in movie_list:
                if i != j and len (i) == 2 and (i[0], i[1]) == (j[0], j[1]):
                    delete_list.add (i)
        if len (delete_list) > 0:
            for i in delete_list:
                movie_list.remove (i)
        for n in movie_list:
            if n == (movie, years):
                possible_matches.append (n)
            elif (n[0], n[1]) == (movie, years):
                return;
    if len (possible_matches) > 1:
        print ("Multiple matches for movie_id {}, '{}'".format (movie_id, name))
        for p in possible_matches:
            print ("\t{}".format (p))
        return
    elif len (possible_matches) == 0:
        print ("No data for movie_id {}, '{}'".format (movie_id, name))
        return
    if possible_matches[0] in movie_actor:
        for actor in movie_actor[possible_matches[0]]:
            cur.execute ('INSERT INTO actor values ({}, "{}")'.format (con.escape(actor), movie_id))
    else:
        print ("No actors for movie_id {}, '{}'".format (movie_id, name))
    if possible_matches[0] in movie_director:
        for director in movie_director[possible_matches[0]]:
            cur.execute ('INSERT INTO director values ({}, "{}")'.format (con.escape(director), movie_id))
    else:
        print ("No directors for movie_id {}, '{}'".format (movie_id, name))     
    cur.execute ("INSERT INTO actors_imported values ({});".format (movie_id))

with gzip.open ("act_pickle.gz", "rb") as f:
#with gzip.open ("short_act_pickle.gz", "rb") as f:
    movie_names = pickle.load (f)
    movie_actor = pickle.load (f)
    movie_director = pickle.load (f)
open()
print ("done unpickling")
#cur.execute ("SELECT movie_id, imdb_name, year FROM film NATURAL JOIN movie "
#             "WHERE movie_id NOT IN (select actors_imported.movie_id FROM actors_imported) "
#             "UNION "
#             "SELECT movie_id, imdb_name, year FROM short NATURAL JOIN movie "
#             "WHERE movie_id NOT IN (select actors_imported.movie_id FROM actors_imported); ");
cur.execute ("SELECT movie_id, name, year FROM movie " 
             "WHERE movie_id NOT IN (select tv_show_old.movie_id FROM tv_show_old) "
            "AND movie_id NOT IN (select actors_imported.movie_id FROM actors_imported) "
            "AND movie_id NOT IN (select tv_show.movie_id FROM tv_show) "
            "ORDER BY movie_id;")
movies = cur.fetchall()

for m in movies:
    print (m)
    movie_actor_insert (m[0], m[1], str(m[2]))
con.commit()

               

