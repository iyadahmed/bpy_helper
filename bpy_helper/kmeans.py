from typing import Any, Iterable, List


class KMeansNode:
    def __init__(self, data: Any, value: float):
        self.data = data
        self.value = value

    def __repr__(self) -> str:
        return f"<{self.data}, {self.value}>"


def k_means_min_max(nodes: Iterable[KMeansNode]):
    """Divide nodes into two clusters, with min and max values as initial centroids"""
    min_node = min(nodes, key=lambda node: node.value)
    max_node = max(nodes, key=lambda node: node.value)

    min_centroid = min_node.value
    max_centroid = max_node.value

    min_cluster: List[KMeansNode] = []
    min_cluster_sum = 0  # TODO: Avoid floating point precision issues when accumlating
    max_cluster: List[KMeansNode] = []
    max_cluster_sum = 0

    for node in nodes:
        dist_to_min = abs(min_centroid - node.value)
        dist_to_max = abs(max_centroid - node.value)

        if dist_to_min < dist_to_max:
            min_cluster.append(node)
            min_cluster_sum += node.value
            min_centroid = min_cluster_sum / len(min_cluster)
        else:
            max_cluster.append(node)
            max_cluster_sum += node.value
            max_centroid = max_cluster_sum / len(max_cluster)

    return min_cluster, max_cluster
