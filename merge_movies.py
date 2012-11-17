#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pymysql as mdb
import sys
import readline

def yn_to_bool (s):
    '''Turn a string starting with y(j) or n into a boolean'''
    if s [0:1].lower() == "n":
        return False
    elif s [0:1].lower() == "y" or s[0:1].lower() == "j":
        return True
    return None

def get_movie_id (con, name):
    escaped_movie_name = con.escape (name)
    cur.execute ("SELECT * FROM movie WHERE movie.name = {};".format (escaped_movie_name))
    rows = cur.fetchall ()
    cur.execute ("SELECT m.movie_id, m.name, amn.name, m.year, m.is_full_length "
                 "FROM alternate_movie_names amn INNER JOIN movie m "
                 "ON amn.movie_id = m.movie_id "
                 "WHERE amn.name = {};".format (escaped_movie_name))
    rows += cur.fetchall ()
    if len (rows) == 0:
        cur.execute ("SELECT * FROM movie WHERE movie.name "
                     "LIKE CONCAT ('%', {}, '%');".format (escaped_movie_name))
        rows = cur.fetchall ()
        cur.execute ("SELECT m.movie_id, m.name, amn.name, m.year, m.is_full_length "
                     "FROM alternate_movie_names amn INNER JOIN movie m "
                     "ON amn.movie_id = m.movie_id "
                     "WHERE amn.name LIKE CONCAT ('%', {}, '%');".format (escaped_movie_name))
        rows += cur.fetchall ()

    if len (rows) == 0:
        print ("No matching entries. Please try again.")
        return
    elif len (rows) == 1:
        print (rows[0])
        is_existing_movie = None
        while is_existing_movie == None:
            is_existing_movie = yn_to_bool (input ("Is this your movie? (Y/N) "));
        if not is_existing_movie:
            return
        return rows [0][0];
    else:
        print ("We have matching entries. Are any of the following your movie?")
        for row in rows:
            print (row)
        is_existing_movie = None
        while is_existing_movie == None:
            is_existing_movie = yn_to_bool (input ("(Y/N): "));
        if not is_existing_movie:
            return;
        movie_id_str = ""
        while (not str.isdigit (movie_id_str)):
            movie_id_str = input ("Which id? ")
        return int (movie_id_str);

try:
    con = None
    cur_execute = print
    con = mdb.connect('localhost', 'dvdeug', '', 'DVDs', use_unicode=True, charset="utf8")
    cur = con.cursor()
    cur.execute ("SET NAMES 'utf8'")

    while True:
        movie_name = input ("Name of the movie, or hit enter to exit: ")
        if movie_name == "":
            sys.exit (0)
        movie_id = get_movie_id (con, movie_name)
        if movie_id is not None:
            break
    while True:
        movie2_name = input ("Name of entry to merge, or hit enter to exit: ")
        if movie2_name == "":
            sys.exit (0)
        movie2_id = get_movie_id (con, movie2_name)
        if movie2_id is not None:
            break
    
    # In order, replace entries in dvd_contents with movie1 then tags
    # then it should be safe to delete the entry
    cur.execute ("UPDATE dvd_contents dc SET dc.movie_id = {} "
                 "WHERE dc.movie_id = {};".format (movie_id, movie2_id))
    cur.execute ("SELECT t.tag FROM tags t WHERE t.movie_id = "
                 "{};".format (movie2_id))
    new_tag_list_dump = cur.fetchall ()
    new_tag_list = []
    for new_tag in new_tag_list_dump:
        new_tag_list.append (new_tag [0])
    print ("Tags on other movie: ")
    print (new_tag_list)
    cur.execute ("DELETE FROM tags WHERE tags.movie_id = {};".format (movie2_id))
    
    for tag in new_tag_list:
        escape_tag = con.escape (tag);
        cur.execute ("SELECT * FROM tags t WHERE t.movie_id = {} "
                     "AND t.tag = {};".format (movie_id, escape_tag))
        rows = cur.fetchone ()
        if not (rows is None):
            print ("{} already a tag; skipping...".format (tag))
        else:
            cur.execute ("INSERT INTO tags (movie_id, tag) "
                         "VALUES ({}, {});".format (movie_id, escape_tag));
    cur.execute ("DELETE FROM movie WHERE movie.movie_id = {};".format (movie2_id));

    con.commit ();

except mdb.Error as e:

    print (e)
    sys.exit(1)

finally:

    if con:
        con.rollback ()
        con.close()
