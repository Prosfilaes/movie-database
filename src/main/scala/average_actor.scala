// import scala.slick.driver.MySQLDriver.simple._
import scala.slick.session.Database
import scala.slick.jdbc.{GetResult, StaticQuery => Q}
import Database.threadLocalSession
import Q.interpolation
import scala.io.Source
import graphBacon._

object mainBody {
  val (username, password) = 
    {
      val passChunks = Source.fromFile("password").getLines.next.split (" ")
      (passChunks.head, passChunks.tail.head)
    }

  val actorConnectionsSQL = Map (
    // Change back from temp_actor_test to actor after getting to work
    (1, 
     //"""SELECT DISTINCT p1.person, p2.person FROM temp_actor_test p1 
     //INNER JOIN temp_actor_test p2 ON p1.movie_id = p2.movie_id AND p1.person != p2.person
     //WHERE p1.person IN (SELECT person FROM temp_actor_test group by person HAVING COUNT(*) > 1) 
     //AND p2.person IN (SELECT person FROM temp_actor_test group by person HAVING COUNT(*) > 1) 
     //;"""
     """SELECT person, movie_id FROM temp_actor_test 
     WHERE person IN (SELECT person FROM temp_actor_test GROUP BY person HAVING COUNT(*) > 1);"""
   )
  )

  // Table definition if we use more abstract database interfaces in the future
  // object Actors extends Table[(String, Int)]("actor") {
  // def person = column[String]("person")
  // def movie_id = column[Int]("movie_id")
  // def * = person ~ movie_id
  // }

  // Returns (Table Description, actor2actor list, map from actor to previous avg. bacon number)
  def readInitialDatabase (tableNumber: Int) : (String, List[(String, Int)], Map[String, Float]) = {
    Database.forURL("jdbc:mysql://localhost:3306/DVDs", driver = "com.mysql.jdbc.Driver", user=username, password=password) withSession {
      val actorConnections = Q.query[Unit, (String, Int)] (actorConnectionsSQL (tableNumber)).list ()
      val priorBaconNums = Q.query[Int, (String, Float)] (
	"SELECT person, bacon_num FROM actorbacon WHERE table_num = ?;").list(tableNumber).toMap
      val tableDescription = Q.query[Int, String] ("SELECT description FROM moviebacon_tablenum WHERE table_num = ?;").list(tableNumber).head
      (tableDescription, actorConnections, priorBaconNums)
    }
  }

  def storeBaconNumbers (tableNumber: Int, baconNumbers: Map [String, graphBacon.Real]): Unit = {
    Database.forURL("jdbc:mysql://localhost:3306/DVDs", driver = "com.mysql.jdbc.Driver", user=username, password=password) withSession {
      (Q.u + "DELETE FROM actorbacon WHERE table_num = " +? tableNumber + ";").execute
      for (bn <- baconNumbers) {
	(Q.u + "INSERT INTO actorbacon VALUES (" +? tableNumber + ", " +? bn._1 + ", " +? bn._2 + ");").execute;
      }
    }
  }

  def main (args: Array[String]): Unit = {
    val startTime = System.currentTimeMillis()

    // XXX: tableNumber needs to be parsed out of args
    val tableNumber = if (args.size == 0) 1 else if (args.size == 1) args(0).toInt else -1;
    if (tableNumber == -1) {
      println ("This program only takes one argument, the table number.")
      return
    }
    val (tableDescription, actorConnections, priorBaconNums) = readInitialDatabase (tableNumber);

    val actors = actorConnections.map (_._1).toSet;

    // premature optimization
    // val actorId = actors.zipWithIndex.toMap
    // val reverseActorId = actorId.map (_.swap)
    // println (actorId)
    // println (reverseActorId)

    def connectActors (a : Iterable[(String, Int)]) = {
      def explode (a : Iterable [String]) = {
	val aSet = a.toSet
	for (person <- aSet) yield (person, aSet - person)
      }
      a.groupBy (_._2).map (_._2.map(_._1)).flatMap (explode).groupBy (_._1).mapValues (_.map (_._2).reduce (_ ++ _))
    }

    val actor2Actor = connectActors (actorConnections)
    // val actor2Actor = actorConnections.toIndexedSeq.groupBy (_._1).mapValues (_.map(_._2).toSet)
    val setupEndTime = System.currentTimeMillis()
    val reachableActors = graphBacon.reachable (actor2Actor, "Dana Hill (I)")
    val subgraph = actor2Actor -- (actors &~ reachableActors) // remove all keys that aren't reachable
    println ("This " + tableDescription + " list following is about the relations of " + reachableActors.size.toString + " actors.")
    Console.flush()

    // XXX: Add checking for no changes? Will only matter if actors is a lot faster then it used to be
    val newBacon : Map [String, graphBacon.Real] = graphBacon.averageDistance (reachableActors, subgraph)
    storeBaconNumbers (tableNumber, newBacon)
    val dataCollectionTime = System.currentTimeMillis()
    val newBaconList = newBacon.toIndexedSeq.sortBy (_._2)
    for (a <- newBaconList) {
      val bacon = a._2
      print (a._1 ++ f": $bacon%.4f")
      if (priorBaconNums.contains (a._1)) {
	val prior = priorBaconNums (a._1)
	val diff = bacon - prior
	println (f" / old $prior%.4f / change $diff%+.4f")
      }
      else println (" / not previously in universe")
    }
    val finalTime = System.currentTimeMillis()
    println ()

    val setupTimeDiff = (setupEndTime - startTime) / 1000.0f
    val travellingTime = (dataCollectionTime - setupEndTime) / 1000.0f
    val perActor = travellingTime / reachableActors.size
    val totalTime = (finalTime - startTime) / 1000.0f
    println (f"Setup: $setupTimeDiff%.2fs; travelling time: $travellingTime%.2fs; per actor: $perActor%.4fs; total: $totalTime%.2fs")

    val sumBacon = newBaconList.map(_._2).reduce (_ + _)
    val avgBacon = sumBacon / reachableActors.size
    if (priorBaconNums.size == 0) {
      println (f"Current Bacon nums: $sumBacon%.2f sum, $avgBacon%.6f avg")
    }
    else {
      val sumOldBacon = priorBaconNums.map(_._2).reduce (_ + _)
      val avgOldBacon = sumOldBacon / priorBaconNums.size
      println (f"Prior Bacon nums: $sumOldBacon%.2f sum, $avgOldBacon%.2f avg; current Bacon nums: $sumBacon%.2f sum, $avgBacon%.6f avg")
    }
  }
}

