from collections import defaultdict

def scc(edges):
    '''
    Uses iterative version of Kosaraju algorithm to determine
    the strongly connected components of a given directed graph.

    INPUT:  List of edges comprising the directed graph, with
    each edge as a tuple in (source, destination) format.

    OUTPUT: Dictionary of node : root keys and values.  The root
    is an arbitrarily selected node from the SCC; any two nodes
    with the same root are strongly connected.'''
    
    out_neighbors = defaultdict(set)
    in_neighbors = defaultdict(set)
    nodes = set()

    for source, dest in edges:
        nodes.add(source)
        nodes.add(dest)
        out_neighbors[source].add(dest)
        in_neighbors[dest].add(source)

    visited = set()
    roots = dict()
    stack_forward = [(False, node) for node in nodes]
    stack_backward = list()

    while stack_forward:
        complete, node = stack_forward.pop()
        if node not in visited:
            visited.add(node)
            stack_forward.append((True, node))
            stack_forward.extend((False, neighbor) for neighbor in out_neighbors[node])
        elif complete:
            stack_backward.append((node, node))

    while stack_backward:
        u, root = stack_backward.pop()
        if u not in roots:
            roots[u] = root
            stack_backward.extend((v, root) for v in in_neighbors[u])

    return roots
    

