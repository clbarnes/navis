import networkx as nx

class TransformGraph:
    def __init__(self, graph: nx.DiGraph) -> None:
        """Convenient chaining of transforms.

        Parameters
        ----------
        graph : nx.DiGraph
            [description]
        """
        self.graph = graph
