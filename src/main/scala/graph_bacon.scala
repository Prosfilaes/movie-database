package graphBacon 

object graphBacon {
  type Real = Double;
  def toReal (i : Int) = i.toDouble

  // Returns a Set of T's in the subgraph
  def reachable[T] (graph: Map [T, Set[T]], initial: T): Set[T] = {
    def reachable_recur (foundSet : Set[T], curElem : T, curSet : Set[T]) : Set[T] = {
      if (curSet.isEmpty) foundSet
      else {
	val newElem = curSet.head
	if (foundSet.contains (newElem)) reachable_recur (foundSet, curElem, curSet.tail)
	else reachable_recur (reachable_recur (foundSet + newElem, newElem, graph (newElem)), curElem, curSet.tail)
      }
    }
    reachable_recur (Set (initial), initial, graph (initial))
  }
 
  def averageDistance[T] (testPoints : Iterable [T], graph : Map[T, Set[T]]) : Map [T, Real] = testPoints.map (x => (x, averageDistance (x, graph))).toMap
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


