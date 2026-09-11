import math
from statistics import median
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def aggregate_results_hybrid(
    results: list[list[dict]],             # one ranked list per retrieval METHOD
    query: str | None = None,              # the single query; enables lexical component
    corpus: list[str] | None = None,       # full observation texts for proper IDF
    method_names: list[str] | None = None, # optional, for diagnostics
    comparable_scores: bool = False,       # True only if all methods use the SAME similarity metric
    id_key: str = "id",
    similarity_key: str = "max_similarity",
    text_keys: tuple[str, ...] = ("text", "description", "summary"),  # fallback chain; ALL non-empty fields are collected
    text_key: str | None = None,           # backward-compat: single key, prepended to text_keys
    # --- blend weights (sum to 1); agreement promoted, it's the fusion signal ---
    w_sim: float = 0.35,        # quality of best version (normalized per method)
    w_agree: float = 0.20,      # method agreement
    w_rel: float = 0.20,        # standing within each method's list
    w_lex: float = 0.15,        # TF-IDF overlap with the query
    w_consensus: float = 0.10,  # version corroboration within a method
    # --- corroboration thresholds (applied on normalized sims) ---
    abs_floor: float = 0.60,
    rel_floor: float = 0.85,
    # --- lexical hygiene ---
    lex_floor: float = 0.05,    # raw cosine below this is treated as noise (zeroed pre-normalization)
    stop_words: str | list | None = "english",  # strip is/on/in/what... so they can't fake a match
    # --- calibration ---
    midpoint: float = 0.50,
    steepness: float = 10.0,
) -> list[dict]:
    """
    Fuses ranked lists from multiple retrieval methods for ONE query.

      S = median over methods of best-version similarity (min-max normalized
          per method unless comparable_scores=True)
      A = fraction of methods that retrieved the id        -> method agreement
      R = median of (best_sim / top_sim) per method        -> scale-free standing
      L = best TF-IDF(query, any version text), stopwords removed, floored at
          lex_floor, then normalized by the global top      -> lexical overlap
      C = median per-method version corroboration c/(c+1)
      score = sigmoid(steepness * (w·[S,A,R,L,C] - midpoint))

    Lexical design notes (fixes for stopword false-positives and missing-text bugs):
      * stop_words="english" prevents long documents from scoring on
        "is/on/in" alone when the query is natural language.
      * Every version's text is collected via a fallback chain over `text_keys`,
        and ALL non-empty fields per row are gathered — so an id whose `text`
        field is empty but whose `description` mentions the entity still matches.
      * Raw cosines below `lex_floor` are zeroed BEFORE normalization, so a
        batch where nothing genuinely matches can't be inflated into
        respectable-looking L values by the divide-by-top step.
      * `lex_raw` (pre-normalization cosine) is included in the output for
        diagnostics; `L_lexical` remains the normalized value used in the blend.
      * If the query yields no usable lexical signal (no texts, empty
        vocabulary after stopword removal, or every doc below the floor),
        w_lex is redistributed proportionally over the other components and
        the L fields are omitted — identical behavior to passing query=None.
    """
    n_methods = len(results)
    if n_methods == 0:
        return []
    names = method_names or [f"method_{i}" for i in range(n_methods)]

    if text_key is not None:  # legacy single-key arg takes priority in the chain
        text_keys = (text_key, *(k for k in text_keys if k != text_key))

    # ---------- helpers ----------
    def row_texts(row: dict) -> list[str]:
        """All non-empty text fields for a row, per the fallback chain."""
        return [row[k] for k in text_keys if isinstance(row.get(k), str) and row[k].strip()]

    # ---------- gather texts & decide whether lexical is viable ----------
    id_texts: dict[object, set[str]] = {}
    for method_rows in results:
        for row in method_rows:
            for t in row_texts(row):
                id_texts.setdefault(row[id_key], set()).add(t)

    use_lexical = query is not None and bool(query.strip())
    vectorizer = None
    if use_lexical:
        fit_texts = list(corpus) if corpus else sorted({t for ts in id_texts.values() for t in ts})
        if fit_texts:
            try:
                vectorizer = TfidfVectorizer(lowercase=True, sublinear_tf=True,
                                             stop_words=stop_words)
                vectorizer.fit(fit_texts)
            except ValueError:  # empty vocabulary after stopword removal
                vectorizer = None
        use_lexical = vectorizer is not None and bool(id_texts)

    # ---------- per-method fusion components ----------
    per_id = defaultdict(lambda: {"S": [], "S_raw": [], "R": [], "C": [],
                                  "lex_raw": 0.0, "lex": 0.0,
                                  "methods": [], "raw_occurrences": 0,
                                  "best_positions": []})

    for m_idx, method_rows in enumerate(results):
        if not method_rows:
            continue

        sims = [float(r[similarity_key]) for r in method_rows]
        if comparable_scores:
            norm = sims
        else:  # min-max normalize within this method's list (standard fusion practice)
            lo, hi = min(sims), max(sims)
            norm = [1.0] * len(sims) if hi == lo else [(s - lo) / (hi - lo) for s in sims]

        versions = defaultdict(list)  # id -> [(norm_sim, raw_sim, position), ...]
        for idx, row in enumerate(method_rows):
            versions[row[id_key]].append((norm[idx], sims[idx], idx + 1))
            per_id[row[id_key]]["raw_occurrences"] += 1

        top_sim = max(s for v in versions.values() for s, _, _ in v)

        for id_, v in versions.items():
            v.sort(key=lambda t: t[0], reverse=True)
            best_sim, best_sim_raw, best_pos = v[0]

            threshold = max(abs_floor, rel_floor * best_sim)
            c = sum(1 for s, _, _ in v[1:] if s >= threshold)

            e = per_id[id_]
            e["S"].append(best_sim)
            e["S_raw"].append(best_sim_raw)
            e["R"].append(best_sim / top_sim if top_sim > 0 else 0.0)
            e["C"].append(c / (c + 1))
            e["methods"].append(names[m_idx])
            e["best_positions"].append(best_pos)

    # ---------- lexical component ----------
    if use_lexical:
        q_vec = vectorizer.transform([query])
        if q_vec.nnz == 0:
            # no query token survives the vocabulary/stopword filter:
            # there is no lexical signal to measure
            use_lexical = False

    if use_lexical:
        for id_, texts in id_texts.items():
            if id_ not in per_id:
                continue  # text gathered for an id that no method actually returned
            t_vecs = vectorizer.transform(sorted(texts))
            raw_lex = float(cosine_similarity(q_vec, t_vecs).max())
            per_id[id_]["lex_raw"] = raw_lex
            per_id[id_]["lex"] = raw_lex if raw_lex >= lex_floor else 0.0  # noise gate

        top_lex = max((e["lex"] for e in per_id.values()), default=0.0)
        if top_lex > 0:
            for e in per_id.values():
                e["lex"] /= top_lex
        else:
            use_lexical = False  # nothing cleared the floor -> no real lexical signal

    if not use_lexical:  # redistribute lexical weight proportionally
        rest = w_sim + w_agree + w_rel + w_consensus
        if rest > 0:
            scale = (rest + w_lex) / rest
            w_sim, w_agree, w_rel, w_consensus = (w * scale for w in (w_sim, w_agree, w_rel, w_consensus))
        w_lex = 0.0

    # ---------- blend, calibrate, emit ----------
    output = []
    for id_, e in per_id.items():
        S, R, C = median(e["S"]), median(e["R"]), median(e["C"])
        S_display = median(e["S_raw"])
        A = len(set(e["methods"])) / n_methods
        L = e["lex"]

        raw = w_sim * S + w_agree * A + w_rel * R + w_lex * L + w_consensus * C
        score = 1 / (1 + math.exp(-steepness * (raw - midpoint)))

        output.append({
            id_key: id_,
            "score": round(score, 5), "raw": round(raw, 5),
            "S_quality": round(S_display, 3), "A_agreement": round(A, 3),
            "R_standing": round(R, 3), "C_consensus": round(C, 3),
            **({"L_lexical": round(L, 3), "lex_raw": round(e["lex_raw"], 4)} if use_lexical else {}),
            "found_by": sorted(set(e["methods"])),
            "raw_occurrences": e["raw_occurrences"],
            "best_position_overall": min(e["best_positions"]),
        })

    return sorted(output, key=lambda r: r["score"], reverse=True)