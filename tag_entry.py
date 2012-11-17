#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pymysql as mdb
import sys
import readline

def parse_year (s):
    '''Parse a four digit year from 1878 to 2020'''
    if len (s) != 4:
        return 0
    if not str.isdigit (s):
        return 0;
    movie_year = int (s)
    if 1878 > movie_year or movie_year > 2020:
        return 0;
    return movie_year

def yn_to_bool (s):
    '''Turn a string starting with y(j) or n into a boolean'''
    if s [0:1].lower() == "n":
        return False
    elif s [0:1].lower() == "y" or s[0:1].lower() == "j":
        return True
    return None

def process_tag_list (s):
    tag_list = [t.strip () for t in s.split (",")]
    if tag_list == ['']:
        return []
    else:
        return tag_list

def report_new_tags (tag_list, prefix = ""):
    for tag in tag_list:
        cur.execute ("SELECT {0}tags.tag FROM {0}tags WHERE {0}tags.tag = {1};".format (prefix, con.escape (tag)));
        numrows = cur.rowcount
        if numrows == 0:
            print (tag + " is new in the system.")

con = None

try:
    cur_execute = print
    con = mdb.connect('localhost', 'dvdeug', '', 'DVDs', use_unicode=True, charset="utf8")
    cur = con.cursor()
    cur.execute ("SET NAMES 'utf8'")

    while (True):
        movie_name = input ("Name of the movie, or hit enter to exit: ")
        if movie_name == "":
            actually_quit = input (
                "If you don't want to exit, type no; any other key to continue. ")
            if actually_quit [0:1].lower() == "n":
                continue
            else:
                break
        escaped_movie_name = con.escape (movie_name)
        cur.execute ("SELECT * FROM movie WHERE movie.name = {};".format (escaped_movie_name))
        rows = cur.fetchall ()
        cur.execute ("SELECT movie.movie_id, movie.name, amn.name, movie.year, movie.is_full_length "
                     "FROM alternate_movie_names amn INNER JOIN movie ON amn.movie_id = movie.movie_id "
                     "WHERE amn.name = {};".format (escaped_movie_name))
        rows += cur.fetchall ()
        is_existing_movie = False;
        if len (rows) == 0:
            escaped_move_name = con.escape (movie_name);
            cur.execute ("SELECT * FROM movie WHERE movie.name "
                         "LIKE CONCAT ('%', {}, '%');".format (escaped_movie_name))
            rows = cur.fetchall ()
            cur.execute ("SELECT movie.movie_id, movie.name, amn.name, movie.year, movie.is_full_length "
                         "FROM alternate_movie_names amn INNER JOIN movie ON amn.movie_id = movie.movie_id "
                         "WHERE amn.name LIKE CONCAT ('%', {}, '%');".format (escaped_movie_name))
            rows += cur.fetchall ()
        if len (rows) == 0:
            print ("No matching entries found. Please try again.");
            continue;
        if len (rows) == 1:
            print (rows[0])
            is_existing_movie = None
            while is_existing_movie == None:
                is_existing_movie = yn_to_bool (input ("Is this your movie? (Y/N) "));
            if not is_existing_movie:
                continue;
            movie_id = rows [0][0];
        else:
            print ("We have matching entries. Are any of the following your movie?")
            for row in rows:
                print (row)
            is_existing_movie = None
            while is_existing_movie == None:
                is_existing_movie = yn_to_bool (input ("(Y/N): "));
            if not is_existing_movie:
                continue;
            movie_id_str = ""
            while (not str.isdigit (movie_id_str)):
                movie_id_str = input ("Which id? ")
            movie_id = int (movie_id_str);

        cur.execute ("SELECT * FROM tags t WHERE t.movie_id = {};".format (movie_id))
        rows = cur.fetchall ()
        for row in rows:
            print (row)
        local_tag_list = process_tag_list (input ("Please input tags, comma separated: "))
        report_new_tags (local_tag_list)
        print ("Inserting tags ", end="")
        print (local_tag_list)

        for tag in local_tag_list:
            escape_tag = con.escape (tag);
            cur.execute ("SELECT * FROM tags t WHERE t.movie_id = {} "
                         "AND t.tag = {};".format (movie_id, escape_tag))
            rows = cur.fetchone ()
            if not (rows is None):
                print ("{} already a tag; skipping...".format (tag))
            else:
                cur.execute ("INSERT INTO tags (movie_id, tag) "
                             "VALUES ({}, {});".format (movie_id, escape_tag));

    con.commit ()


except mdb.Error as e:

    print (e)
    sys.exit(1)

finally:

    if con:
        con.rollback ()
        con.close()
