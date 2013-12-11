#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pymysql as mdb
import sys
import readline
import time
import graph_bacon

def create_table (table_num, first_name):
    # Weird names so we don't touch working code
    cur.execute ("CREATE TEMPORARY TABLE m2m "
                 "(person1 varchar(180) NOT NULL, "
                 "person2 varchar(180) NOT NULL, "
                 "INDEX mid_idx (person1)) DEFAULT CHARSET=utf8mb4;")
    # We need to factor out the cut and paste between 6 and 9.
    if table_num not in [1, 6, 7, 8, 9]:
        assert False, "All but 1, 6, 8 and 9 are unimplemented"
    if table_num == 1:
        cur.execute ("INSERT INTO m2m "
                     "SELECT DISTINCT p1.person, p2.person FROM actor p1 "
                     "INNER JOIN actor p2 ON p1.movie_id = p2.movie_id AND p1.person != p2.person "
                     "WHERE p1.person IN (SELECT person FROM actor group by person HAVING COUNT(*) > 1) "
                     "AND p2.person IN (SELECT person FROM actor group by person HAVING COUNT(*) > 1) "
                     ";")
                     #"SELECT DISTINCT p1.movie_id, p2.movie_id FROM actor p1 "
                     #"INNER JOIN actor p2 ON p1.person = p2.person AND p1.movie_id != p2.movie_id;")
    elif table_num == 2 or table_num == 5:
        cur.execute ("CREATE TEMPORARY TABLE small_dvd_movies "
                     "(movie_id SMALLINT (5) UNSIGNED UNIQUE NOT NULL, "
                     "INDEX mid_idx (movie_id)); ")
        if table_num == 2:
            cur.execute ('INSERT INTO small_dvd_movies '
                         'SELECT DISTINCT movie_id FROM dvd d '
                         'INNER JOIN dvd_contents dc ON dc.dvd_id = d.dvd_id '
                         'WHERE d.dvd_id NOT IN '
                         '(SELECT dvd_id FROM dvd_tags WHERE tag = "large movie pack");');
            cur.execute ('INSERT IGNORE INTO small_dvd_movies '
                         'SELECT movie_id FROM movie WHERE have_watched;')
        elif table_num == 5:
            #The full length only version of the above
            cur.execute ('INSERT INTO small_dvd_movies '
                         'SELECT DISTINCT m.movie_id FROM dvd d '
                         'INNER JOIN dvd_contents dc ON dc.dvd_id = d.dvd_id '
                         'INNER JOIN movie m ON dc.movie_id = m.movie_id AND m.is_full_length '
                         'WHERE d.dvd_id NOT IN '
                         '(SELECT dvd_id FROM dvd_tags WHERE tag = "large movie pack");');
            cur.execute ('INSERT IGNORE INTO small_dvd_movies '
                         'SELECT movie_id FROM movie WHERE have_watched and is_full_length;')
        else:
            assert True, "This should be unreachable"
        cur.execute ("INSERT INTO m2m "
                     "SELECT DISTINCT p1.movie_id, p2.movie_id FROM actor p1 "
                     "INNER JOIN actor p2 ON p1.person = p2.person AND p1.movie_id != p2.movie_id "
                     "WHERE p1.movie_id IN (SELECT movie_id from small_dvd_movies); ")  
        #The natural formulation doesn't work in MySQL, since you can't reference the temporary table small_dvd_movies
        #twice in one statement
        cur.execute ("DELETE FROM m2m WHERE movie_id2 NOT IN (SELECT movie_id from small_dvd_movies);")
    elif table_num == 3:
        cur.execute ("INSERT INTO m2m "
                     "SELECT DISTINCT m1.movie_id, m2.movie_id FROM movie m1 "
                     "INNER JOIN actor p1 ON p1.movie_id = m1.movie_id "
                     "INNER JOIN actor p2 ON p1.person = p2.person "
                     "INNER JOIN movie m2 on p2.movie_id = m2.movie_id AND m2.have_watched "
                     "WHERE m1.have_watched;")
    elif table_num == 4:
        cur.execute ("INSERT INTO m2m "
                     "SELECT DISTINCT p1.movie_id, p2.movie_id FROM actor p1 "
                     "INNER JOIN actor p2 "
                     "ON p1.person = p2.person AND p1.movie_id != p2.movie_id "
                     "INNER JOIN movie m1 ON p1.movie_id = m1.movie_id AND m1.is_full_length "
                     "INNER JOIN movie m2 ON p2.movie_id = m2.movie_id AND m2.is_full_length "
                     ";")
    elif table_num == 6:
        cur.execute ("CREATE TEMPORARY TABLE single_movie_dvd_movies "
                     "(movie_id SMALLINT (5) UNSIGNED UNIQUE NOT NULL, "
                     "INDEX mid_idx (movie_id)); ")
        cur.execute ('INSERT INTO single_movie_dvd_movies '
                     'SELECT DISTINCT movie_id FROM movie where is_full_length AND have_watched;');
        cur.execute ("CREATE TEMPORARY TABLE single_movie_dvd_actors "
                     "(person varchar(180)) DEFAULT CHARSET = utf8mb4;")
        cur.execute ("INSERT INTO single_movie_dvd_actors "
                     "SELECT person FROM actor WHERE movie_id IN (SELECT movie_id FROM single_movie_dvd_movies) "
                     "GROUP BY person HAVING COUNT(*) > 1;")
        cur.execute ("CREATE TEMPORARY TABLE single_movie_dvd_actors2 "
                     "(person varchar(180)) DEFAULT CHARSET = utf8mb4;")
        cur.execute ("INSERT INTO single_movie_dvd_actors2 "
                     "SELECT * FROM single_movie_dvd_actors;");
        cur.execute ("INSERT INTO m2m "
                     "SELECT DISTINCT p1.person, p2.person FROM actor p1 "
                     "INNER JOIN actor p2 ON p1.movie_id = p2.movie_id AND p1.person != p2.person "
                     "INNER JOIN single_movie_dvd_movies s ON s.movie_id = p1.movie_id "
                     "INNER JOIN single_movie_dvd_actors s1 on p1.person = s1.person "
                     "INNER JOIN single_movie_dvd_actors2 s2 on p2.person = s2.person;")
        #cur.execute ("INSERT INTO m2m "
        #             "SELECT DISTINCT m1.movie_id, m2.movie_id FROM movie m1 "
        #             "INNER JOIN actor p1 ON p1.movie_id = m1.movie_id "
        #             "INNER JOIN actor p2 ON p1.person = p2.person "
        #             "INNER JOIN movie m2 ON p2.movie_id = m2.movie_id AND m2.have_watched AND m2.is_full_length "
        #             "WHERE m1.have_watched AND m1.is_full_length;")
    elif table_num == 7:
        cur.execute ("CREATE TEMPORARY TABLE tv_actors "
                     "(person varchar(180)) DEFAULT CHARSET = utf8mb4;")
        cur.execute ("INSERT INTO tv_actors "
                     "SELECT person FROM actor natural join tv_show group by person HAVING COUNT(*) > 1;")
        cur.execute ("INSERT INTO m2m "
                     "SELECT DISTINCT p1.person, p2.person FROM actor p1 "
                     "INNER JOIN actor p2 ON p1.movie_id = p2.movie_id AND p1.person != p2.person "
                     "INNER JOIN tv_actors ON tv_actors.person = p1.person "
                     "INNER JOIN tv_show ON tv_show.movie_id = p1.movie_id "
                     ";")
        print ("Insertion complete.", file=sys.stderr)
        cur.execute ("DELETE FROM m2m WHERE person2 NOT IN (SELECT person FROM tv_actors);")
        print ("Uninsertion complete.", file=sys.stderr)
        #cur.execute ("INSERT INTO m2m "
        #             "SELECT DISTINCT p1.movie_id, p2.movie_id FROM actor p1 "
        #             "INNER JOIN actor p2 "
        #             "ON p1.person = p2.person AND p1.movie_id != p2.movie_id "
        #             "INNER JOIN movie m1 ON p1.movie_id = m1.movie_id  "
        #             "INNER JOIN movie m2 ON p2.movie_id = m2.movie_id  "
        #             "WHERE m1.movie_id in (SELECT movie_id FROM tv_show) AND "
        #             "m2.movie_id in (SELECT movie_id FROM tv_show) "
        #             ";")
    elif table_num == 8:
        cur.execute ("CREATE TEMPORARY TABLE wfls_dvd_movies "
                     "(movie_id SMALLINT (5) UNSIGNED UNIQUE NOT NULL, "
                     "INDEX mid_idx (movie_id)); ")
        cur.execute ("INSERT INTO wfls_dvd_movies "
                     "SELECT DISTINCT m1.movie_id FROM movie m1 "
                     "INNER JOIN tags t1 ON t1.movie_id = m1.movie_id AND t1.tag = 'science fiction' "
                     "WHERE m1.have_watched AND m1.is_full_length;")
        cur.execute ("CREATE TEMPORARY TABLE sci_fi_actors "
                     "(person varchar(180)) DEFAULT CHARSET = utf8mb4;")
        cur.execute ("INSERT INTO sci_fi_actors "
                     "SELECT person FROM actor WHERE movie_id IN (SELECT movie_id FROM wfls_dvd_movies) "
                     "GROUP BY person HAVING COUNT(*) > 1;")
        cur.execute ("INSERT INTO m2m "
                     "SELECT DISTINCT p1.person, p2.person FROM actor p1 "
                     "INNER JOIN actor p2 ON p1.movie_id = p2.movie_id AND p1.person != p2.person "
                     "INNER JOIN wfls_dvd_movies s ON s.movie_id = p1.movie_id;")
        cur.execute ("DELETE FROM m2m WHERE person1 NOT IN (select person FROM sci_fi_actors);");
        cur.execute ("DELETE FROM m2m WHERE person2 NOT IN (select person FROM sci_fi_actors);");        
    elif table_num == 9:
        cur.execute ("CREATE TEMPORARY TABLE single_movie_dvd_movies "
                     "(movie_id SMALLINT (5) UNSIGNED UNIQUE NOT NULL, "
                     "INDEX mid_idx (movie_id)); ")
        cur.execute ('INSERT INTO single_movie_dvd_movies '
                     'SELECT DISTINCT movie_id FROM dvd d '
                     'INNER JOIN dvd_contents dc ON dc.dvd_id = d.dvd_id '
                     'GROUP BY d.dvd_ID HAVING COUNT(*) = 1;');
        cur.execute ("CREATE TEMPORARY TABLE single_movie_dvd_actors "
                     "(person varchar(180)) DEFAULT CHARSET = utf8mb4;")
        cur.execute ("INSERT INTO single_movie_dvd_actors "
                     "SELECT person FROM actor WHERE movie_id IN (SELECT movie_id FROM single_movie_dvd_movies) "
                     "GROUP BY person HAVING COUNT(*) > 1;")
        cur.execute ("CREATE TEMPORARY TABLE single_movie_dvd_actors2 "
                     "(person varchar(180)) DEFAULT CHARSET = utf8mb4;")
        cur.execute ("INSERT INTO single_movie_dvd_actors2 "
                     "SELECT * FROM single_movie_dvd_actors;");
        cur.execute ("INSERT INTO m2m "
                     "SELECT DISTINCT p1.person, p2.person FROM actor p1 "
                     "INNER JOIN actor p2 ON p1.movie_id = p2.movie_id AND p1.person != p2.person "
                     "INNER JOIN single_movie_dvd_movies s ON s.movie_id = p1.movie_id "
                     "INNER JOIN single_movie_dvd_actors s1 on p1.person = s1.person "
                     "INNER JOIN single_movie_dvd_actors2 s2 on p2.person = s2.person;")
    else:
        assert True, "table_nums above 9 are unknown"
    cur.execute ("SELECT * FROM m2m;")
    m2m = cur.fetchall ()
    # make this a list s.t. m2m_dict[i] = None or set()? Would that speed it up?
    m2m_dict = dict () 
    for i in m2m:
        if i[0] not in m2m_dict:
            m2m_dict[i[0]] = set ()    
        m2m_dict[i[0]].add (i[1])
        if i[1] not in m2m_dict:
            m2m_dict[i[1]] = set ()
        m2m_dict[i[1]].add (i[0])
    return m2m_dict

try:
    MAX_TABLENUM = 9
    # This is inappropriately intertangled in so many ways.
    # The appropriate thing would be to find the largest subset
    # instead of storing a value known to be in the largest subset.
    # That's more work, both coding and computational, and speed
    # matters for this code.
    #initial_movie_id = [None, 376, 376, 376, 376, 376, 376, 4169, 51, 376]
    initial_actor = "Frank Welker" # watched fl single DVD sci-fi movie actor + TV
    if (len(sys.argv) != 2 or int(sys.argv[1]) < 1 or
        int(sys.argv[1]) > MAX_TABLENUM):
        
        print ("This program takes one argument, the tablenum to calculate, in the range 1 .. {}."
               "".format (MAX_TABLENUM))
        sys.exit()
    table_num = int(sys.argv[1])
    start_time = time.clock ()
    global con, cur
    insert = True
    shortcut = True
    with open ("password", "r") as pass_file:
        l = pass_file.readline().split()
        username = l[0]
        password = l[1]
    con = mdb.connect('localhost', username, password, 'DVDs', use_unicode=True, charset="utf8")
    cur = con.cursor()
    cur.execute ("SET NAMES 'utf8'")
    m2m_dict = create_table (table_num, initial_actor)
    cur.execute ("SELECT person, bacon_num FROM actorbacon WHERE table_num = {};"
                 "".format(table_num))
    prior_bacon_nums = dict (cur.fetchall ())
    if len (prior_bacon_nums) == 0:
        prior_bacon_nums [""] = 1
    setup_end_time = time.clock ()
    root_id = initial_actor
    global_movie_set = graph_bacon.get_set_closure (m2m_dict, root_id)
    num_movies = len (global_movie_set)
    cur.execute ("SELECT description FROM moviebacon_tablenum WHERE table_num = {};"
                 "".format(table_num))
    table_name = cur.fetchone()[0]
    con.rollback () # Close transaction
    print ("The {} list following is about the relations of {} actors."
           "".format (table_name, num_movies))
    sys.stdout.flush()
    bacon_list = []
    if shortcut:
        zero_count = 0
    else:
        zero_count = -1
    for movie in global_movie_set:
        bacon_list.append ((movie, graph_bacon.average_bacon_num (m2m_dict, movie, num_movies)))
        if zero_count > -1:
            if bacon_list [-1][0] not in prior_bacon_nums:
                zero_count = -1
                continue
            if bacon_list[-1][1] == prior_bacon_nums [bacon_list[-1][0]]:
                zero_count += 1
            else:
                zero_count = -1
            if zero_count == 3:
                print ("Results haven't changed since last run; aborting.")
                sys.exit (0)       
    data_collection_time = time.clock ()
    print ("Data collection took {:.2f}s".format (data_collection_time - setup_end_time))
    bacon_list.sort (key=lambda x: x[1])
    if insert:
        cur.execute ("DELETE FROM actorbacon WHERE table_num = {};".format (table_num))
    for x in bacon_list:
        #cur.execute ("SELECT name, year FROM movie WHERE movie_id = {};".format (x[0]));
        name = x[0]
        if insert:
            cur.execute ("INSERT into actorbacon VALUES ({}, {}, {});".format (table_num, con.escape(name), x[1]))
        print ("{}: {:.4f}".format(name, x[1]), end = ';')
        if x[0] in prior_bacon_nums:
            print (" / old {:.4f} / change {:+.4f}"
                   "".format (prior_bacon_nums [name],
                              x[1] - prior_bacon_nums [name]));
        else:
            print (" / not previously in universe")
    if insert:
        con.commit ()
    else:
        con.rollback ()
    final_time = time.clock ()
    print ()
    print ("Setup: {:.2f}s; travelling time: {:.2f}s; per actor: {:.4f}s; total: {:.2f}s"
           "".format (setup_end_time - start_time, data_collection_time - setup_end_time,
                      (data_collection_time - setup_end_time) / num_movies,
                      final_time - start_time))
    print ("Prior Bacon nums: {:.2f} sum, {:.6f} avg; current Bacon nums: {:.2f} sum, {:.6f} avg"
           "".format (sum (prior_bacon_nums.values()), sum(prior_bacon_nums.values()) / len (prior_bacon_nums.values()),
                      sum ([x[1] for x in bacon_list]), sum ([x[1] for x in bacon_list]) / len (bacon_list)))
except mdb.Error as e:
    print (e)
    con.rollback ()
    sys.exit(1)