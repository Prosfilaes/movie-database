#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pymysql as mdb
import sys
import readline

def calculate_person_data (name):
    people_tree = [set((name,))]
    people_set = set ((name,))
    i = 0
    while (len (people_tree[i]) > 0):
        i += 1;
        people_tree.append (set ())
        for person in people_tree[i - 1]:
            cur.execute ("SELECT DISTINCT p2.name from person p2 "
                         "INNER JOIN person p1 ON p1.movie_id = p2.movie_id "
                         "INNER JOIN movie m1 on p1.movie_id = m1.movie_id "
                         "INNER JOIN movie m2 on p2.movie_id = m2.movie_id "
                         "WHERE p1.name = {} AND m1.year < 1940 AND m2.year < 1940 "
                         "ORDER BY p2.name;"
                         "".format(con.escape (person)))           
            newbies = cur.fetchall ()
            for newb in newbies:
                if newb[0] not in people_set:
                    people_set.add (newb [0])
                    people_tree [i].add (newb[0])   
    return (people_set, people_tree)

def average_bacon_num (people_tree, total_number_of_people):
    total_bacon = 0
    for j in range (len (people_tree)):
        total_bacon += j * len(people_tree [j])
    return total_bacon / total_number_of_people 

try:
    global con, cur
    insert = False
    con = mdb.connect('localhost', 'dvdeug', '', 'DVDs', use_unicode=True, charset="utf8")
    cur = con.cursor()
    cur.execute ("SET NAMES 'utf8'")
    cur.execute ("SELECT person, bacon FROM bacon WHERE table_num = 1;")
    prior_bacon_nums = dict (cur.fetchall ())
    base_name = "Shirley Temple"
    (dana_person_set, people_tree) = calculate_person_data (base_name)
    num_people = len (dana_person_set)
    bacon_list = [(base_name, average_bacon_num (people_tree, num_people))]
    dana_person_set.remove (base_name)

    for person in dana_person_set:
        bacon_list.append ((person, average_bacon_num (calculate_person_data (person)[1], num_people)))

    bacon_list.sort (key=lambda x: x[1])
    for x in bacon_list:
        print ("{}: {:.4f}".format(x[0], x[1]), end = ";")
        if x[0] in prior_bacon_nums:
            print (" / old {:.4f} / change {:+.4f}"
                   "".format (prior_bacon_nums [x[0]],
                              x[1] - prior_bacon_nums [x[0]]));
        else:
            print (" / not previously in universe")
#    if insert:
#        con.commit ()
#    else:
    con.rollback ()
except mdb.Error as e:
    print (e)
    sys.exit(1)
