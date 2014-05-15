import scala.slick.session.Database
import scala.slick.jdbc.{GetResult, StaticQuery => Q}
import Database.threadLocalSession
import Q.interpolation

import scala.io.Source
import java.io._

import graphBacon._

object mainBody {
  val (username, password) = 
    {
      val passChunks = Source.fromFile("password").getLines.next.split (" ")
      (passChunks.head, passChunks.tail.head)
    }

  val actorConnectionsSQL = Map (
    (1, 
     """SELECT person, movie_id FROM actor;"""
   ),
    (2, 
     """SELECT person, movie_id FROM actor NATURAL JOIN movie m WHERE m.have_watched
     UNION
     SELECT DISTINCT person, movie_id FROM actor NATURAL JOIN dvd_contents
     WHERE dvd_id NOT IN (SELECT dvd_id FROM dvd_tags where tag = "large movie pack");"""
   ),
    (3,
     """SELECT person, movie_id FROM actor NATURAL JOIN movie m WHERE m.have_watched;"""
   ),
    (4,
     """SELECT person, movie_id FROM actor NATURAL JOIN movie m
     WHERE m.is_full_length;"""
   ),
    (5, 
     """SELECT person, movie_id FROM actor NATURAL JOIN movie m 
     WHERE m.have_watched AND m.is_full_length
     UNION
     SELECT DISTINCT person, movie_id FROM actor NATURAL JOIN movie m NATURAL JOIN dvd_contents
     WHERE dvd_id NOT IN (SELECT dvd_id FROM dvd_tags where tag = "large movie pack")
     AND m.is_full_length;"""
   ),
    (6,
     """SELECT person, movie_id FROM actor NATURAL JOIN movie m
     WHERE m.is_full_length AND m.have_watched;"""
   ),
    (7, 
     """SELECT person, movie_id FROM actor NATURAL JOIN tv_show t;"""
   ),
    (8, 
     """SELECT DISTINCT person, movie_id FROM actor NATURAL JOIN movie m NATURAL JOIN tags t
     WHERE t.tag = "science fiction" AND m.have_watched AND m.is_full_length;"""
   ),
    (9,
     """SELECT DISTINCT person, movie_id FROM actor NATURAL JOIN dvd_contents WHERE
     dvd_id IN (SELECT dvd_id FROM dvd_contents GROUP BY dvd_id HAVING COUNT(*) = 1);"""
   ),    
    (10, 
     """SELECT person, movie_id FROM actor NATURAL JOIN tv_show t 
     NATURAL JOIN movie m WHERE m.have_watched;"""
   ),
    (11, 
     """SELECT person, movie_id FROM actor NATURAL JOIN tags t 
     WHERE t.tag = "animation";"""
   ),
    (21,
     """SELECT person, movie_id FROM actor NATURAL JOIN movie m WHERE m.year < 1920;"""
   ),
   (22,
     """SELECT person, movie_id FROM actor NATURAL JOIN movie m WHERE m.year >= 1920 AND m.year < 1930;"""
   ),
   (23,
     """SELECT person, movie_id FROM actor NATURAL JOIN movie m WHERE m.year >= 1930 AND m.year < 1940;"""
   ),
   (24,
     """SELECT person, movie_id FROM actor NATURAL JOIN movie m WHERE m.year >= 1940 AND m.year < 1950;"""
   ),
   (25,
     """SELECT person, movie_id FROM actor NATURAL JOIN movie m WHERE m.year >= 1950 AND m.year < 1960;"""
   ),
   (26,
     """SELECT person, movie_id FROM actor NATURAL JOIN movie m WHERE m.year >= 1960 AND m.year < 1970;"""
   ),
   (27,
     """SELECT person, movie_id FROM actor NATURAL JOIN movie m WHERE m.year >= 1970 AND m.year < 1980;"""
   ),
   (28,
     """SELECT person, movie_id FROM actor NATURAL JOIN movie m WHERE m.year >= 1980 AND m.year < 1990;"""
   ),
   (29,
     """SELECT person, movie_id FROM actor NATURAL JOIN movie m WHERE m.year >= 1990 AND m.year < 2000;"""
   ),
   (30,
     """SELECT person, movie_id FROM actor NATURAL JOIN movie m WHERE m.year >= 2000 AND m.year < 2010;"""
   ),
   (31,
     """SELECT person, movie_id FROM actor NATURAL JOIN movie m WHERE m.year >= 2010 AND m.year < 2020;"""
   )
  )

  // Table definition if we use more abstract database interfaces in the future
  // object Actors extends Table[(String, Int)]("actor") {
  // def person = column[String]("person")
  // def movie_id = column[Int]("movie_id")
  // def * = person ~ movie_id
  // }

  // Returns (Table Description, actor2actor list, map from actor to previous avg. bacon number, list of movies)
  def readInitialDatabase (tableNumber: Int) : (String, List[(String, Int)], Map[String, Float], 
						Map[Int, Float], Map[Int, String], Map [Int, (String, Int)]) 
  = {
    Database.forURL("jdbc:mysql://localhost:3306/DVDs", driver = "com.mysql.jdbc.Driver", 
		    user=username, password=password) withSession {
      val actorConnections = Q.query[Unit, (String, Int)] (actorConnectionsSQL (tableNumber)).list ()
      val priorActorBaconNums = Q.query[Int, (String, Float)] (
	"SELECT person, bacon_num FROM actorbacon WHERE table_num = ?;").list(tableNumber).toMap
      val priorMovieBaconNums = Q.query[Int, (Int, Float)] (
	"SELECT movie_id, bacon_num FROM moviebacon WHERE table_num = ?;").list(tableNumber).toMap
      val tableDescription = Q.query[Int, String] (
	"SELECT description FROM moviebacon_tablenum WHERE table_num = ?;").list(tableNumber).head
      val movieDescriptions = Q.query[Unit, (Int, String, Int)] ("SELECT movie_id, name, year FROM movie;").
	list().map (x => (x._1, (x._2, x._3))).toMap
      val movieNames = Q.query[Unit, (Int, String)] ("SELECT movie_id, name FROM movie;").list().toMap
      (tableDescription, actorConnections, priorActorBaconNums, priorMovieBaconNums, movieNames, movieDescriptions)
    }
  }

  def storeActorBaconNumbers (tableNumber: Int, baconNumbers: Iterable [(String, graphBacon.Real)]): Unit = {
    Database.forURL("jdbc:mysql://localhost:3306/DVDs", driver = "com.mysql.jdbc.Driver", user=username, 
		    password=password) withSession {
      (Q.u + "DELETE FROM actorbacon WHERE table_num = " +? tableNumber + ";").execute
      for (bn <- baconNumbers) {
	(Q.u + "INSERT INTO actorbacon VALUES (" +? tableNumber + ", " +? bn._1 + ", " +? bn._2 + ");").execute
      }
    }
  }

  def storeMovieBaconNumbers (tableNumber: Int, baconNumbers: Iterable [(Int, graphBacon.Real)]): Unit = {
    Database.forURL("jdbc:mysql://localhost:3306/DVDs", driver = "com.mysql.jdbc.Driver", user=username, 
		    password=password) withSession {
      (Q.u + "DELETE FROM moviebacon WHERE table_num = " +? tableNumber + ";").execute
      for (bn <- baconNumbers) {
	(Q.u + "INSERT INTO moviebacon VALUES (" +? tableNumber + ", " +? bn._1 + ", " +? bn._2 + ");").execute
      }
    }
  }

  // Given a list of (a, b), remove all the a's that only appear once
  def non_unique [A, B](a : Iterable[(A, B)]) = a.groupBy (_._1).filter (_._2.size > 1).values.flatten

  // Transforms a list of (A, B) pairs to a map from A's to a set of other A's that share a B
  def connect [A, B](a : Iterable[(A, B)]) = {
    def explode (a : Iterable [A]) = {
      val aSet = a.toSet
      for (person <- aSet) yield (person, aSet - person)
    }
    a.groupBy (_._2).map (_._2.map(_._1)).flatMap (explode).groupBy (_._1).
    mapValues (_.map (_._2).reduce (_ ++ _))
  }

  class runTimes (val mysqlTime : Float, val setupTime : Float, val travellingTime : Float) {
    def totalTime = mysqlTime + setupTime + travellingTime
  }

  // I acknowledge that internationalized code needs more care then this. This is unlikely
  // to ever need internationalized. Even plural concerns are irrelevant; this is a silly report
  // on one element.
  def reportOutHeader (where: PrintWriter, who: String, description: String, size: Integer) = {
    where.println ("This " + description + " list following is about the relations of " + 
		   size.toString + " " + who + ".");
    where.flush()
  }

  val noChangeLimit = 0.00001
  def noChangeOut (where: PrintWriter) = {
    where.println ("Results haven't changed since last run; aborting.");
  }

  def reportOut[A] (where: PrintWriter, who: String, data : Map [A, graphBacon.Real], 
		 priorData : Map [A, Float], t : runTimes, names : A => String) = 
  {
    val sortedData = data.toIndexedSeq.sortBy (_._2)
    for (a <- sortedData) {
      val bacon = a._2
      where.write (names(a._1) ++ f": $bacon%.4f")
      if (priorData.contains (a._1)) {
	val prior = priorData (a._1)
	val diff = bacon - prior
	if (scala.math.abs(diff) < noChangeLimit) // That is, a "0.0000" represents values in [0.00001 .. 0.0001)
	  where.println (" / no change")
	else
	  where.println (f" / old $prior%.4f / change $diff%+.4f")
      }
	else where.println (" / not previously in universe")
      }
    where.println ()
    val perDataTime = t.travellingTime / sortedData.length
    where.println (
      f"MySQL time: ${t.mysqlTime}%.2fs; setup: ${t.setupTime}%.2fs; travelling time: " ++
      f"${t.travellingTime}%.2fs; per $who: $perDataTime%.4fs; total: ${t.totalTime}%.2fs")
    val sumBacon = sortedData.map(_._2).reduce (_ + _)
    val avgBacon = sumBacon / sortedData.length
    if (priorData.size == 0) {
      where.println (f"Current Bacon nums: $sumBacon%.2f sum, $avgBacon%.4f avg")
    }
    else {
      val sumOldBacon = priorData.map(_._2).reduce (_ + _)
      val avgOldBacon = sumOldBacon / priorData.size
      where.println (f"Prior Bacon nums: $sumOldBacon%.2f sum, $avgOldBacon%.4f avg; current Bacon " ++
			   f"nums: $sumBacon%.2f sum, $avgBacon%.4f avg")
    }
  }

  def main (args: Array[String]): Unit = {
    try {
      val startTime = System.currentTimeMillis()

      if (args.size != 3) {
	println ("This program takes three arguments, the table number, the actor filename and the movie filename")
	return
      }
      val tableNumber = args(0).toInt
      if (tableNumber == 12) {
	mainDoubleBody.start (args(2))
	return
      }
      
      val (tableDescription, actorConnections, priorActorBacon, priorMovieBacon, movieNames, movieDescriptions) = 
	readInitialDatabase (tableNumber);
      val mysqlTime = System.currentTimeMillis()
      
      val actor2Actor = connect (non_unique (actorConnections))
      val movie2Movie = connect (actorConnections.map (x => (x._2, x._1)))
      val setupEndTime = System.currentTimeMillis()
      val reachingStart = 
	if (tableNumber <= 12) "Mel Blanc"
	else if (tableNumber == 21) "Charles Chaplin"
	else if (tableNumber == 22) "Buster Keaton"
	else if (tableNumber == 23 || tableNumber == 24 || tableNumber == 25) "Bela Lugosi"
        else if (tableNumber == 26 || tableNumber == 27 || tableNumber == 28 || tableNumber == 29) "Sean Connery"
	else if (tableNumber == 30) "Ben Stiller"
	else if (tableNumber == 31) "Christopher Lee (I)"
	else throw new Exception ("Unknown tableNumber in finding start")
      val reachableActors = graphBacon.reachable (actor2Actor, reachingStart)
      val reachableMovies = graphBacon.reachable (
	movie2Movie, actorConnections.filter (_._1 == reachingStart).map (_._2).head)
      // remove all keys that aren't reachable
      val subgraphActor = actor2Actor -- (actor2Actor.keySet &~ reachableActors)
      val subgraphMovie = movie2Movie -- (movie2Movie.keySet &~ reachableMovies)
      
      val actorOutput = new PrintWriter(new File(args(1).toString))
    
      reportOutHeader (actorOutput, "actors", tableDescription, reachableActors.size)

      if (scala.math.abs(reachableActors.drop(3).map (graphBacon.averageDistance (_, subgraphActor)).sum - 
                          reachableActors.drop(3).map (priorActorBacon(_)).sum)
           < noChangeLimit * 3) 
      {
	noChangeOut (actorOutput)
      } 
      else {
	val newActorBacon : Map [String, graphBacon.Real] = graphBacon.averageDistance (reachableActors, subgraphActor)
	val actorDataTime = System.currentTimeMillis()
	val actorRunTime = new runTimes ((mysqlTime - startTime) / 1000.0f, 
					 (setupEndTime - mysqlTime) / 1000.0f, 
					 (actorDataTime - setupEndTime) / 1000.0f)

	storeActorBaconNumbers (tableNumber, newActorBacon)
	reportOut (actorOutput, "actor", newActorBacon, priorActorBacon, actorRunTime, (x : String) => x)
      }
      actorOutput.close()

      val movieOutput = new PrintWriter (new File(args(2).toString))
      val movieDataStartTime = System.currentTimeMillis()

      reportOutHeader (movieOutput, "movies", tableDescription, reachableMovies.size)

      if ((reachableMovies.drop(3).map (graphBacon.averageDistance (_, subgraphMovie)).sum) < noChangeLimit * 3) {
	noChangeOut (movieOutput)
      } else {      
	val newMovieBacon  = graphBacon.averageDistance (reachableMovies, subgraphMovie)
	val movieDataTime = System.currentTimeMillis()
	val movieRunTime = new runTimes ((mysqlTime - startTime) / 1000.0f, 
					 (setupEndTime - mysqlTime) / 1000.0f, 
					 (movieDataTime - movieDataStartTime) / 1000.0f)

	storeMovieBaconNumbers (tableNumber, newMovieBacon)
	reportOut (movieOutput, "movies", newMovieBacon, priorMovieBacon, movieRunTime, movieNames)
      }
      movieOutput.close()

    }
    catch {
      case e : Throwable => e.printStackTrace()
    }
  }
}
