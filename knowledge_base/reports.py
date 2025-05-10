import chromadb
from chromadb.utils import embedding_functions
import json
import uuid
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class AnalyticsReport:
    id: str
    title: str
    description: str

class Report:
    def __init__(self, collection_name: str = 'analytics_reports'):
        # Initializing chroma client with persistent storage
        self.client = chromadb.PersistentClient(path='./chroma_storage')

        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name='all-MiniLM-L6-v2'
            )

        self.collection = self.client.get_or_create_collection(
              name=collection_name,
              embedding_function=self.embedding_function,
              metadata={"hnsw:space": "cosine"}
            )

        # Load sample reports if collection is empty
        if self.collection.count() == 0:
            self.load_sample_reports()

    def load_sample_reports(self):
        sample_reports = json.load(open('/app/utils/sample_reports.json'))
        ids = []
        documents = []
        metadatas = []

        for report in sample_reports:
            report_id = str(uuid.uuid4())
            ids.append(report_id)
            documents.append(f"{report['title']} {report['description']}")
            metadatas.append({
                "title": report["title"],
                "description": report["description"]
            })

        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
      )

    def search_reports(self, query: str, top_k: int = 3) -> List[Tuple[AnalyticsReport, float]]:
        """Search for relevant reports using vector similarity"""
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            include=['metadatas', 'distances']
        )

        # Convert results to AnalyticsReport objects
        reports = []
        for idx, (metadata, distance) in enumerate(zip(results['metadatas'][0], results['distances'][0])):
            report = AnalyticsReport(
                id=results['ids'][0][idx],
                title=metadata["title"],
                description=metadata["description"]
            )
            # Convert distance to similarity score (Chroma returns distances)
            similarity = 1 - distance
            reports.append((report, similarity))
        
        return reports
