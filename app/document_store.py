"""
Document store avec séparation stricte par tenant utilisant ChromaDB
"""
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple
import os


class TenantDocumentStore:
    """Store de documents avec isolation par tenant"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.collections = {}
    
    def get_collection(self, tenant_id: str):
        """Récupère ou crée une collection pour un tenant spécifique"""
        if tenant_id not in self.collections:
            collection_name = f"tenant_{tenant_id}"
            self.collections[tenant_id] = self.client.get_or_create_collection(
                name=collection_name
            )
        return self.collections[tenant_id]
    
    def add_documents(self, tenant_id: str, documents: List[Dict[str, str]]):
        """
        Ajoute des documents pour un tenant spécifique
        documents: [{"content": "...", "source": "...", "metadata": {...}}]
        """
        collection = self.get_collection(tenant_id)
        
        for idx, doc in enumerate(documents):
            doc_id = f"{tenant_id}_{doc.get('source', 'unknown')}_{idx}"
            embedding = self.model.encode(doc['content']).tolist()
            
            metadata = {
                "source": doc.get('source', 'unknown'),
                "tenant_id": tenant_id,
                **doc.get('metadata', {})
            }
            
            collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[doc['content']],
                metadatas=[metadata]
            )
    
    def search(self, tenant_id: str, query: str, n_results: int = 3) -> List[Dict]:
        """
        Recherche sémantique dans les documents d'un tenant
        Retourne les résultats avec leurs sources
        """
        collection = self.get_collection(tenant_id)
        
        # Vérifier si la collection est vide
        try:
            count = collection.count()
            if count == 0:
                return []
        except:
            return []
        
        query_embedding = self.model.encode(query).tolist()
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, count)
        )
        
        # Formater les résultats
        formatted_results = []
        if results['documents'] and len(results['documents'][0]) > 0:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'content': results['documents'][0][i],
                    'source': results['metadatas'][0][i].get('source', 'unknown'),
                    'distance': results['distances'][0][i] if 'distances' in results else 0,
                    'metadata': results['metadatas'][0][i]
                })
        
        return formatted_results
    
    def clear_tenant_data(self, tenant_id: str):
        """Supprime toutes les données d'un tenant"""
        try:
            collection_name = f"tenant_{tenant_id}"
            self.client.delete_collection(name=collection_name)
            if tenant_id in self.collections:
                del self.collections[tenant_id]
        except:
            pass
    
    def load_documents_from_directory(self, tenant_id: str, directory: str):
        """Charge tous les fichiers texte d'un répertoire pour un tenant"""
        documents = []
        
        if not os.path.exists(directory):
            return
        
        for filename in os.listdir(directory):
            if filename.endswith('.txt'):
                filepath = os.path.join(directory, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    documents.append({
                        'content': content,
                        'source': filename,
                        'metadata': {'filepath': filepath}
                    })
        
        if documents:
            self.add_documents(tenant_id, documents)
