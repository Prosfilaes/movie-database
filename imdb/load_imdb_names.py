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

def movie_imdb_name_insert (movie_id, names, years):
    possible_matches = []
    for movie in names:
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
#    print (possible_matches)
    if len (possible_matches) > 1:
        print ("Multiple matches for movie_id {}, '{}'".format (movie_id, names[0]))
        for p in possible_matches:
            print ("\t{}".format (p))
        return
    elif len (possible_matches) == 0:
        print ("No match found for movie_id {}, '{}'".format (movie_id, names[0]))
        return
    cur.execute ('SELECT is_full_length FROM movie WHERE movie_id = {};'.format (movie_id))
    ifl = cur.fetchone()[0]
    if ifl == 1:
        cur.execute ('INSERT INTO film VALUES ({}, {});'.format (movie_id, con.escape (possible_matches[0][0])))
    elif ifl == 0:
        cur.execute ('INSERT INTO short VALUES ({}, {});'.format (movie_id, con.escape (possible_matches[0][0])))
    else:
        print ("Invalid values for ifl on movie_id {}: {}".format(movie_id, ifl));
    return;

with gzip.open ("act_pickle.gz", "rb") as f:
#with gzip.open ("short_act_pickle.gz", "rb") as f:
    movie_names = pickle.load (f)
    movie_actor = pickle.load (f)
    movie_director = pickle.load (f)
open()
cur.execute ("SELECT movie_id, name, year FROM movie " 
             "WHERE movie_id NOT IN (select tv_show_old.movie_id FROM tv_show_old) "
             "AND movie_id NOT IN (select film.movie_id FROM film) "
             "AND movie_id NOT IN (select short.movie_id FROM short) "
#             "WHERE movie_id NOT IN (select actors_imported.movie_id FROM actors_imported) "
             "ORDER BY movie_id;")
movies = cur.fetchall()

for m in movies:
    cur.execute ("SELECT amn.name FROM alternate_movie_names amn WHERE amn.movie_id = {};".format (m[0]))
    amn = cur.fetchall()
    mnames = [m[1]]
    if len (amn) > 0:
        mnames.extend([a[0] for a in amn])
    movie_imdb_name_insert (m[0], mnames, str(m[2]))
con.commit()
