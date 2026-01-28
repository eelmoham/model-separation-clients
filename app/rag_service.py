"""
Service RAG (Retrieval-Augmented Generation) avec séparation par tenant
"""
from typing import Dict, List, Optional
from app.document_store import TenantDocumentStore


class RAGService:
    """Service de recherche et génération de réponses basées sur les documents"""
    
    def __init__(self, document_store: TenantDocumentStore):
        self.store = document_store
    
    def query(self, tenant_id: str, question: str, n_results: int = 3) -> Dict:
        """
        Recherche la réponse à une question dans les documents du tenant
        
        Returns:
            {
                "answer": str,
                "sources": List[str],
                "context": List[Dict],
                "has_answer": bool
            }
        """
        # Rechercher les documents pertinents
        results = self.store.search(tenant_id, question, n_results)
        
        if not results:
            return {
                "answer": "Aucune information disponible pour répondre à cette question dans vos documents.",
                "sources": [],
                "context": [],
                "has_answer": False
            }
        
        # Filtrer les résultats par pertinence (distance < 1.0 pour être pertinent)
        relevant_results = [r for r in results if r['distance'] < 1.0]
        
        if not relevant_results:
            return {
                "answer": "Aucune information pertinente trouvée dans vos documents pour répondre à cette question.",
                "sources": [],
                "context": results[:2],  # Montrer quand même les résultats les plus proches
                "has_answer": False
            }
        
        # Construire la réponse basée sur les documents trouvés
        answer = self._build_answer(question, relevant_results)
        sources = list(set([r['source'] for r in relevant_results]))
        
        return {
            "answer": answer,
            "sources": sources,
            "context": relevant_results,
            "has_answer": True
        }
    
    def _build_answer(self, question: str, results: List[Dict]) -> str:
        """
        Construit une réponse basée sur les documents récupérés
        """
        # Pour ce test, on retourne simplement les extraits les plus pertinents
        # Dans un système complet, on utiliserait un LLM pour synthétiser
        
        answer_parts = []
        answer_parts.append(f"D'après les documents disponibles :\n")
        
        for i, result in enumerate(results[:2], 1):  # Max 2 extraits
            content = result['content']
            # Limiter la longueur de l'extrait
            if len(content) > 500:
                content = content[:500] + "..."
            answer_parts.append(f"\n[Extrait {i} - {result['source']}]")
            answer_parts.append(content)
        
        return "\n".join(answer_parts)
    
    def initialize_tenant_documents(self, tenant_id: str, data_directory: str):
        """Initialise les documents d'un tenant depuis un répertoire"""
        self.store.load_documents_from_directory(tenant_id, data_directory)
    
    def get_tenant_stats(self, tenant_id: str) -> Dict:
        """Retourne les statistiques d'un tenant"""
        collection = self.store.get_collection(tenant_id)
        try:
            count = collection.count()
        except:
            count = 0
        
        return {
            "tenant_id": tenant_id,
            "document_count": count
        }
