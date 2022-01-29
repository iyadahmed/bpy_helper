from typing import Any, Iterable


class KMeansNode:
    def __init__(self, data: Any, value: float):
        self.data = data
        self.value = value

    def __repr__(self) -> str:
        return f"<{self.data}, {self.value}>"


# Can use a set instead
class KMeansCluster(list):
    def __init__(self, centroid: float) -> None:
        super().__init__()
        self._centroid = centroid

    @property
    def centroid(self):
        return self._centroid

    def add_node(self, node: KMeansNode):
        old_len = len(self)
        if old_len == 0:
            self._centroid = node.value
        else:
            self._centroid = (self._centroid + (node.value / old_len)) / (1 + 1 / old_len)
        self.append(node)


def k_means_min_max(nodes: Iterable[KMeansNode]):
    """Divide nodes into two clusters, with min and max values as initial centroids"""
    min_node = min(nodes, key=lambda node: node.value)
    max_node = max(nodes, key=lambda node: node.value)

    min_cluster = KMeansCluster(min_node.value)
    max_cluster = KMeansCluster(max_node.value)

    for node in nodes:
        dist_to_min = abs(min_cluster.centroid - node.value)
        dist_to_max = abs(max_cluster.centroid - node.value)

        if dist_to_min < dist_to_max:
            min_cluster.add_node(node)
        else:
            max_cluster.add_node(node)

    return min_cluster, max_cluster
