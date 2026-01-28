from typing import Dict, List
from app.document_store import TenantDocumentStore


class RAGService:
    
    def __init__(self, document_store: TenantDocumentStore):
        self.store = document_store
    
    def query(self, tenant_id: str, question: str, n_results: int = 3) -> Dict:
        results = self.store.search(tenant_id, question, n_results)
        
        if not results:
            return {
                "answer": "Aucune information disponible pour répondre à cette question dans vos documents.",
                "sources": [],
                "context": [],
                "has_answer": False
            }
        
        relevant_results = [r for r in results if r['distance'] < 1.0]
        
        if not relevant_results:
            return {
                "answer": "Aucune information pertinente trouvée dans vos documents pour répondre à cette question.",
                "sources": [],
                "context": results[:2],
                "has_answer": False
            }
        
        answer = self._build_answer(question, relevant_results)
        sources = list(set([r['source'] for r in relevant_results]))
        
        return {
            "answer": answer,
            "sources": sources,
            "context": relevant_results,
            "has_answer": True
        }
    
    def _build_answer(self, question: str, results: List[Dict]) -> str:
        answer_parts = [f"D'après les documents disponibles :\n"]
        
        for i, result in enumerate(results[:2], 1):
            content = result['content']
            if len(content) > 500:
                content = content[:500] + "..."
            answer_parts.append(f"\n[Extrait {i} - {result['source']}]")
            answer_parts.append(content)
        
        return "\n".join(answer_parts)
    
    def initialize_tenant_documents(self, tenant_id: str, data_directory: str):
        self.store.load_documents_from_directory(tenant_id, data_directory)
    
    def get_tenant_stats(self, tenant_id: str) -> Dict:
        collection = self.store.get_collection(tenant_id)
        try:
            count = collection.count()
        except:
            count = 0
        
        return {
            "tenant_id": tenant_id,
            "document_count": count
        }
