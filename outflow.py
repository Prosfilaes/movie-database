#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pymysql as mdb
import sys
import readline

try:
    global con, cur
    con = mdb.connect('localhost', 'dvdeug', '', 'DVDs', use_unicode=True, charset="utf8")
    cur = con.cursor()
    cur.execute ("SET NAMES 'utf8'")

    cur.execute ("CREATE TEMPORARY TABLE outflow (movie_id SMALLINT(5), outflow SMALLINT(5) UNSIGNED);")
    cur.execute ("SELECT movie_id FROM movie;")
    movie_ids = [i[0] for i in cur.fetchall ()]
    for mi in movie_ids:
        cur.execute ("insert into outflow (select {0}, COUNT(*) "
                    "from "
                        "(select m1.movie_id from person p1 "
                        "inner join person p2 on p1.name = p2.name "
                        "inner join movie m1 on p1.movie_id = m1.movie_id "
                        "inner join movie m2 on p2.movie_id = m2.movie_id "
                        "where m1.movie_id = {0} and m1.movie_id != m2.movie_id "
                        "group by m2.movie_id order by m2.year) as c);".format (mi))
    cur.execute ("SELECT m.name, m.year, o.outflow, mb.bacon_num  FROM outflow o "
                "INNER JOIN movie_bacon mb ON o.movie_id = mb.movie_id "
                "INNER JOIN movie m ON m.movie_id = o.movie_id "
                "ORDER BY o.outflow, mb.bacon_num;")
    i = 0
    for movie in cur.fetchall ():
        i += 1
        print ("{:3} {} ({}): {}, {:.4f}".format (i, movie[0], movie[1], movie[2], movie[3]))
    con.rollback ()
except mdb.Error as e:
    print (e)
    con.rollback ()
    sys.exit(1)
