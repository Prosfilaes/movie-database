#!/usr/bin/python
# -*- coding: utf-8 -*-

#import pymysql as mdb
import MySQLdb as mdb
import sys
import readline
import pylab
import pickle 

def calculate_initial_set (movie_id):
    movie_tree = [set((movie_id,))]
    movie_set = set ((movie_id,))
    i = 0
    while (len (movie_tree[i]) > 0):
        i += 1;
        movie_tree.append (set ())
        for movie in movie_tree[i - 1]:
            cur.execute ("SELECT DISTINCT p2.movie_id from person p2 "
                         "INNER JOIN person p1 ON p1.name = p2.name "
                         "WHERE p1.movie_id = {} ORDER BY p2.movie_id;"
                         "".format(con.escape (movie)))           
            newbies = cur.fetchall ()
            for newb in newbies:
                if newb[0] not in movie_set:
                    movie_set.add (newb [0])
                    movie_tree [i].add (newb[0])   
    return movie_set

def calculate_1_spread (movie_id):
    cur.execute ("SELECT DISTINCT p2.movie_id from person p2 "
                 "INNER JOIN person p1 ON p1.name = p2.name and p2.movie_id != p1.movie_id "
                 "WHERE p1.movie_id = {} ORDER BY p2.movie_id;"
                 "".format(con.escape (movie_id)))
    return cur.rowcount

def average_bacon_num (movie_tree, total_number_of_movies):
    total_bacon = 0
    for j in range (len (movie_tree)):
        total_bacon += j * len(movie_tree [j])
    return total_bacon / total_number_of_movies 

try:
    global con, cur
    rebuild_pickle = False
    num_connects = []
    bacon_num = []
    if rebuild_pickle:
        con = mdb.connect('localhost', 'dvdeug', '', 'DVDs', use_unicode=True, charset="utf8")
        cur = con.cursor()
        cur.execute ("SET NAMES 'utf8'")
        cur.execute ("SELECT movie_id, bacon_num FROM movie_bacon;")
        prior_bacon_nums = dict (cur.fetchall ())
        global_movie_set = calculate_initial_set (376)
        num_movies = len (global_movie_set)

        for movie in global_movie_set:
            num_connects.append (calculate_1_spread (movie))
            bacon_num.append (prior_bacon_nums [movie])

        con.rollback ()

        with open ('linreg_pickle', 'w') as f:
            pickle.dump (num_connects, f)
            pickle.dump (bacon_num, f)
    else:
        with open ('linreg_pickle', 'r') as f:
            num_connects = pickle.load (f)
            bacon_num = pickle.load (f)

    temp = sorted([(num_connects [i], bacon_num[i]) for i in range (0, len (num_connects))],key = lambda x:x[0])
    num_connects = [t[0] for t in temp]
    bacon_num = [t[1] for t in temp]
    fit = pylab.polyfit(num_connects, bacon_num, 2)
    fit_fn = pylab.poly1d(fit) # fit_fn is now a function which takes in x and returns an estimate for y

    pylab.plot(num_connects, bacon_num, 'yo', num_connects, fit_fn(num_connects), '--k')
    pylab.show ()


except mdb.Error as e:
    print (e)
    con.rollback ()
    sys.exit(1)
