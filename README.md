# 🔐 Système SaaS Multi-Tenant - RAG avec Séparation Stricte des Clients

Application SaaS multi-tenant avec séparation stricte des données clients utilisant RAG (Retrieval-Augmented Generation) et ChromaDB.

## ✨ Caractéristiques

- 🔒 **Séparation stricte des clients** - Isolation complète des données par tenant
- 🔑 **Authentification API Key** - Header HTTP `X-API-KEY`
- 🤖 **RAG avec ChromaDB** - Recherche sémantique dans les documents
- 💬 **Interface moderne** - Style ChatGPT avec streaming de texte
- ⚡ **FastAPI Backend** - API REST performante
- 🎨 **Streamlit Frontend** - Interface utilisateur élégante

## 🚀 Démarrage Rapide

### Installation

```bash
# Cloner le projet
git clone https://github.com/eelmoham/model-separation-clients.git
cd model-separation-clients

# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# ou: venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r req.txt
```

### Lancement

```bash
# Démarrer backend et frontend
./start.sh
```

**URLs:**
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- Documentation API: http://localhost:8000/docs

## 📁 Structure du Projet

```
.
├── app/
│   ├── main.py              # API FastAPI
│   ├── document_store.py    # Gestion ChromaDB
│   ├── rag_service.py       # Service RAG
│   ├── deps.py              # Authentification
│   └── config.py            # Configuration
├── data/
│   ├── clientA/             # Documents Client A
│   └── clientB/             # Documents Client B
├── frontend.py              # Interface Streamlit
├── test_separation.py       # Tests d'isolation
├── start.sh                 # Script de lancement
└── req.txt                  # Dépendances Python
```

## 🎯 Utilisation

### Interface Web

1. Ouvrir http://localhost:8501
2. Sélectionner un client (A ou B)
3. Poser une question
4. Voir la réponse avec sources

### API REST

```bash
# Client A
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: tenantA_key" \
  -d '{"question":"Quelle est la procédure de résiliation?"}'

# Client B
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: tenantB_key" \
  -d '{"question":"Comment déclarer un sinistre?"}'
```

## 🧪 Tests

```bash
# Tester l'isolation des tenants
python test_separation.py
```

## 🔑 Clients & API Keys

| Client   | API Key        | Documents                           |
|----------|----------------|-------------------------------------|
| Client A | `tenantA_key`  | Résiliation, RC Pro A               |
| Client B | `tenantB_key`  | Sinistres, RC Pro B                 |

## 🛠️ Technologies

- **Backend**: FastAPI, Uvicorn
- **Base de données**: ChromaDB (vecteurs)
- **Embeddings**: Sentence-Transformers (all-MiniLM-L6-v2)
- **Frontend**: Streamlit
- **HTTP Client**: httpx
- **Python**: 3.9+

## 📝 Licence

MIT

## 🚫 Points de Vigilance (Critères Éliminatoires)

### ✅ Implémenté pour éviter l'élimination :

1. **Pas de réponse cross-tenant** : 
   - ✅ Chaque collection ChromaDB est isolée par tenant
   - ✅ Le `tenant_id` est validé à chaque requête

2. **Toujours des sources** :
   - ✅ Chaque document indexé contient son nom de fichier
   - ✅ Les sources sont retournées dans la réponse

3. **Pas d'invention** :
   - ✅ Réponses basées uniquement sur les documents indexés
   - ✅ Extraits directs des documents (pas de génération)

4. **Gestion "aucune réponse possible"** :
   - ✅ Détection quand distance > 1.0 (pas assez pertinent)
   - ✅ Message clair : "Aucune information pertinente trouvée"

## 📊 Endpoints API

### `POST /query`
Recherche dans les documents du client authentifié

**Headers** :
- `X-API-KEY` : API key du client (obligatoire)

**Body** :
```json
{
  "question": "Votre question"
}
```

**Response** :
```json
{
  "answer": "Réponse basée sur les documents",
  "sources": ["file1.txt", "file2.txt"],
  "has_answer": true,
  "tenant_id": "clientA"
}
```

### `GET /health/{tenant_id}`
Vérification de la santé et statistiques du tenant

### `POST /reload-documents`
Recharge les documents du tenant (utile pour le développement)

## 🔧 Configuration

Les API keys sont définies dans [app/config.py](app/config.py):

```python
API_KEYS = {
    "tenantA_key": "clientA",
    "tenantB_key": "clientB",
}
```

## 📝 Ajout de Documents

Pour ajouter des documents à un client :

1. Créer un fichier `.txt` dans le répertoire du client :
   - `data/clientA/` pour le Client A
   - `data/clientB/` pour le Client B

2. Redémarrer le backend ou appeler l'endpoint `/reload-documents`

## ⚡ Performance et Limites

- **Premier lancement** : Téléchargement du modèle d'embeddings (~90MB)
- **Indexation** : ~1 seconde par document au démarrage
- **Recherche** : <200ms par requête
- **Limite** : Système de test, pas optimisé pour des milliers de documents

## 🧩 Extensions Possibles

Pour un système de production, envisager :

1. **LLM pour la génération** : Intégrer GPT/Claude pour synthétiser les réponses
2. **Base de données** : PostgreSQL pour les métadonnées
3. **Cache** : Redis pour les requêtes fréquentes
4. **Chunking** : Découper les documents en chunks pour meilleure précision
5. **Monitoring** : Logs structurés, métriques, alertes
6. **Tests** : Suite de tests automatisés pour validation continue

## 📄 Licence

Projet de test pour recrutement.

## 👤 Auteur

Développé dans le cadre d'un test technique.

---

**Temps de développement estimé** : 4-5 heures
# model-separation-clients
# model-separation-clients
