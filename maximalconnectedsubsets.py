#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pymysql as mdb
import sys
import readline

def show_one_step (person, cur_depth, max_depth):
    cur.execute ("SELECT DISTINCT p2.name from person p2 "
                 "INNER JOIN person p1 ON p1.movie_id = p2.movie_id "
                 "WHERE p1.name = {} ORDER BY p2.name;"
                 "".format(con.escape (person)))
    people = cur.fetchall ()
    for new_person in people:
#        print ('\t' * cur_depth, new_person[0])
        if cur_depth < max_depth:
            show_one_step (new_person, cur_depth + 1, max_depth)
        else:
            print (new_person [0])

try:
#    max_depth = 5
    global con, cur
    con = mdb.connect('localhost', 'dvdeug', '', 'DVDs', use_unicode=True, charset="utf8")
    cur = con.cursor()
    cur.execute ("SET NAMES 'utf8'")
    cur.execute ("SELECT DISTINCT name from person;")
    remaining_person_list = set ()
    for person in cur.fetchall ():
        remaining_person_list.add (person [0])
    group_num = 1
    while (len (remaining_person_list) > 0):
        if group_num == 1:
            first_person = "Dana Hill"
        else:
            first_person = remaining_person_list.pop ()
        people_tree = [set((first_person,))]
        people_set = set ((first_person,))
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

        print ("==Group {}==".format (group_num))
        print ("Total number of people: ", len (people_set))
        print
        for i in sorted (people_set):
            print (i)
        remaining_person_list = remaining_person_list - people_set
        group_num += 1

except mdb.Error as e:
    print (e)
    sys.exit(1)
