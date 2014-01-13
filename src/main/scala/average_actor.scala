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
     """SELECT person, movie_id FROM actor 
     WHERE person IN (SELECT person FROM actor GROUP BY person HAVING COUNT(*) > 1);"""
   ),
    (4,
     """SELECT person, movie_id FROM actor NATURAL JOIN movie m
     WHERE m.is_full_length AND person IN 
     (SELECT person FROM actor NATURAL JOIN movie m WHERE m.is_full_length 
     GROUP BY person HAVING COUNT(*) > 1);"""
   ),
    (6,
     """SELECT person, movie_id FROM actor NATURAL JOIN movie m
     WHERE m.is_full_length AND m.have_watched AND person IN 
     (SELECT person FROM actor NATURAL JOIN movie m WHERE m.is_full_length 
     AND m.have_watched GROUP BY person HAVING COUNT(*) > 1);"""
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
						Map [Int, (String, Int)]) 
  = {
    Database.forURL("jdbc:mysql://localhost:3306/DVDs", driver = "com.mysql.jdbc.Driver", 
		    user=username, password=password) withSession {
      val actorConnections = Q.query[Unit, (String, Int)] (actorConnectionsSQL (tableNumber)).list ()
      val priorBaconNums = Q.query[Int, (String, Float)] (
	"SELECT person, bacon_num FROM actorbacon WHERE table_num = ?;").list(tableNumber).toMap
      val tableDescription = Q.query[Int, String] (
	"SELECT description FROM moviebacon_tablenum WHERE table_num = ?;").list(tableNumber).head
      val movieDescriptions = Q.query[Unit, (Int, String, Int)] ("SELECT movie_id, name, year FROM movie;").
	list().map (x => (x._1, (x._2, x._3))).toMap
      (tableDescription, actorConnections, priorBaconNums, movieDescriptions)
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

  def connect [A, B](a : Iterable[(A, B)]) = {
    def explode (a : Iterable [A]) = {
      val aSet = a.toSet
      for (person <- aSet) yield (person, aSet - person)
    }
    a.groupBy (_._2).map (_._2.map(_._1)).flatMap (explode).groupBy (_._1).
    mapValues (_.map (_._2).reduce (_ ++ _))
  }

  class runTimes (val mysqlTime : Float, val setupTime : Float, val travellingTime : Float);

  // I acknowledge that internationalized code needs more care then this. This is unlikely
  // to ever need internationalized.
  def reportOut (where: OutputStreamWriter, who: String, who_plural: String, 
		 data : Map [String, graphBacon.Real], t : runTimes) = ()

  def main (args: Array[String]): Unit = {
    try {
      val startTime = System.currentTimeMillis()

      if (args.size != 3) {
	println ("This program takes three arguments, the table number, the actor filename and the movie filename")
	return
      }
      val tableNumber = args(0).toInt
      
      val (tableDescription, actorConnections, priorBaconNums, movieDescriptions) = readInitialDatabase (tableNumber);
      val mysqlTime = System.currentTimeMillis()
      
      val actor2Actor = connect (actorConnections)
      val movie2Movie = connect (actorConnections.map (x => (x._2, x._1)))
      val setupEndTime = System.currentTimeMillis()
      val reachingStart = "Dana Hill (I)" // This needs to be much more subtle and error out if she's not found
      val reachableActors = graphBacon.reachable (actor2Actor, reachingStart)
      val reachableMovies = graphBacon.reachable (
	movie2Movie, actorConnections.filter (_._1 == reachingStart).map (_._2).head)
      // remove all keys that aren't reachable
      val subgraphActor = actor2Actor -- (actor2Actor.keySet &~ reachableActors)
      val subgraphMovie = movie2Movie -- (movie2Movie.keySet &~ reachableMovies)
      
      val actorOutput = new PrintWriter(new File(args(1).toString))
      //    val movieOutput = new PrintWriter(new File(args(2).toString))
    
      actorOutput.println ("This " + tableDescription + " list following is about the relations of " + 
			   reachableActors.size.toString + " actors.")
      //    movieOutput.write ("This " + tableDescription + " list following is about the relations of " + 
      //	     reachableMovies.size.toString + " movies.")    
      actorOutput.flush()
      
      // XXX: Add checking for no changes?
      val newActorBacon : Map [String, graphBacon.Real] = graphBacon.averageDistance (reachableActors, subgraphActor)
      storeActorBaconNumbers (tableNumber, newActorBacon)
      val newActorBaconList = newActorBacon.toIndexedSeq.sortBy (_._2)
      val dataCollectionTime = System.currentTimeMillis()

      for (a <- newActorBaconList)
	{
	  val bacon = a._2
	  actorOutput.print (a._1 ++ f": $bacon%.4f")
	  if (priorBaconNums.contains (a._1)) {
	    val prior = priorBaconNums (a._1)
	    val diff = bacon - prior
	    actorOutput.println (f" / old $prior%.4f / change $diff%+.4f")
	  }
	  else actorOutput.println (" / not previously in universe")
	}
      val finalTime = System.currentTimeMillis()
      actorOutput.println ()

      val mysqlTimeDiff = (mysqlTime - startTime) / 1000.0f
      val setupTimeDiff = (setupEndTime - mysqlTime) / 1000.0f
      val travellingTime = (dataCollectionTime - setupEndTime) / 1000.0f
      val perActor = travellingTime / reachableActors.size
      val totalTime = (finalTime - startTime) / 1000.0f
      actorOutput.println (f"MySQL time: $mysqlTimeDiff%.2fs; setup: $setupTimeDiff%.2fs; travelling time: " ++
			   f"$travellingTime%.2fs; per actor: $perActor%.4fs; total: $totalTime%.2fs")

      val sumBacon = newActorBaconList.map(_._2).reduce (_ + _)
      val avgBacon = sumBacon / reachableActors.size
      if (priorBaconNums.size == 0) {
	actorOutput.println (f"Current Bacon nums: $sumBacon%.2f sum, $avgBacon%.6f avg")
      }
      else {
	val sumOldBacon = priorBaconNums.map(_._2).reduce (_ + _)
	val avgOldBacon = sumOldBacon / priorBaconNums.size
	actorOutput.println (f"Prior Bacon nums: $sumOldBacon%.2f sum, $avgOldBacon%.2f avg; current Bacon " ++
			     f"nums: $sumBacon%.2f sum, $avgBacon%.6f avg")
      }
      actorOutput.close()
    }
    catch {
      case e : Throwable => e.printStackTrace()
    }
  }
}
