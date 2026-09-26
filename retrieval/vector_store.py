"""
Vector Retrieval Engine (Section 9B).
Wraps Chroma collections (fhir_r4_vectors, loinc_vectors, ohdsi_vectors)
using sentence-transformers/all-MiniLM-L6-v2 (dim 384).
Provides semantic similarity as supporting evidence.
"""

import os
os.environ["USE_TF"] = "0"
os.environ["USE_TORCH"] = "1"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import logging
from typing import List, Dict, Any, Optional
import chromadb
from models.schemas import EvidenceItem

logger = logging.getLogger(__name__)


class VectorSearchEngine:
    """
    Semantic vector search engine querying pre-indexed clinical terminology and FHIR vectors.
    """

    def __init__(self, persist_dir: Optional[str] = None):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.persist_dir = persist_dir or os.path.join(base_dir, "retrieval", "vector_db")
        self._client: Optional[chromadb.PersistentClient] = None
        self._embedder = None
        self._query_cache: Dict[str, List[EvidenceItem]] = {}

    def _get_client(self) -> Optional[chromadb.PersistentClient]:
        if self._client is None and os.path.exists(self.persist_dir):
            try:
                self._client = chromadb.PersistentClient(path=self.persist_dir)
            except Exception as e:
                logger.warning(f"Could not connect to Chroma at {self.persist_dir}: {e}")
        return self._client

    def _get_embedder(self):
        if self._embedder is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._embedder = SentenceTransformer("all-MiniLM-L6-v2")
            except Exception as e:
                logger.warning(f"Could not load SentenceTransformer: {e}")
        return self._embedder

    def search_collection(
        self, collection_name: str, query: str, top_k: int = 3
    ) -> List[EvidenceItem]:
        """
        Query a Chroma vector collection and return supporting EvidenceItems.
        """
        cache_key = f"{collection_name}::{query.strip().lower()}::{top_k}"
        if cache_key in self._query_cache:
            return self._query_cache[cache_key]
        client = self._get_client()
        embedder = self._get_embedder()

        if client is None or embedder is None:
            return []

        try:
            col = client.get_collection(collection_name)
            query_emb = embedder.encode(query).tolist()
            res = col.query(query_embeddings=[query_emb], n_results=top_k)

            evidence = []
            docs = res.get("documents", [[]])[0]
            metas = res.get("metadatas", [[]])[0]
            dists = res.get("distances", [[]])[0]
            ids = res.get("ids", [[]])[0]

            source_map = {
                "fhir_r4_vectors": "FHIR_R4",
                "loinc_vectors": "LOINC",
                "ohdsi_vectors": "OHDSI",
            }
            source_tag = source_map.get(collection_name, "OHDSI")

            for i in range(len(docs)):
                doc_text = docs[i] if i < len(docs) else ""
                meta = metas[i] if i < len(metas) else {}
                dist = dists[i] if i < len(dists) else 1.0
                doc_id = ids[i] if i < len(ids) else f"vec_{i}"

                # Cosine distance to similarity (approximate: 1 / (1 + dist) or max(0, 1 - dist/2))
                similarity = max(0.0, min(1.0, 1.0 - (dist / 2.0)))

                evidence.append(
                    EvidenceItem(
                        evidence_id=f"{source_tag}_VEC_{doc_id}",
                        source=source_tag,
                        retrieval_method="VECTOR_SEARCH",
                        evidence_type="context",
                        matched_term_or_code=str(meta.get("code") or doc_id),
                        canonical_id=str(meta.get("code") or doc_id),
                        description=f"Semantic match in {collection_name}: {doc_text[:200]}",
                        score=round(similarity, 3),
                        provenance_metadata={
                            "collection": collection_name,
                            "distance": round(dist, 4),
                            "metadata": meta,
                        },
                    )
                )

            self._query_cache[cache_key] = evidence
            return evidence
        except Exception as e:
            logger.warning(f"Error querying Chroma collection {collection_name}: {e}")
            return []
