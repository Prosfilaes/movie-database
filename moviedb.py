#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pymysql as mdb
import sys
import readline
import sqlite3
import builtins

def _parse_year (s):
    '''Parse a four digit year from 1878 to 2020'''
    if len (s) != 4:
        return 0
    if not str.isdigit (s):
        return 0;
    movie_year = int (s)
    if 1878 > movie_year or movie_year > 2020:
        return 0;
    return movie_year

def _yn_to_bool (s):
    '''Turn a string starting with y(j) or n into a boolean'''
    if s [0:1].lower() == "n":
        return False
    elif s [0:1].lower() == "y" or s[0:1].lower() == "j":
        return True
    return None

def _process_tag_list (s):
    tag_list = [t.strip () for t in s.split (",")]
    if tag_list == ['']:
        return []
    else:
        return tag_list

def _report_new_tags (tag_list, prefix = ""):
    for tag in tag_list:
        cur.execute ("SELECT {0}tags.tag FROM {0}tags "
                     "WHERE {0}tags.tag = {1};".format (prefix, con.escape (tag)));
        numrows = cur.rowcount
        if numrows == 0:
            print (tag + " is new in the system.")

#def _report_new_people (people_list):
#    for person in people_list:
#        cur.execute ("SELECT person FROM person_name "
#                     "WHERE person = {};".format (con.escape (person)));
#        numrows = cur.rowcount
#        if numrows == 0:
#            print (person + " is new in the system.")

check_length = True
con = None
cur = None
default_full_length = True
global_tag_list = []
tv_show = None

def open ():
    '''Open the database connection'''
    global con, cur
    with builtins.open ("password", "r") as pass_file:
        l = pass_file.readline().split()
        username = l[0]
        password = l[1]
    con = mdb.connect('localhost', username, password, 'DVDs', use_unicode=True, charset="utf8")
    cur = con.cursor()
    cur.execute ("SET NAMES 'utf8'")
    return (con, cur)

def new_dvd ():
    '''Create a new dvd in the system, returning the dvd_id'''
    dvd_name = input ("Please enter the name of the DVD (set): ")
    escaped_dvd_name = con.escape (dvd_name)
    cur.execute ("INSERT INTO dvd (dvd_id, name) VALUES (null, {});".format (escaped_dvd_name))
    dvd_id = con.insert_id ()
    dvd_tag_list = _process_tag_list (input ("Please input dvd tags, comma separated: "))
    print ("DVD tags will be: ", end = "")
    print (dvd_tag_list)
    _report_new_tags (dvd_tag_list, "dvd_")
    for dvd_tag in dvd_tag_list:
        cur.execute ("INSERT INTO dvd_tags (dvd_id, tag) "
                     "VALUES ({}, {});".format (dvd_id, con.escape (dvd_tag)))
    return dvd_id

def new_tvshow ():
    '''Create a new dvd that has a TV show in the system, returning the dvd_id'''
    global tv_show
    dvd_name = input ("Please enter the name of the DVD (set): ")
    escaped_dvd_name = con.escape (dvd_name)
    cur.execute ("INSERT INTO dvd (dvd_id, name) VALUES (null, {});".format (escaped_dvd_name))
    dvd_id = con.insert_id ()
    dvd_tag_list = _process_tag_list (input ("Please input dvd tags, comma separated: "))
    print ("DVD tags will be: ", end = "")
    print (dvd_tag_list)
    _report_new_tags (dvd_tag_list, "dvd_")
    for dvd_tag in dvd_tag_list:
        cur.execute ("INSERT INTO dvd_tags (dvd_id, tag) "
                     "VALUES ({}, {});".format (dvd_id, con.escape (dvd_tag)))
    tv_show = input ("Please enter the name of the TV show: ")
    return dvd_id

def add_new_tvshow ():
    '''Add a TV show'''
    global tv_show
    tv_show = input ("Please enter the name of the TV show: ");
    return

def mangle_name_for_sort (name):
   if name [0:4] == "The ":
       return name [4:] + ", The"
   elif name [0:2] == "A ":
       return name [2:] + ", A"
   elif name [0:3] == "An ":
       return name [3:] + ", An"
   else:
       return name

def preload_movie_values ():
    '''Ask questions up front, and remember the answer for later movies'''
    global check_length, default_full_length, global_tag_list
    while (check_length == None):
        check_length_str = input ("Are any of these shorts? (Y/N): ")
        check_length = _yn_to_bool (check_length_str);
        if check_length == None:
            print ("Please answer y or n.")
    if check_length:
        all_shorts = None
        while (all_shorts == None):
            all_shorts = _yn_to_bool (input ("Are all of these shorts? (Y/N): "))
            if all_shorts:
                check_length = False
                default_full_length = False;
    global_tag_list = _process_tag_list (input ("Please input global tags, comma separated: "))
    print ("Global tags will be: ", end="")
    print (global_tag_list)
    _report_new_tags (global_tag_list)

def input_one_dvd_movie ():
    name = input ("Please enter the name of the movie and DVD: ")
    escaped_name = con.escape (name)
    cur.execute ("INSERT INTO dvd (dvd_id, name) VALUES (null, {});".format (escaped_name))
    dvd_id = con.insert_id ()
    dvd_tag_list = _process_tag_list (input ("Please input dvd tags, comma separated: "))
    print ("DVD tags will be: ", end = "")
    print (dvd_tag_list)
    _report_new_tags (dvd_tag_list, "dvd_")
    for dvd_tag in dvd_tag_list:
        cur.execute ("INSERT INTO dvd_tags (dvd_id, tag) "
                     "VALUES ({}, {});".format (dvd_id, con.escape (dvd_tag)))

    cur.execute ("SELECT * FROM movie WHERE movie.name = {};"
                 "".format (escaped_name))
    rows = cur.fetchall ()
    cur.execute ("SELECT movie.movie_id, movie.name, amn.name, movie.year, movie.is_full_length "
                 "FROM alternate_movie_names amn INNER JOIN movie ON amn.movie_id = movie.movie_id "
                 "WHERE amn.name = {};".format (escaped_name))
    rows += cur.fetchall ()
    is_existing_movie = False;
    if len (rows) > 0:
        print ("We have matching entries. Are any of the following your movie?")
        for row in rows:
            print (row)
        is_existing_movie = None
        while is_existing_movie == None:
            is_existing_movie = _yn_to_bool (input ("(Y/N) :"));
        if is_existing_movie:
            if len (rows) == 1:
                movie_id = rows [0][0];
            else:
                movie_id_str = ""
                while (not str.isdigit (movie_id_str)):
                    movie_id_str = input ("Which id? ")
                    movie_id = int (movie_id_str)
    if not is_existing_movie:
        movie_year = 0
        while (movie_year == 0):
            movie_year_str = input ("Year of the movie (1878-2020): ")
            movie_year = _parse_year (movie_year_str);
        is_full_length = None;
        while (is_full_length == None):
            ifl_str = input ("Is this a full-length feature? (Y/N): ")
            is_full_length = _yn_to_bool (ifl_str)
            if is_full_length == None:
                print ("Please answer y or n.")

        local_tag_list = _process_tag_list (input ("Please input tags, comma separated: "))
        _report_new_tags (local_tag_list)
        tag_list = local_tag_list;
        print ("Inserting tags ", end="")
        print (tag_list)

        hs_str = input ("Have you seen this movie? (Y/N): ")
        have_watched = _yn_to_bool (hs_str)

        sort_name = con.escape (mangle_name_for_sort (name))
        if have_watched == None:
            cur.execute ("INSERT INTO movie "
                         "(movie_id, name, year, is_full_length, sort_name) "
                         "VALUES (null, {}, {}, {}, {})"
                         ";".format (escaped_name, movie_year, 
                                     is_full_length, sort_name))
        else:
            cur.execute ("INSERT INTO movie "
                         "(movie_id, name, year, is_full_length, have_watched, sort_name) "
                         "VALUES (null, {}, {}, {}, {}, {})"
                         ";".format (escaped_name, movie_year, is_full_length,
                                     have_watched, sort_name))

        movie_id = con.insert_id ()
        for tag in set (tag_list):
            cur.execute ("INSERT INTO tags (movie_id, tag) "
                         "VALUES ({}, {});".format (movie_id, con.escape (tag)))
    else:
        cur.execute ("SELECT tags.tag FROM tags WHERE tags.movie_id = {};".format (movie_id))
        old_tags_return = cur.fetchall ()
        old_tags = [otag [0] for otag in old_tags_return];
        print ("Existing tags: ", end = "")
        print (old_tags)
        local_tag_list = _process_tag_list (input ("Please input tags, comma separated: "))
        _report_new_tags (local_tag_list)
        all_tag_list = global_tag_list + local_tag_list
        tag_list = [tag for tag in all_tag_list if tag not in old_tags]
        print ("Inserting tags ", end="")
        print (tag_list)
        for tag in set (tag_list):
            cur.execute ("INSERT INTO tags (movie_id, tag) "
                         "VALUES ({}, {});".format (movie_id, con.escape (tag)))

    cur.execute ("INSERT INTO dvd_contents (dvd_id, movie_id) "
                 "VALUES ({}, {});".format (dvd_id, movie_id))
    cur.execute ("INSERT IGNORE INTO has_been_retagged VALUES ({});".format (movie_id));
    return dvd_id;

def input_one_movie (dvd_id):
    movie_name = input ("Name of the movie, or hit enter to exit: ").strip()
    if movie_name == "":
        return;
    escaped_movie_name = con.escape (movie_name)
    cur.execute ("SELECT * FROM movie WHERE movie.name = {};".format (escaped_movie_name))
    rows = cur.fetchall ()
    cur.execute ("SELECT movie.movie_id, movie.name, amn.name, movie.year, movie.is_full_length "
                 "FROM alternate_movie_names amn INNER JOIN movie ON amn.movie_id = movie.movie_id "
                 "WHERE amn.name = {};".format (escaped_movie_name))
    rows += cur.fetchall ()
    is_existing_movie = False;
    
    if len (rows) > 0:
        print ("We have matching entries. Are any of the following your movie?")
        for row in rows:
            print (row)
        is_existing_movie = None
        while is_existing_movie == None:
            is_existing_movie = _yn_to_bool (input ("(Y/N) :"));
        if is_existing_movie:
            if len (rows) == 1:
                movie_id = rows [0][0];
            else:
                movie_id_str = ""
                while (not str.isdigit (movie_id_str)):
                    movie_id_str = input ("Which id? ")
                    movie_id = int (movie_id_str)
    if not is_existing_movie:
        movie_year = 0
        while (movie_year == 0):
            movie_year_str = input ("Year of the movie (1878-2020): ")
            movie_year = _parse_year (movie_year_str);
        if check_length:
            is_full_length = None;
            while (is_full_length == None):
                ifl_str = input ("Is this a full-length feature? (Y/N): ")
                is_full_length = _yn_to_bool (ifl_str)
                if is_full_length == None:
                    print ("Please answer y or n.")
        else:
            is_full_length = default_full_length;

        local_tag_list = _process_tag_list (input ("Please input tags, comma separated: "))
        _report_new_tags (local_tag_list)
        tag_list = global_tag_list + local_tag_list;
        print ("Inserting tags ", end="")
        print (tag_list)
        
#        people_list = _process_tag_list (input ("Please input notable creators, comma separated: "))
#        _report_new_people (people_list)
        
        hs_str = input ("Have you seen this movie? (Y/N): ")
        have_watched = _yn_to_bool (hs_str)
        
        sort_name = con.escape (mangle_name_for_sort (movie_name))

        if have_watched == None:
            cur.execute ("INSERT INTO movie "
                         "(movie_id, name, year, is_full_length, sort_name) "
                         "VALUES (null, {}, {}, {}, {})"
                         ";".format (escaped_movie_name, movie_year, 
                                     is_full_length, sort_name))
        else:
            cur.execute ("INSERT INTO movie "
                         "(movie_id, name, year, is_full_length, have_watched, sort_name) "
                         "VALUES (null, {}, {}, {}, {}, {})"
                         ";".format (escaped_movie_name, movie_year, is_full_length,
                                     have_watched, sort_name))

        movie_id = con.insert_id ()
        for tag in set (tag_list):
            cur.execute ("INSERT INTO tags (movie_id, tag) "
                         "VALUES ({}, {});".format (movie_id, con.escape (tag)))
        insert_people (movie_id, movie_name, movie_year)
    else:
        cur.execute ("SELECT tags.tag FROM tags WHERE tags.movie_id = {};".format (movie_id))
        old_tags_return = cur.fetchall ()
        old_tags = [otag [0] for otag in old_tags_return];
        print ("Existing tags: ", end = "")
        print (old_tags)
        local_tag_list = _process_tag_list (input ("Please input tags, comma separated: "))
        _report_new_tags (local_tag_list)
        all_tag_list = global_tag_list + local_tag_list
        tag_list = [tag for tag in all_tag_list if tag not in old_tags]
        print ("Inserting tags ", end="")
        print (tag_list)
        for tag in set (tag_list):
            cur.execute ("INSERT INTO tags (movie_id, tag) "
                         "VALUES ({}, {});".format (movie_id, con.escape (tag)))
    cur.execute ("INSERT INTO dvd_contents (dvd_id, movie_id) "
                 "VALUES ({}, {});".format (dvd_id, movie_id))
    cur.execute ("SELECT * FROM has_been_retagged WHERE movie_id = {};".format (movie_id));
    if cur.rowcount == 0:
        cur.execute ("INSERT INTO has_been_retagged VALUES ({});".format (movie_id));
    return movie_id;

def add_people (movie_id):
    cur.execute ("SELECT name, year FROM movie WHERE movie_id = {};".format(movie_id));
    (movie_name, movie_year) = cur.fetchone ()
    insert_people (movie_id, movie_name, movie_year)

ordinal = ["Zeroth", "First", "Second", "Third", "Fourth", 
           "Fifth", "Sixth", "Seventh", "Eighth", "Ninth",
           "Tenth", "Eleventh", "Twelfth", "Thirteenth", "Fourteenth", "Fifteenth", 
           "Sixteenth", "Seventeenth", "Eighteenth", "Ninteenth", "Twentieth",
           "Twenty-First", "Twenty-Second", "Twenty-Third", "Twenty-Fourth", "Twenty-Fifth"]
def cur_execute (s):
    print (s)
    cur.execute (s)

def input_one_show (dvd_id):
    print ()
    show_name = input ("What's the name of the show? ")
    if show_name == '':
        return
    season_num = 0
    while season_num == 0:
        season_str = input ("What integer season number is it? (1-25): ")
        if str.isdigit (season_str):
            season_num = int (season_str)
            if season_num < 1 or season_num > 25:
                season_num = 0
    episode_num = 0
    while episode_num == 0:
        episode_str = input ("What integer episode number is it? ")
        if str.isdigit (episode_str):
            episode_num = int (episode_str)
            if episode_num < 1:
                episode_num = 0
    show_year = 0
    while (show_year < 1936):
        show_year_str = input ("IMDB show year (1936-2020): ")
        show_year = _parse_year (show_year_str);
        
    movie_year = 0
    while (movie_year < 1936):
        movie_year_str = input ("Episode year (1936-2020): ")
        movie_year = _parse_year (movie_year_str);

    if check_length:
        is_full_length = None;
        while (is_full_length == None):
            ifl_str = input ("Is this a full-length feature? (Y/N): ")
            is_full_length = _yn_to_bool (ifl_str)
            if is_full_length == None:
                print ("Please answer y or n.")
    else:
        is_full_length = default_full_length;

    local_tag_list = _process_tag_list (input ("Please input tags, comma separated: "))
    _report_new_tags (local_tag_list)
    tag_list = global_tag_list + local_tag_list;
    print ("Inserting tags ", end="")
    print (tag_list)
    
    imdbcon = sqlite3.connect ('imdb/tv_show.db')
    imdbcur = imdbcon.cursor ()
    imdbcur.execute ("SELECT show_name, episode_name FROM episode_names "
                     "WHERE show_name = ? AND season = ? AND episode = ? AND year = ?;",
                     (show_name, season_num, episode_num, show_year))
    movie_list = imdbcur.fetchall ()
    # We need to deal with this all more elegantly, find some nonmanual solution for loading
    # non-IMDB data
    if len (movie_list) == 1:
        print ('Is "{}" (IMDB {}), season {}, episode {} named "{}" correct?'
               ''.format (movie_list [0][0], show_year, season_num, episode_num, movie_list [0][1]))
        is_correct = _yn_to_bool (input (": "))
        if not (is_correct):
            return
        episode_name = movie_list [0][1]
    elif len (movie_list) == 0:
        if _yn_to_bool (input("Show not found in tv_show.db; continue? ")):
            episode_name = input("Enter episode name: ")
        else:
            return
    else:
        print ("Multiple episodes return; database problem.")
        print (movie_list)
        return;
      
    hs_str = input ("Have you seen this episode? (Y/N): ")
    have_watched = _yn_to_bool (hs_str)

    sort_episode_name = mangle_name_for_sort (episode_name)
    sort_tv_show = mangle_name_for_sort (show_name)
    escaped_movie_name = con.escape ('"' + show_name + '": ' + episode_name)
    escaped_sort_name = con.escape ('"' + sort_tv_show + '": ' + sort_episode_name)

    print ((sort_episode_name, sort_tv_show, escaped_movie_name, escaped_sort_name))
    if have_watched == None:
        cur.execute ("INSERT INTO movie "
                     "(movie_id, name, year, is_full_length, sort_name) "
                     "VALUES (null, {}, {}, {}, {})"
                     ";".format (escaped_movie_name, movie_year, 
                                 is_full_length, escaped_sort_name))
    else:
        cur.execute ("INSERT INTO movie "
                     "(movie_id, name, year, is_full_length, have_watched, sort_name) "
                     "VALUES (null, {}, {}, {}, {}, {})"
                     ";".format (escaped_movie_name, movie_year, is_full_length,
                                 have_watched, escaped_sort_name))

    movie_id = con.insert_id ()
    for tag in set(tag_list):
        cur.execute ("INSERT INTO tags (movie_id, tag) "
                     "VALUES ({}, {});".format (movie_id, con.escape (tag)))

    cur.execute ("INSERT INTO dvd_contents (dvd_id, movie_id) "
                 "VALUES ({}, {});".format (dvd_id, movie_id))
    cur.execute ("INSERT INTO has_been_retagged VALUES ({});".format (movie_id));
    print (movie_id, show_name, season_num, episode_num)
    cur.execute ("INSERT INTO tv_show (movie_id, show_name, episode_name, season_num, episode_num) "
                 "VALUES ({}, {}, {}, {}, {});"
                 "".format (movie_id, con.escape (show_name), con.escape (episode_name), season_num, episode_num))
    
    imdbcur.execute ("SELECT actor FROM episode_actors where show_name = ? AND season = ? AND episode = ? AND year = ?;",
                     (show_name, season_num, episode_num, show_year))
    actor_list = set(imdbcur.fetchall ())
    for i in actor_list:
        cur.execute ("INSERT INTO actor VALUES ({}, {});"
                     "".format (con.escape(i[0]), movie_id))
    imdbcur.execute ("SELECT director FROM episode_directors where show_name = ? AND season = ? AND episode = ? AND year = ?;",
                     (show_name, season_num, episode_num, show_year))    
    dir_list = imdbcur.fetchall ()
    for i in dir_list:
        cur.execute ("INSERT INTO director VALUES ({}, {});"
                     "".format (con.escape(i[0]), movie_id))
    imdbcon.rollback ()
    imdbcon.close ()
    print ()
    return movie_id;

def input_one_tv_season (dvd_id):
    print ()
    show_name = input ("What's the name of the show? ")
    if show_name == None:
        return
    season_num = 0
    while season_num == 0:
        season_str = input ("What integer season number is it? (1-25): ")
        if str.isdigit (season_str):
            season_num = int (season_str)
            if season_num < 1 or season_num > 25:
                season_num = 0
    show_year = 0
    while (show_year < 1936):
        show_year_str = input ("IMDB show year (1936-2020): ")
        show_year = _parse_year (show_year_str);
        
    # Problematic; we're still adding bad years, just not as bad, since seasons can cross years
    movie_year = 0
    while (movie_year < 1936):
        movie_year_str = input ("Season year (1936-2020): ")
        movie_year = _parse_year (movie_year_str);
        
    if check_length:
        is_full_length = None;
        while (is_full_length == None):
            ifl_str = input ("Is this a full-length feature? (Y/N): ")
            is_full_length = _yn_to_bool (ifl_str)
            if is_full_length == None:
                print ("Please answer y or n.")
    else:
        is_full_length = default_full_length;

    local_tag_list = _process_tag_list (input ("Please input tags, comma separated: "))
    _report_new_tags (local_tag_list)
    tag_list = global_tag_list + local_tag_list;
    print ("Inserting tags ", end="")
    print (tag_list)
    
    imdbcon = sqlite3.connect ('imdb/tv_show.db')
    imdbcur = imdbcon.cursor ()
    imdbcur.execute ("SELECT DISTINCT show_name FROM episode_names "
                     "WHERE show_name = ? AND season = ? AND year = ?;",
                     (show_name, season_num, show_year))
    movie_list = imdbcur.fetchall ()
    if len (movie_list) == 1:
        tvshow = movie_list [0]
        print ("Unique TV show found: ", end="")
        print (tvshow)
        is_correct = _yn_to_bool (input ("Is this correct? "))
        if not (is_correct):
            return       
    elif len (movie_list) == 0:
        print ("No TV shows found; exiting.")
        return
    else:
        print ("Non-unique TV shows found: ")
        print (movie_list)
        print ("Database problem; exiting.")
    hs_str = input ("Have you seen this season? (Y/N): ")
    have_watched = _yn_to_bool (hs_str)
    #season_year = 0
    #while 1936 > season_year or 2020 < season_year:
    #    season_year = int (input ("What year is this season? " ))
    imdbcur.execute ("SELECT show_name, season, episode, episode_name FROM episode_names "
                     "WHERE show_name = ? and season = ? and year = ? ORDER BY episode;",
                     (show_name, season_num, show_year))
    episode_list = imdbcur.fetchall ()
    for e in episode_list:
        print (e)
        (show_name, season_num, episode_num, episode_name) = e;
        sort_episode_name = mangle_name_for_sort (episode_name)
        sort_tv_show = mangle_name_for_sort (show_name)
        escaped_movie_name = con.escape ('"' + show_name + '": ' + episode_name)
        escaped_sort_name = con.escape ('"' + sort_tv_show + '": ' + sort_episode_name)

        print ((sort_episode_name, sort_tv_show, escaped_movie_name, escaped_sort_name))
        if have_watched == None:
            cur.execute ("INSERT INTO movie "
                         "(movie_id, name, year, is_full_length, sort_name) "
                         "VALUES (null, {}, {}, {}, {})"
                         ";".format (escaped_movie_name, movie_year, 
                                     is_full_length, escaped_sort_name))
        else:
            cur.execute ("INSERT INTO movie "
                         "(movie_id, name, year, is_full_length, have_watched, sort_name) "
                         "VALUES (null, {}, {}, {}, {}, {})"
                         ";".format (escaped_movie_name, movie_year, is_full_length,
                                     have_watched, escaped_sort_name))

        movie_id = con.insert_id ()
        #print ("#1 ", movie_id)
        for tag in set(tag_list):
            cur.execute ("INSERT INTO tags (movie_id, tag) "
                         "VALUES ({}, {});".format (movie_id, con.escape (tag)))
        #print ("#2 ")
        cur.execute ("INSERT INTO dvd_contents (dvd_id, movie_id) "
                     "VALUES ({}, {});".format (dvd_id, movie_id))
        cur.execute ("INSERT INTO has_been_retagged VALUES ({});".format (movie_id));
        #print ("#3 ")
        print (movie_id, show_name, season_num, episode_num)
        cur.execute ("INSERT INTO tv_show (movie_id, show_name, episode_name, season_num, episode_num) "
                     "VALUES ({}, {}, {}, {}, {});"
                     "".format (movie_id, con.escape (show_name), con.escape (episode_name), season_num, episode_num))
        #print ("#4 ")
        imdbcur.execute ("SELECT actor FROM episode_actors where show_name = ? AND season = ? AND episode = ?;",
                         (show_name, season_num, episode_num))
        actor_list = set(imdbcur.fetchall ())
        for i in actor_list:
            cur.execute ("INSERT INTO actor VALUES ({}, {});"
                         "".format (con.escape(i[0]), movie_id))
        imdbcur.execute ("SELECT director FROM episode_directors where show_name = ? AND season = ? AND episode = ?;",
                         (show_name, season_num, episode_num))
        #print ("#5")
        dir_list = imdbcur.fetchall ()
        for i in dir_list:
            cur.execute ("INSERT INTO director VALUES ({}, {});"
                         "".format (con.escape(i[0]), movie_id))
    cur.execute ("INSERT INTO complete_seasons VALUES ({}, {}, 0);"
                 "".format (con.escape (show_name), season_num));
    imdbcon.rollback ()
    imdbcon.close ()
    print ()
    return movie_id;

def close_dvd (dvd_id):
    cur.execute ("SELECT dvd.name FROM dvd WHERE dvd.dvd_id = {};".format (dvd_id))
    dvd_name = cur.fetchone ()[0]
    print ("Successful insertion of movies for {}, dvd_id {}.".format (dvd_name, dvd_id))
    cur.execute ("SELECT movie.movie_id, movie.name, movie.year, movie.is_full_length FROM movie "
                 "INNER JOIN dvd_contents ON dvd_contents.movie_id = movie.movie_id "
                 "INNER JOIN dvd ON dvd_contents.dvd_id = dvd.dvd_id WHERE dvd.dvd_id = {};".format (dvd_id))
    rows = cur.fetchall ()
    for row in rows:
        print (row)

def close_database ():
    con.commit ()
    con.close ()

def abort_database ():
    con.rollback ()
    con.close ()

def display_dvd (dvd_id):
    cur.execute ("SELECT dvd.name from dvd WHERE dvd.dvd_id = {}"
                 ";".format (dvd_id))
    rows = cur.fetchall ()
    for row in rows:
        print (row[0])

def display_movie (movie_id):
    cur.execute ("SELECT movie.movie_id, movie.name, movie.year, movie.sort_name, "
                 "movie.is_full_length, movie.have_watched "
                 "FROM movie "
                 "WHERE movie.movie_id = {};".format (movie_id))
    row = cur.fetchone ()
    print ("{} ({}) (ID: {}) (Sorted as {})".format (row[1], row[2], row[0], row[3]))
    print ("Full length: {}; Has been watched: {}".format (row[4], row[5]))
    cur.execute ("SELECT dvd.name, dvd.dvd_id FROM dvd "
                 "INNER JOIN dvd_contents dc ON dc.dvd_id = dvd.dvd_id "
                 "WHERE dc.movie_id = {};".format (row [0]))
    rows = cur.fetchall ()
    DVDs_list = ["{} (DVD id {})".format(x[0], x[1]) for x in rows]
    print ("On DVDs: {}".format (DVDs_list))
    cur.execute ("SELECT tags.tag FROM tags WHERE tags.movie_id = {};".format (row[0]))
    rows = cur.fetchall ()
    tags_list = [x[0] for x in rows]
    print ("Tagged: {}".format (tags_list))

def get_movie_id ():
    while (True):
        movie_name = input ("Name of the movie, or hit enter to exit: ")
        if movie_name == "":
            actually_quit = input (
                "If you don't want to exit, type no; any other key to continue. ")
            if actually_quit [0:1].lower() == "n":
                continue
            else:
                return
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
                is_existing_movie = _yn_to_bool (input ("Is this your movie? (Y/N) "));
            if not is_existing_movie:
                continue;
            movie_id = rows [0][0];
        else:
            print ("We have matching entries. Are any of the following your movie?")
            for row in rows:
                print (row)
            is_existing_movie = None
            while is_existing_movie == None:
                is_existing_movie = _yn_to_bool (input ("(Y/N): "));
            if not is_existing_movie:
                continue;
            movie_id_str = ""
            while (not str.isdigit (movie_id_str)):
                movie_id_str = input ("Which id? ")
            movie_id = int (movie_id_str);
        if movie_id in [movie[0] for movie in rows]:
            return movie_id

def insert_people (movie_id, movie, year):
    imdbcon = sqlite3.connect ('imdb/movies.db')
    imdbcur = imdbcon.cursor ()
    imdbcur.execute ("SELECT movie_id, movie_name, year, variant FROM movie "
                     "WHERE movie_name = ? AND year = ?;", (movie, year))
    movie_list = imdbcur.fetchall ()
    if len (movie_list) == 1:
        print ("Loading ", movie_list[0])
        sqlite_movie_id = movie_list [0][0]
    elif len (movie_list) == 0:
        print ("Movie not found in movies.db")
        return
    else:
        choice = None
        while choice == None:
            for i in range (len(movie_list)):
                print (i, ": ", movie_list [1])
            chstr = input ("Which number do you want? (Go high for none of the above)")
            choice = int (chstr)
            if choice == None:
                continue                
            if choice >= len (movie_list):
                return
        sqlite_movie_id = movie_list [choice][0]
    imdbcur.execute ("SELECT actor FROM movie_actors where movie_id = ?;", (sqlite_movie_id, ))
    actor_list = imdbcur.fetchall ()
    for i in actor_list:
        cur.execute ("INSERT INTO actor VALUES ({}, {});"
                     "".format (con.escape(i[0]), movie_id))
    imdbcur.execute ("SELECT director FROM movie_directors where movie_id = ?;", (sqlite_movie_id, ))
    dir_list = imdbcur.fetchall ()
    for i in dir_list:
        cur.execute ("INSERT INTO director VALUES ({}, {});"
                     "".format (con.escape(i[0]), movie_id))
    return

def markwatched (movie_id):
    cur.execute ("UPDATE movie SET have_watched = true WHERE movie_id = {};".format (movie_id))

def commit_data ():
    con.commit ()

