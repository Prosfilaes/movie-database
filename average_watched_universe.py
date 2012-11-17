#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pymysql as mdb
import sys
import readline

def calculate_movie_data (movie_id):
    movie_tree = [set((movie_id,))]
    movie_set = set ((movie_id,))
    i = 0
    while (len (movie_tree[i]) > 0):
        i += 1;
        movie_tree.append (set ())
        for movie in movie_tree[i - 1]:
            cur.execute ("SELECT DISTINCT p2.movie_id from person p2 "
                         "INNER JOIN person p1 ON p1.name = p2.name "
                         "INNER JOIN movie m ON m.movie_id = p2.movie_id "
                         "WHERE p1.movie_id = {} AND m.have_watched "
                         "ORDER BY p2.movie_id;"
                         "".format(con.escape (movie)))           
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
    global con, cur
    insert = True
    con = mdb.connect('localhost', 'dvdeug', '', 'DVDs', use_unicode=True, charset="utf8")
    cur = con.cursor()
    cur.execute ("SET NAMES 'utf8'")
    cur.execute ("SELECT movie_id, bacon_num FROM moviebacon WHERE table_num = 3;")
    prior_bacon_nums = dict (cur.fetchall ())
    if insert:
        cur.execute ("DELETE FROM moviebacon WHERE table_num = 3;")
    (global_movie_set, movie_tree) = calculate_movie_data (376)
    num_movies = len (global_movie_set)
    bacon_list = [(376, average_bacon_num (movie_tree, num_movies))]
    global_movie_set.remove (376)

    for movie in global_movie_set:
        bacon_list.append ((movie, average_bacon_num (calculate_movie_data (movie)[1], num_movies)))
    bacon_list.sort (key=lambda x: x[1])
    for x in bacon_list:
        cur.execute ("SELECT name, year FROM movie WHERE movie_id = {};".format (x[0]));
        name = cur.fetchall ()
        if insert:
            cur.execute ("INSERT into moviebacon VALUES (3, {}, {});".format (x[0], x[1]))
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
except mdb.Error as e:
    print (e)
    con.rollback ()
    sys.exit(1)
