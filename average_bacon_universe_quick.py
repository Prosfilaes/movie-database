#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pymysql as mdb
import sys
import readline
import time

def calculate_person_data (person_id):
    people_tree = [set((person_id,))]
    people_set = set ((person_id,))
    i = 0
    while (len (people_tree[i]) > 0):
        i += 1;
        people_tree.append (set ())
        for person in people_tree[i - 1]:
            cur.execute ("SELECT DISTINCT p2.person_id from movie_people p2 "
                         "INNER JOIN movie_people p1 ON p1.movie_id = p2.movie_id "
                         "WHERE p1.person_id = {};"
                         "".format(person))
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
    start_time = time.clock ()
    insert = True
    con = mdb.connect('localhost', 'dvdeug', '', 'DVDs', use_unicode=True, charset="utf8")
    cur = con.cursor()
    cur.execute ("SET NAMES 'utf8'")
    cur.execute ("SELECT person_id, bacon_num FROM bacon WHERE table_num = 2;")
    prior_bacon_nums = dict (cur.fetchall ())
    setup_end_time = time.clock ()
#    con.rollback ()
    root_id = 1307 # Dana Hill is 1307
    (dana_person_set, people_tree) = calculate_person_data (root_id)
    num_people = len (dana_person_set)
    cur.execute ("SELECT person_id FROM movie_people WHERE person_id in {} "
                 "GROUP BY person_id HAVING COUNT(*) > 1;"
                 "".format (tuple (dana_person_set)))
    total_person_set = set ([a[0] for a in cur.fetchall()])
    printed_num_people = len (total_person_set)
    print ("Total number of people: ", printed_num_people)
    bacon_list = [(root_id, average_bacon_num (people_tree, num_people))]
    total_person_set.remove (root_id)

    for person in total_person_set:
#        print ("#" + person)
#        sys.stdout.flush()
        bacon_list.append ((person, average_bacon_num (calculate_person_data (person)[1], num_people)))

    data_collection_time = time.clock ()
    bacon_list.sort (key=lambda x: x[1])
    if insert:
        cur.execute ("DELETE FROM bacon WHERE table_num = 2;")
    for x in bacon_list:
        if insert:
            cur.execute ("INSERT into bacon VALUES (2, {}, {});".format (
                    x[0], x[1]));
        cur.execute ("SELECT person from person_name where person_id = {};".format (x[0]))
        print ("{}: {:.4f}".format(cur.fetchone()[0], x[1]), end = ";")
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
    print ("Setup: {:.2f}s; travelling time: {:.2f}s; per person: {:.4f}s; total: {:.2f}s"
           "".format (setup_end_time - start_time, data_collection_time - setup_end_time,
                      (data_collection_time - setup_end_time) / printed_num_people,
                      final_time - start_time))
except mdb.Error as e:
    print (e)
    sys.exit(1)
