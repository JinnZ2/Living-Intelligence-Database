class TorusTopology(Topology):
    """Periodic 2D grid with both dimensions wrapped."""
    def __init__(self, width=20, height=20):
        self.w = width; self.h = height
    def nodes(self): return [(i,j) for i in range(self.w) for j in range(self.h)]
    def edges(self):
        edges = []
        for i in range(self.w):
            for j in range(self.h):
                edges.append(((i,j), ((i+1)%self.w, j)))
                edges.append(((i,j), (i, (j+1)%self.h)))
        return edges
    def size(self): return self.w * self.h

class OctahedralTopology(Topology):
    """8 vertices of an octahedron with edges along axes."""
    def __init__(self):
        self._nodes = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
    def nodes(self): return self._nodes
    def edges(self):
        # connect all pairs (for simplicity, the octahedral graph)
        edges = []
        for i, a in enumerate(self._nodes):
            for b in self._nodes[i+1:]:
                edges.append((a,b))
        return edges
    def size(self): return 6
