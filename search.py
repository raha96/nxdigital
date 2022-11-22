from nxdigital import circuit

def topoligical_sort_from_outputs (cir:circuit) -> list:
    """Return a list of circuit nets, sorted by reverse topological order"""
    from queue import Queue
    from nxdigital.utils import _net_type

    #def neighbors(node):
    #    modules = []
    #    for edge in cir.graph.edges:
    #        if edge[1] == node:
    #            modules.append(edge[0])
    #    nets = []
    #    for m in modules:
    #        for edge in cir.graph.edges:
    #            if edge[1] == m:
    #                nets.append(str(edge[0]))
    #    return nets

    def innodes(node):
        """Return all nodes that have an edge to `node`"""
        modules = []
        for edge in cir.graph.edges:
            if edge[1] == node:
                modules.append(edge[0])
        return modules

    marked = {}
    order = []

    for m in cir.module_list:
        node = cir.module_list[m]
        marked[node] = False

    q = Queue()
    for n in cir.net_list:
        node = cir.net_list[n]
        if node.ntype == _net_type.OUT:
            order.append(n)
            marked[n] = True
            newmods = innodes(node)
            # A single module
            assert len(newmods) == 1
            m = newmods[0]
            assert (not m in marked) or (not marked[m])
            q.put(m)
            marked[m] = True
        else:
            marked[n] = False

    while q.qsize():
        mod = q.get()
        candidates = innodes(mod)
        for n in candidates:
            fanout = cir.graph.adj[n]
            ready = True
            for m in fanout:
                if not marked[m]:
                    ready = False
            if ready and not marked[n.name]:
                marked[n.name] = True
                order.append(n.name)
            prevmods = innodes(n)
            for m in prevmods:
                if not marked[m]:
                    q.put(m)
                    marked[m] = True
    return order
