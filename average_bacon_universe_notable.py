#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pymysql as mdb
import sys
import readline
import time

def calculate_person_data (person):
#    print (person)
#    print (con.escape(person))
#    sys.stdout.flush()
#    x = ('SELECT person_id FROM tmp_pid WHERE person = {};'.format (con.escape(person)));
#    print (x)
    cur.execute ('SELECT person_id FROM tmp_pid WHERE person = {};'.format (con.escape(person)));
    person_id = cur.fetchone()[0]
    people_tree = [set((person_id,))]
    people_set = set ((person_id,))
    i = 0
    while (len (people_tree[i]) > 0):
        i += 1;
        people_tree.append (set ())
        for person in people_tree[i - 1]:
            cur.execute ("SELECT person_id2 from tmp_p2p where person_id = {};".format (person));
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
    start_time = time.time ()
    insert = True
    con = mdb.connect('localhost', 'dvdeug', '', 'DVDs', use_unicode=True, charset="utf8")
    cur = con.cursor()
    cur.execute ("SET NAMES 'utf8'")
    cur.execute ("SELECT person, bacon_num FROM actorbacon WHERE table_num = 3;")
    prior_bacon_nums = dict (cur.fetchall ())
    cur.execute ("DROP TABLE IF EXISTS tmp_pid;")
    cur.execute ("DROP TABLE IF EXISTS tmp_p2p;")
    cur.execute ("CREATE TABLE tmp_pid (person_id smallint(5) unsigned NOT NULL AUTO_INCREMENT, person varchar(180) NOT NULL, PRIMARY KEY (person_id), KEY (person)) DEFAULT CHARSET=utf8mb4;")
    cur.execute ("INSERT INTO tmp_pid SELECT null, person FROM (SELECT DISTINCT person FROM actor) as a;") 
    cur.execute ("CREATE TEMPORARY TABLE tmp_p2p (person_id smallint(5) unsigned NOT NULL, person_id2 smallint(5) unsigned NOT NULL, PRIMARY KEY(person_id, person_id2));")
    con.commit ()
    if True:
        cur.execute ("INSERT INTO tmp_p2p "
                     "SELECT DISTINCT pid1.person_id, pid2.person_id FROM actor a1 "
                     "INNER JOIN tmp_pid pid1 ON pid1.person = a1.person "
                     "INNER JOIN actor a2 ON a2.movie_id = a1.movie_id AND a1.person != a2.person "
                     "INNER JOIN tmp_pid pid2 ON a2.person = pid2.person;")
    setup_end_time = time.time ()
#   print (setup_end_time - start_time)
#    sys.stdout.flush()   
#    exit ()

    root_id = "Dana Hill (I)"
    (dana_person_set, people_tree) = calculate_person_data (root_id)
    num_people = len (dana_person_set)
    total_person_set = set ()
    bacon_list = [(root_id, average_bacon_num (people_tree, num_people))]
    
    cur.execute ("SELECT person FROM notable_actor;");
    notable_people = cur.fetchall()
    printed_num_people = len (notable_people) + 1
    print ("Total number of people: ", printed_num_people)
    sys.stdout.flush()
    for person in notable_people:
#        print ("#" + person)
#        sys.stdout.flush()
        if person[0] != root_id:
            bacon_list.append ((person[0], average_bacon_num (calculate_person_data (person[0])[1], num_people)))

    data_collection_time = time.time ()
    bacon_list.sort (key=lambda x: x[1])
    if insert:
        cur.execute ("DELETE FROM actorbacon WHERE table_num = 3;")
    for x in bacon_list:
        if insert:
            cur.execute ("INSERT into actorbacon VALUES (3, {}, {});".format (
                    con.escape(x[0]), x[1]));
##        cur.execute ("SELECT person from person_name where person = {};".format (x[0]))
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
    final_time = time.time ()
    print ("Setup: {:.2f}s; travelling time: {:.2f}s; per person: {:.4f}s; total: {:.2f}s"
           "".format (setup_end_time - start_time, data_collection_time - setup_end_time,
                      (data_collection_time - setup_end_time) / printed_num_people,
                      final_time - start_time))
except mdb.Error as e:
    print (e)
    sys.exit(1)
finally:
    cur.execute ("DROP TABLE IF EXISTS tmp_pid;")
    cur.execute ("DROP TABLE IF EXISTS tmp_p2p;")
