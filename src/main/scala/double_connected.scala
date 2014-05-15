import scala.slick.session.Database
import scala.slick.jdbc.{GetResult, StaticQuery => Q}
import Database.threadLocalSession
import Q.interpolation

import scala.io.Source
import java.io._

import graphBacon._

object mainDoubleBody {
  val (username, password) = 
    {
      val passChunks = Source.fromFile("password").getLines.next.split (" ")
      (passChunks.head, passChunks.tail.head)
    }

  def connect (a : Iterable [(Int, Int)]) = {
    a.groupBy (_._1).map (x => (x._1, x._2.map (_._2).toSet)).toMap
  }

  // Table definition if we use more abstract database interfaces in the future
  // object Actors extends Table[(String, Int)]("actor") {
  // def person = column[String]("person")
  // def movie_id = column[Int]("movie_id")
  // def * = person ~ movie_id
  // }

  def readInitialDatabase : (String, List[(Int, Int)], Map[Int, Float], 
						Map[Int, String], Map [Int, (String, Int)]) 
  = {
    Database.forURL("jdbc:mysql://localhost:3306/DVDs", driver = "com.mysql.jdbc.Driver", 
		    user=username, password=password) withSession {
      val movieConnections = Q.query[Unit, (Int, Int)] (
	"""SELECT m1.movie_id, m2.movie_id FROM movie m1 INNER JOIN actor a1 ON a1.movie_id = m1.movie_id 
	INNER JOIN actor a2 on a1.person = a2.person INNER JOIN movie m2 ON m2.movie_id = a2.movie_id
	GROUP BY m1.movie_id, m2.movie_id HAVING COUNT(*) > 1;""").list ()
      val priorMovieBaconNums = Q.query[Unit, (Int, Float)] (
	"SELECT movie_id, bacon_num FROM moviebacon WHERE table_num = 12;").list().toMap
      val tableDescription = Q.query[Unit, String] (
	"SELECT description FROM moviebacon_tablenum WHERE table_num = 12;").list().head
      val movieDescriptions = Q.query[Unit, (Int, String, Int)] ("SELECT movie_id, name, year FROM movie;").
	list().map (x => (x._1, (x._2, x._3))).toMap
      val movieNames = Q.query[Unit, (Int, String)] ("SELECT movie_id, name FROM movie;").list().toMap
      (tableDescription, movieConnections, priorMovieBaconNums, movieNames, movieDescriptions)
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
	if (scala.math.abs(diff) < 0.00001) // That is, a "0.0000" represents values in [0.00001 .. 0.0001)
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

  def start (movieFilename : String): Unit = {
    try {
      val startTime = System.currentTimeMillis()

//      if (args.size != 1) {
//	println ("This program takes one argument, the movie filename")
//	return
  //    }

      val tableNumber = 12
      
      val (tableDescription, movieConnections, priorMovieBacon, movieNames, movieDescriptions) = 
	readInitialDatabase;
      val mysqlTime = System.currentTimeMillis()
      
      val movie2Movie = connect (movieConnections)
      val setupEndTime = System.currentTimeMillis()
      val reachingStart = 62 // Spaceballs
      val reachableMovies = graphBacon.reachable (movie2Movie, reachingStart)
      // remove all keys that aren't reachable
      val subgraphMovie = movie2Movie.filter (x => reachableMovies.contains (x._1))
      
      val movieOutput = new PrintWriter (movieFilename)
      val movieDataStartTime = System.currentTimeMillis()
      reportOutHeader (movieOutput, "movies", tableDescription, reachableMovies.size)

      // XXX: Add checking for no changes?
      val newMovieBacon  = graphBacon.averageDistance (reachableMovies, subgraphMovie)
      val movieDataTime = System.currentTimeMillis()
      val movieRunTime = new runTimes ((mysqlTime - startTime) / 1000.0f, 
				       (setupEndTime - mysqlTime) / 1000.0f, 
				       (movieDataTime - movieDataStartTime) / 1000.0f)

      storeMovieBaconNumbers (tableNumber, newMovieBacon)
      reportOut (movieOutput, "movies", newMovieBacon, priorMovieBacon, movieRunTime, movieNames)
      movieOutput.close()

    }
    catch {
      case e : Throwable => e.printStackTrace()
    }
  }
}
