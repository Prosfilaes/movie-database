#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pymysql as mdb
import sys
import readline
import time

def calculate_movie_data (movie_id):
    movie_tree = [set((movie_id,))]
    movie_set = set ((movie_id,))
    i = 0
    while (len (movie_tree[i]) > 0):
        i += 1;
        movie_tree.append (set ())
        for movie in movie_tree[i - 1]:
            cur.execute ("SELECT DISTINCT m2m.movie_id2 from m2m "
                         "WHERE m2m.movie_id1 = {};"
                         "".format (con.escape (movie)));       
            newbies = cur.fetchall ()
            for newb in newbies:
                if newb[0] not in movie_set:
                    movie_set.add (newb [0])
                    movie_tree [i].add (newb[0])   
    return (movie_set, movie_tree)

def average_bacon_num (movie_tree, total_number_of_movies):
    total_bacon = 0
    for j in range (len (movie_tree)):
        total_bacon += j * len(movie_tree [j])
    return total_bacon / total_number_of_movies 

def create_table_m2m (table_num):
    cur.execute ("CREATE TEMPORARY TABLE m2m "
                 "(movie_id1 SMALLINT (5) UNSIGNED NOT NULL, "
                 "movie_id2 SMALLINT (5) UNSIGNED NOT NULL, "
                 "INDEX mid_idx (movie_id1));")
    if table_num == 1:
        cur.execute ("INSERT INTO m2m "
                     "SELECT DISTINCT p1.movie_id, p2.movie_id FROM actor p1 "
                     "INNER JOIN actor p2 ON p1.person = p2.person AND p1.movie_id != p2.movie_id;")
    elif table_num == 2 or table_num == 5:
        cur.execute ("CREATE TEMPORARY TABLE small_dvd_movies "
                     "(movie_id SMALLINT (5) UNSIGNED UNIQUE NOT NULL, "
                     "INDEX mid_idx (movie_id)); ")
        if table_num == 2:
            cur.execute ('INSERT INTO small_dvd_movies '
                         'SELECT DISTINCT movie_id FROM dvd d '
                         'INNER JOIN dvd_contents dc ON dc.dvd_id = d.dvd_id '
                         'WHERE d.dvd_id NOT IN '
                         '(SELECT dvd_id FROM dvd_tags WHERE tag = "large movie pack");');
            cur.execute ('INSERT IGNORE INTO small_dvd_movies '
                         'SELECT movie_id FROM movie WHERE have_watched;')
        elif table_num == 5:
            #The full length only version of the above
            cur.execute ('INSERT INTO small_dvd_movies '
                         'SELECT DISTINCT m.movie_id FROM dvd d '
                         'INNER JOIN dvd_contents dc ON dc.dvd_id = d.dvd_id '
                         'INNER JOIN movie m ON dc.movie_id = m.movie_id AND m.is_full_length '
                         'WHERE d.dvd_id NOT IN '
                         '(SELECT dvd_id FROM dvd_tags WHERE tag = "large movie pack");');
            cur.execute ('INSERT IGNORE INTO small_dvd_movies '
                         'SELECT movie_id FROM movie WHERE have_watched and is_full_length;')
        else:
            assert True, "This should be unreachable"
        cur.execute ("INSERT INTO m2m "
                     "SELECT DISTINCT p1.movie_id, p2.movie_id FROM actor p1 "
                     "INNER JOIN actor p2 ON p1.person = p2.person AND p1.movie_id != p2.movie_id "
                     "WHERE p1.movie_id IN (SELECT movie_id from small_dvd_movies); ")  
        #The natural formulation doesn't work in MySQL, since you can't reference the temporary table small_dvd_movies
        #twice in one statement
        cur.execute ("DELETE FROM m2m WHERE movie_id2 NOT IN (SELECT movie_id from small_dvd_movies);")
    elif table_num == 3:
        cur.execute ("INSERT INTO m2m "
                     "SELECT DISTINCT m1.movie_id, m2.movie_id FROM movie m1 "
                     "INNER JOIN actor p1 ON p1.movie_id = m1.movie_id "
                     "INNER JOIN actor p2 ON p1.person = p2.person "
                     "INNER JOIN movie m2 on p2.movie_id = m2.movie_id AND m2.have_watched "
                     "WHERE m1.have_watched;")
    elif table_num == 4:
        cur.execute ("INSERT INTO m2m "
                     "SELECT DISTINCT p1.movie_id, p2.movie_id FROM actor p1 "
                     "INNER JOIN actor p2 "
                     "ON p1.person = p2.person AND p1.movie_id != p2.movie_id "
                     "INNER JOIN movie m1 ON p1.movie_id = m1.movie_id AND m1.is_full_length "
                     "INNER JOIN movie m2 ON p2.movie_id = m2.movie_id AND m2.is_full_length "
                     ";")
    elif table_num == 6:
        cur.execute ("INSERT INTO m2m "
                     "SELECT DISTINCT m1.movie_id, m2.movie_id FROM movie m1 "
                     "INNER JOIN actor p1 ON p1.movie_id = m1.movie_id "
                     "INNER JOIN actor p2 ON p1.person = p2.person "
                     "INNER JOIN movie m2 ON p2.movie_id = m2.movie_id AND m2.have_watched AND m2.is_full_length "
                     "WHERE m1.have_watched AND m1.is_full_length;")
    elif table_num == 7:
        cur.execute ("INSERT INTO m2m "
                     "SELECT DISTINCT p1.movie_id, p2.movie_id FROM actor p1 "
                     "INNER JOIN actor p2 "
                     "ON p1.person = p2.person AND p1.movie_id != p2.movie_id "
                     "INNER JOIN movie m1 ON p1.movie_id = m1.movie_id  "
                     "INNER JOIN movie m2 ON p2.movie_id = m2.movie_id  "
                     "WHERE m1.movie_id in (SELECT movie_id FROM tv_show) AND "
                     "m2.movie_id in (SELECT movie_id FROM tv_show) "
                     ";")
    elif table_num == 8:
        cur.execute ("INSERT INTO m2m "
                     "SELECT DISTINCT m1.movie_id, m2.movie_id FROM movie m1 "
                     "INNER JOIN actor p1 ON p1.movie_id = m1.movie_id "
                     "INNER JOIN actor p2 ON p1.person = p2.person "
                     "INNER JOIN movie m2 ON p2.movie_id = m2.movie_id AND m2.have_watched AND m2.is_full_length "
                     "INNER JOIN tags t1 ON t1.movie_id = m1.movie_id AND t1.tag = 'science fiction' "
                     "INNER JOIN tags t2 ON t2.movie_id = m2.movie_id AND t2.tag = 'science fiction' "
                     "WHERE m1.have_watched AND m1.is_full_length;")
    else:
        assert True, "table_nums above 8 are unknown"
    return

try:
    MAX_TABLENUM = 8
    # This is inappropriately intertangled in so many ways.
    # The appropriate thing would be to find the largest subset
    # instead of storing a value known to be in the largest subset.
    # That's more work, both coding and computational, and speed
    # matters for this code.
    initial_movie_id = [None, 376, 376, 376, 376, 376, 376, 4584, 51]
    if (len(sys.argv) != 2 or int(sys.argv[1]) < 1 or
        int(sys.argv[1]) > MAX_TABLENUM):
        
        print ("This program takes one argument, the tablenum to calculate, in the range 1 .. {}."
               "".format (MAX_TABLENUM))
        sys.exit()
        
    table_num = int(sys.argv[1])
    start_time = time.clock ()
    global con, cur
    insert = True
    con = mdb.connect('localhost', 'dvdeug', '', 'DVDs', use_unicode=True, charset="utf8")
    cur = con.cursor()
    cur.execute ("SET NAMES 'utf8'")
    create_table_m2m (table_num)
    cur.execute ("SELECT movie_id, bacon_num FROM moviebacon WHERE table_num = {};"
                 "".format(table_num))
    prior_bacon_nums = dict (cur.fetchall ())
    setup_end_time = time.clock ()
    root_id = initial_movie_id[table_num]
    (global_movie_set, movie_tree) = calculate_movie_data (root_id)
    num_movies = len (global_movie_set)
    cur.execute ("SELECT description FROM moviebacon_tablenum WHERE table_num = {};"
                 "".format(table_num))
    print ("The {} list following is about the relations of {} movies."
           "".format (cur.fetchone()[0], num_movies))
    sys.stdout.flush()
    bacon_list = [(root_id, average_bacon_num (movie_tree, num_movies))]
    global_movie_set.remove (root_id)
    zero_count = 0
    for movie in global_movie_set:
        bacon_list.append ((movie, average_bacon_num (calculate_movie_data (movie)[1], num_movies)))
        if zero_count > -1:
            if bacon_list [-1][0] not in prior_bacon_nums:
                zero_count = -1
                continue
            if bacon_list[-1][1] == prior_bacon_nums [bacon_list[-1][0]]:
                zero_count += 1
            else:
                zero_count = -1
            if zero_count == 3:
                print ("Results haven't changed since last run; aborting.")
                sys.exit (0)       
    data_collection_time = time.clock ()
 
    bacon_list.sort (key=lambda x: x[1])
    if insert:
        cur.execute ("DELETE FROM moviebacon WHERE table_num = {};".format (table_num))
    for x in bacon_list:
        cur.execute ("SELECT name, year FROM movie WHERE movie_id = {};".format (x[0]));
        name = cur.fetchall ()
        if insert:
            cur.execute ("INSERT into moviebacon VALUES ({}, {}, {});".format (table_num, x[0], x[1]))
        print ("{} ({}): {:.4f}".format(name[0][0], name[0][1], x[1]), end = ";")
        if x[0] in prior_bacon_nums:
            print (" / old {:.4f} / change {:+.4f}"
                   "".format (prior_bacon_nums [x[0]],
                              x[1] - prior_bacon_nums [x[0]]));
        else:
            print (" / not previously in universe")
    if insert:
        con.commit ()
    else:
        con.rollback ()
    final_time = time.clock ()
    print ("Setup: {:.2f}s; travelling time: {:.2f}s; per movie: {:.4f}s; total: {:.2f}s"
           "".format (setup_end_time - start_time, data_collection_time - setup_end_time,
                      (data_collection_time - setup_end_time) / num_movies,
                      final_time - start_time))
except mdb.Error as e:
    print (e)
    con.rollback ()
    sys.exit(1)
