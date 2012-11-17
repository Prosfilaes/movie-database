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
            cur.execute ("SELECT DISTINCT m2m.movie_id2 from small_m2m m2m "
                         "WHERE m2m.movie_id1 = {};"
                         "".format (con.escape (movie)));
#            cur.execute ("SELECT DISTINCT p2.movie_id from person p2 "
#                         "INNER JOIN person p1 ON p1.name = p2.name "
##                         "INNER JOIN movie m ON m.movie_id = p2.movie_id "
#                         "INNER JOIN small_dvd_movies sdm ON sdm.movie_id = p2.movie_id "
#                         "WHERE p1.movie_id = {} "
#                         "ORDER BY p2.movie_id;"
#                         "".format(con.escape (movie)))           
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
    insert = True
    con = mdb.connect('localhost', 'dvdeug', '', 'DVDs', use_unicode=True, charset="utf8")
    cur = con.cursor()
    cur.execute ("SET NAMES 'utf8'")
    cur.execute ("CREATE TEMPORARY TABLE small_m2m "
                 "(movie_id1 SMALLINT (5) UNSIGNED NOT NULL, "
                 "movie_id2 SMALLINT (5) UNSIGNED NOT NULL, "
                 "INDEX mid_idx (movie_id1));")
    cur.execute ("INSERT INTO small_m2m "
                 "SELECT DISTINCT m1.movie_id, m2.movie_id FROM movie m1 "
                 "INNER JOIN person p1 ON p1.movie_id = m1.movie_id "
                 "INNER JOIN person p2 ON p1.name = p2.name "
                 "INNER JOIN movie m2 on p2.movie_id = m2.movie_id AND m2.have_watched "
                 "WHERE m1.have_watched;")
#    cur.execute ("CREATE TEMPORARY TABLE small_dvd_movies "
#                 "(movie_id SMALLINT (5) UNSIGNED UNIQUE NOT NULL, "
#                 "INDEX mid_idx (movie_id)); ")
##                 "FOREIGN KEY (movie_id) REFERENCES movie(movie_id));")
#    cur.execute ('INSERT INTO small_dvd_movies '
#                 'SELECT distinct movie_id FROM dvd d '
#                 'INNER JOIN dvd_contents dc ON dc.dvd_id = d.dvd_id '
#                 'WHERE d.dvd_id NOT IN '
#                 '(SELECT dvd_id FROM dvd_tags WHERE tag = "large movie pack");');
#    cur.execute ('INSERT IGNORE INTO small_dvd_movies '
#                 'SELECT movie_id FROM movie WHERE have_watched;')
# Didn't hugely improve speed; need to test again
#    cur.execute ('CREATE TEMPORARY TABLE sperson1 '
#                 '(movie_id smallint (5) UNSIGNED NOT NULL, '
#                 'name varchar(180) NOT NULL, '
#                 'PRIMARY KEY (movie_id, name)) DEFAULT CHARSET=utf8mb4;')
#    cur.execute ('INSERT INTO sperson1 '
#                 'SELECT p.movie_id, name FROM person p INNER JOIN small_dvd_movies s '
#                 'ON s.movie_id = p.movie_id;')
# Can't join a temporary table to itself!?! Duplicate it, I guess.
#    cur.execute ('CREATE TEMPORARY TABLE sperson2 '
#                 '(movie_id smallint (5) UNSIGNED NOT NULL, '
#                 'name varchar(180) NOT NULL, '
#                 'PRIMARY KEY (movie_id, name)) DEFAULT CHARSET=utf8mb4;')
#    cur.execute ('INSERT INTO sperson2 SELECT * FROM sperson1;')
    cur.execute ("SELECT movie_id, bacon_num FROM moviebacon WHERE table_num = 2;")
    prior_bacon_nums = dict (cur.fetchall ())
    setup_end_time = time.clock ()
    print ("Setup complete: time taken {} seconds".format (setup_end_time - start_time))
    (global_movie_set, movie_tree) = calculate_movie_data (376)
    num_movies = len (global_movie_set)
    bacon_list = [(376, average_bacon_num (movie_tree, num_movies))]
    global_movie_set.remove (376)
    print ("One run of calculate_movie_data roughly {} seconds".format (time.clock () - setup_end_time))

    for movie in global_movie_set:
        bacon_list.append ((movie, average_bacon_num (calculate_movie_data (movie)[1], num_movies)))
    print ("Data collected: {} seconds from start".format (time.clock () - start_time));

    bacon_list.sort (key=lambda x: x[1])
    if insert:
        cur.execute ("DELETE FROM moviebacon WHERE table_num = 2;")
    for x in bacon_list:
        cur.execute ("SELECT name, year FROM movie WHERE movie_id = {};".format (x[0]));
        name = cur.fetchall ()
        if insert:
            cur.execute ("INSERT into moviebacon VALUES (2, {}, {});".format (x[0], x[1]))
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
    print ("Total time: {} seconds".format (time.clock() - start_time))
except mdb.Error as e:
    print (e)
    con.rollback ()
    sys.exit(1)
