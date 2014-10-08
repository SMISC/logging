SMISC Twitter Analysis
======================

1. BFS for network discovery
----------------------------

Edges: X is following Y means there is a directed edge from X to Y. 

* queues:
    - filter queue: list of (user id, depth) pair waiting to see if they already have been visited
    - fetch queue: list of (user id, depth) pair that are known to not have been visited
* n fetch threads
    - Dequeues from fetch queues
    - Uses Twitter API
    - Pushes next items to filter queue
* 1 filter thread
    - Dequeues from filter queue
    - Filters through PostgreSQL
    - Pushes to fetch queue
