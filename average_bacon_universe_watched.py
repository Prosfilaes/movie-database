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
                         "INNER JOIN movie m ON m.movie_id = p2.movie_id "
                         "WHERE p1.name = {} AND m.have_watched "
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
    insert = True
    con = mdb.connect('localhost', 'dvdeug', '', 'DVDs', use_unicode=True, charset="utf8")
    cur = con.cursor()
    cur.execute ("SET NAMES 'utf8'")
    cur.execute ("SELECT person, bacon_num FROM bacon where table_num = 3;")
    prior_bacon_nums = dict (cur.fetchall ())
    if insert:
        cur.execute ("DELETE FROM bacon where table_num = 3;")
    (total_person_set, people_tree) = calculate_person_data ("Dana Hill")
    num_people = len (total_person_set)
#    cur.execute ("SELECT name FROM person WHERE name in {} GROUP BY name HAVING COUNT(*) > 1;"
#                 "".format (tuple (dana_person_set)))
#    total_person_set = set ([a[0] for a in cur.fetchall()])
    print ("Total number of people: ", num_people)
    bacon_list = [("Dana Hill", average_bacon_num (people_tree, num_people))]
    total_person_set.remove ("Dana Hill")

    for person in total_person_set:
        bacon_list.append ((person, average_bacon_num (calculate_person_data (person)[1], num_people)))

    bacon_list.sort (key=lambda x: x[1])
    for x in bacon_list:
        if insert:
            cur.execute ("INSERT into bacon VALUES (3, {}, {});".format (
                    con.escape (x[0]), x[1]));
        print ("{}: {:.4f}".format(x[0], x[1]), end = ";")
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
    sys.exit(1)
