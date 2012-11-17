#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pymysql as mdb
import sys
import readline

try:
#    max_depth = 5
    global con, cur
    con = mdb.connect('localhost', 'dvdeug', '', 'DVDs', use_unicode=True, charset="utf8")
    cur = con.cursor()
    cur.execute ("SET NAMES 'utf8'")
    starting_name = input ("Starting name, please: ")
    people_tree = [set((starting_name,))]
    people_set = set ((starting_name,))
    i = 0
    while (len (people_tree[i]) > 0):
        i += 1;
        people_tree.append (set ())
        for person in people_tree[i - 1]:
            cur.execute ("SELECT DISTINCT p2.name from person p2 "
                         "INNER JOIN person p1 ON p1.movie_id = p2.movie_id "
                         "WHERE p1.name = {} ORDER BY p2.name;"
                         "".format(con.escape (person)))           
            newbies = cur.fetchall ()
            for newb in newbies:
                if newb[0] not in people_set:
                    people_set.add (newb [0])
                    people_tree [i].add (newb[0])
    print ("Total number of people: ", len (people_set))
    bacon_num = 0
    for j in range (i):
        bacon_num += j * len (people_tree [j])
    bacon_num = bacon_num * 1.0 / len (people_set)
    print ("Bacon number: ", bacon_num)
    for j in range (i):
        print
        print (j)
        for p in sorted (people_tree [j]):
            print (p)
except mdb.Error as e:
    print (e)
    sys.exit(1)
