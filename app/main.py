"""
API FastAPI pour le système SaaS multi-tenant
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import os

from app.deps import get_current_client
from app.config import DATA_PATH
from app.document_store import TenantDocumentStore
from app.rag_service import RAGService

# Initialisation
app = FastAPI(
    title="SaaS Multi-Tenant RAG System",
    description="Système de recherche documentaire avec séparation stricte par tenant",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialisation du store et du service RAG
document_store = TenantDocumentStore(persist_directory="./chroma_db")
rag_service = RAGService(document_store)

# Modèles Pydantic
class QueryRequest(BaseModel):
    question: str
    
class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
    has_answer: bool
    tenant_id: str
    
class HealthResponse(BaseModel):
    status: str
    tenant_stats: Optional[Dict] = None


@app.on_event("startup")
async def startup_event():
    """Chargement des documents au démarrage"""
    # Charger les documents pour le client A
    clientA_data_path = os.path.join(DATA_PATH, "clientA")
    if os.path.exists(clientA_data_path):
        rag_service.initialize_tenant_documents("clientA", clientA_data_path)
        print(f"✅ Documents chargés pour clientA")
    
    # Charger les documents pour le client B
    clientB_data_path = os.path.join(DATA_PATH, "clientB")
    if os.path.exists(clientB_data_path):
        rag_service.initialize_tenant_documents("clientB", clientB_data_path)
        print(f"✅ Documents chargés pour clientB")


@app.get("/", response_model=HealthResponse)
async def health_check():
    """Endpoint de santé"""
    return {
        "status": "ok"
    }


@app.get("/health/{tenant_id}", response_model=HealthResponse)
async def tenant_health(
    tenant_id: str,
    client_id: str = Depends(get_current_client)
):
    """
    Vérification de santé pour un tenant spécifique
    Accessible uniquement par le client authentifié
    """
    if client_id != tenant_id:
        raise HTTPException(
            status_code=403,
            detail="Accès interdit : vous ne pouvez accéder qu'à vos propres données"
        )
    
    stats = rag_service.get_tenant_stats(client_id)
    
    return {
        "status": "ok",
        "tenant_stats": stats
    }


@app.post("/query", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    client_id: str = Depends(get_current_client)
):
    """
    Recherche dans les documents du client authentifié
    
    L'authentification se fait via le header X-API-KEY
    Le client_id est automatiquement déduit du header
    
    ⚠️ POINT CLÉ : Le client ne peut jamais accéder aux documents d'un autre tenant
    """
    if not request.question or len(request.question.strip()) == 0:
        raise HTTPException(status_code=400, detail="Question vide")
    
    # Recherche UNIQUEMENT dans les documents du client authentifié
    result = rag_service.query(client_id, request.question, n_results=3)
    
    return {
        "answer": result["answer"],
        "sources": result["sources"],
        "has_answer": result["has_answer"],
        "tenant_id": client_id
    }


@app.post("/reload-documents")
async def reload_documents(client_id: str = Depends(get_current_client)):
    """
    Recharge les documents pour le client authentifié
    Utile pour le développement
    """
    # Effacer les anciennes données
    document_store.clear_tenant_data(client_id)
    
    # Recharger
    data_path = os.path.join(DATA_PATH, client_id)
    if os.path.exists(data_path):
        rag_service.initialize_tenant_documents(client_id, data_path)
        stats = rag_service.get_tenant_stats(client_id)
        return {
            "status": "reloaded",
            "tenant_id": client_id,
            "stats": stats
        }
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Répertoire de données non trouvé : {data_path}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
