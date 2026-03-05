"""
RAG store for code samples.

Indexes Python scripts from the code_samples/ directory into a ChromaDB collection,
enabling semantic retrieval of relevant examples at code generation time.
"""

import ast
import glob
import hashlib
import os
from typing import List

import chromadb
from dotenv import load_dotenv

load_dotenv()

SAMPLES_COLLECTION = "code_samples"


class CodeSampleStore:
    """
    Vector store for code samples using ChromaDB.
    Enables semantic retrieval of relevant example scripts for the code generator.
    """

    def __init__(self):
        self.chroma_client = chromadb.HttpClient(
            host=os.environ["CHROMA_CLIENT_URL"], ssl=True
        )
        try:
            self.chroma_client.heartbeat()
        except Exception as e:
            raise ConnectionError(
                f"Failed to connect to ChromaDB at {os.environ['CHROMA_CLIENT_URL']}: {e}"
            )

        self.collection = self.chroma_client.get_or_create_collection(
            name=SAMPLES_COLLECTION,
            metadata={"description": "Curated geospatial code samples for RAG-grounded generation."},
        )

    def _extract_docstring(self, source: str) -> str:
        """Extract the module-level docstring from a Python source string."""
        try:
            tree = ast.parse(source)
            return ast.get_docstring(tree) or ""
        except SyntaxError:
            return ""

    def index_samples_from_directory(self, samples_dir: str) -> int:
        """
        Walk samples_dir recursively, index all .py files into ChromaDB.

        Each document is: docstring + first 60 lines of code (for embedding quality).
        Metadata stores the full source for retrieval.
        Uses a content hash to detect changes — new files are added and
        modified files are updated (upserted).

        Returns:
            Number of newly indexed or updated files.
        """
        pattern = os.path.join(samples_dir, "**", "*.py")
        filepaths = sorted(glob.glob(pattern, recursive=True))

        if not filepaths:
            print(f"[CodeSampleStore] No .py files found under {samples_dir}")
            return 0

        # Fetch already-indexed entries with their content hashes
        existing_data = self.collection.get(include=["metadatas"])
        existing_hashes = {}
        for id_, meta in zip(existing_data["ids"], existing_data["metadatas"] or []):
            existing_hashes[id_] = meta.get("content_hash", "")

        documents = []
        metadatas = []
        ids = []

        for filepath in filepaths:
            file_id = os.path.relpath(filepath, samples_dir)

            with open(filepath, encoding="utf-8") as f:
                source = f.read()

            content_hash = hashlib.sha256(source.encode("utf-8")).hexdigest()

            # Skip if already indexed with the same content
            if file_id in existing_hashes and existing_hashes[file_id] == content_hash:
                continue

            docstring = self._extract_docstring(source)
            # Embedding text: docstring + condensed code header
            head_lines = "\n".join(source.splitlines()[:60])
            embed_text = f"{docstring}\n\n{head_lines}".strip()

            # Derive task_type from subdirectory name
            task_type = file_id.split(os.sep)[0] if os.sep in file_id else "general"

            documents.append(embed_text)
            metadatas.append({
                "filepath": file_id,
                "task_type": task_type,
                "docstring": docstring[:500],
                "source": source,
                "content_hash": content_hash,
            })
            ids.append(file_id)

        if ids:
            self.collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
            print(f"[CodeSampleStore] Indexed/updated {len(ids)} code sample(s) in ChromaDB.")
        else:
            print(f"[CodeSampleStore] All {len(filepaths)} sample(s) already up to date.")

        return len(ids)

    def query_samples(self, query: str, n_results: int = 3) -> List[dict]:
        """
        Retrieve the top-N most relevant code samples for a given query.

        Args:
            query: Natural language description of the analysis task.
            n_results: Number of samples to return.

        Returns:
            List of dicts with keys: filepath, task_type, docstring, source.
        """
        total = self.collection.count()
        if total == 0:
            return []

        n = min(n_results, total)
        results = self.collection.query(query_texts=[query], n_results=n, include=["metadatas"])

        if not results.get("metadatas") or not results["metadatas"]:
            return []

        return [
            {
                "filepath": meta["filepath"],
                "task_type": meta["task_type"],
                "docstring": meta["docstring"],
                "source": meta["source"],
            }
            for meta in results["metadatas"][0]
        ]
