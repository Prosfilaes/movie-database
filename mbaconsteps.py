#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pymysql as mdb
import sys
import readline

#def show_one_step (movie, cur_depth, max_depth):
#    cur.execute ("SELECT DISTINCT p2.movie_id from person p2 "
#                 "INNER JOIN person p1 ON p1.name = p2.name "
#                 "WHERE p1.movie_id = {} ORDER BY p2.movie_id;"
#                 "".format(con.escape (movie)))
#    movies = cur.fetchall ()
#    for new_person in people:
#        print ('\t' * cur_depth, new_person[0])
#        if cur_depth < max_depth:
#            show_one_step (new_person, cur_depth + 1, max_depth)
#        else:
#            print (new_person [0])

def movieid_to_name (movie_id):
    cur.execute ("SELECT name from movie where movie_id = {};"
                 "".format (movie_id))
    return cur.fetchone () [0]

try:
#    max_depth = 5
    global con, cur
    con = mdb.connect('localhost', 'dvdeug', '', 'DVDs', use_unicode=True, charset="utf8")
    cur = con.cursor()
    cur.execute ("SET NAMES 'utf8'")
    starting_name = input ("Starting movie_id, please: ")
    movie_tree = [set((int(starting_name),))]
    movie_set = set ((int(starting_name),))
    i = 0
    while (len (movie_tree[i]) > 0):
        i += 1;
        movie_tree.append (set ())
        for movie in movie_tree[i - 1]:
            cur.execute ("SELECT DISTINCT p2.movie_id from movie_people p2 "
                         "INNER JOIN movie_people p1 ON p1.person_id = p2.person_id "
                         "WHERE p1.movie_id = {} ORDER BY p2.movie_id;"
                         "".format(con.escape (movie)))     
            newbies = cur.fetchall ()
            for newb in newbies:
                if newb[0] not in movie_set:
                    movie_set.add (newb [0])
                    movie_tree [i].add (newb[0])
    print ("Total number of movie: ", len (movie_set))
    for j in range (i):
        print
        print (j)
        for p in sorted ([movieid_to_name (k) for k in movie_tree [j]]):
            print (p)
except mdb.Error as e:
    print (e)
    sys.exit(1)
