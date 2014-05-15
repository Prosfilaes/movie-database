package graphBacon 

object graphBacon {
  type Real = Double;
  def toReal (i : Int) = i.toDouble

  // Returns a Set of T's in the subgraph
  def reachable[T] (graph: Map [T, Set[T]], initial: T): Set[T] = {
    def reachable_recur (foundSet : Set[T], curElem : T, curSet : Set[T]) : Set[T] = {
      var curFoundSet = foundSet
      if (curSet.isEmpty) foundSet
      else {
	for (e <- curSet) {
	  if (!foundSet.contains (e)) 
	    curFoundSet = reachable_recur (curFoundSet ++ curSet, e, graph (e))
	}
	curFoundSet
      }
    }

    reachable_recur (Set (initial), initial, graph (initial))
  }
 
  def averageDistance[T] (testPoints : Iterable [T], graph : Map[T, Set[T]]) : Map [T, Real] = testPoints.toVector.par.map (x => (x, averageDistance (x, graph))).toList.toMap
  def averageDistance[T] (point : T, graph : Map [T, Set[T]]) : Real = {
    val numElems = graph.size
    def distanceRecur (distance : Int, bucket : Set[T], lastConnected : Set[T], currentSum : Int) : Real = {
      val newConnected = lastConnected.flatMap (graph (_)) &~ bucket
      val ncLength = newConnected.size
      if (ncLength == 0) toReal(currentSum) / toReal(numElems)
      else distanceRecur (distance + 1, bucket ++ newConnected, newConnected, currentSum + newConnected.size * distance)
    }
    distanceRecur (1, Set(point), Set(point), 0)
  }
      
}


