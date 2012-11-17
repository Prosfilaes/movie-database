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

try:
    start_time = time.clock ()
    global con, cur
    insert = False
    con = mdb.connect('localhost', 'dvdeug', '', 'DVDs', use_unicode=True, charset="utf8")
    cur = con.cursor()
    cur.execute ("SET NAMES 'utf8'")
    cur.execute ("CREATE TEMPORARY TABLE m2m "
                 "(movie_id1 SMALLINT (5) UNSIGNED NOT NULL, "
                 "movie_id2 SMALLINT (5) UNSIGNED NOT NULL, "
                 "INDEX mid_idx (movie_id1));")
    cur.execute ("INSERT INTO m2m "
                 "SELECT DISTINCT p1.movie_id, p2.movie_id FROM actor p1 "
                 "INNER JOIN actor p2 "
                 "ON p1.person = p2.person AND p1.movie_id != p2.movie_id "
                 "INNER JOIN movie m1 ON p1.movie_id = m1.movie_id AND m1.is_full_length AND m1.have_watched "
                 "INNER JOIN movie m2 ON p2.movie_id = m2.movie_id AND m2.is_full_length AND m2.have_watched "
                 ";")
    cur.execute ("SELECT movie_id, bacon_num FROM moviebacon WHERE table_num = 6;")
    prior_bacon_nums = dict (cur.fetchall ())
    setup_end_time = time.clock ()
    (global_movie_set, movie_tree) = calculate_movie_data (376)
    num_movies = len (global_movie_set)
    bacon_list = [(376, average_bacon_num (movie_tree, num_movies))]
    global_movie_set.remove (376)
    zero_count = 0
    for movie in global_movie_set:
        bacon_list.append ((movie, average_bacon_num (calculate_movie_data (movie)[1], num_movies)))
        if zero_count > -1:
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
        cur.execute ("DELETE FROM moviebacon WHERE table_num = 6;")
    for x in bacon_list:
        cur.execute ("SELECT name, year FROM movie WHERE movie_id = {};".format (x[0]));
        name = cur.fetchall ()
        if insert:
            cur.execute ("INSERT into moviebacon VALUES (6, {}, {});".format (x[0], x[1]))
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
