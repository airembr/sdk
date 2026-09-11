import math

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def get_clustered_result(items: list[dict], similarity_threshold: float = 0.5, top_k: int = 1) -> list[dict]:
    """
    Groups items by semantic similarity of text_string, scores each cluster as
    mean(_score) * log(1 + size), and returns all members of the top_k best clusters.
    """
    if len(items) <= 1:
        return items

    texts = [item.get('text_string', '') or '' for item in items]
    if sum(1 for t in texts if t.strip()) < 2:
        return items

    vectorizer = TfidfVectorizer(stop_words='english', min_df=1)
    try:
        tfidf_matrix = vectorizer.fit_transform(texts)
    except ValueError:
        return items

    sim_matrix = cosine_similarity(tfidf_matrix)

    parent = list(range(len(items)))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x: int, y: int) -> None:
        parent[find(x)] = find(y)

    n = len(items)
    for i in range(n):
        for j in range(i + 1, n):
            if sim_matrix[i, j] >= similarity_threshold:
                union(i, j)

    clusters: dict[int, list[dict]] = {}
    for idx in range(n):
        clusters.setdefault(find(idx), []).append(items[idx])

    ranked = sorted(
        clusters.values(),
        key=lambda members: (
            sum(m['_score'] for m in members) / len(members)
        ) * math.log(1 + len(members)),
        reverse=True,
    )

    result = []
    for cluster_number, cluster in enumerate(ranked[:top_k], start=1):
        avg = sum(m['_score'] for m in cluster) / len(cluster)
        cluster_score = avg * math.log(1 + len(cluster))
        for item in cluster:
            item['_cluster_score'] = cluster_score
            item['_cluster_number'] = cluster_number
        result.extend(cluster)
    return result
