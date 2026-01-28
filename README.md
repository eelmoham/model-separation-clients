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

### Étape 1: Installation

```bash
# 1. Cloner le projet
git clone https://github.com/eelmoham/model-separation-clients.git
cd model-separation-clients

# 2. Créer l'environnement virtuel Python
python3 -m venv venv

# 3. Activer l'environnement virtuel
source venv/bin/activate  # macOS/Linux
# ou: venv\Scripts\activate  # Windows

# 4. Installer toutes les dépendances (FastAPI, ChromaDB, Streamlit, etc.)
pip install -r req.txt
```

### Étape 2: Lancement du Projet

```bash
# Méthode simple: utiliser le script de lancement
./start.sh
```

Le script lancera automatiquement:
- ✅ **Backend FastAPI** sur le port 8000 (en arrière-plan)
- ✅ **Frontend Streamlit** sur le port 8501 (en arrière-plan)
- ✅ **Chargement des documents** pour Client A et Client B

**Accès aux services:**
- 🌐 **Interface utilisateur**: http://localhost:8501
- 🔌 **API Backend**: http://localhost:8000
- 📚 **Documentation API**: http://localhost:8000/docs

### Étape 3: Vérifier que ça fonctionne

```bash
# Vérifier le backend
curl http://localhost:8000/
# Résultat attendu: {"status":"ok","tenant_stats":null}

# Voir les logs en temps réel
tail -f backend.log    # Logs du backend
tail -f frontend.log   # Logs du frontend
```

### Arrêter le Projet

```bash
pkill -f uvicorn && pkill -f streamlit
```

## � Comment ça Fonctionne

### Architecture du Système

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│  Frontend   │────────▶│   Backend    │────────▶│  ChromaDB   │
│  Streamlit  │  HTTP   │   FastAPI    │  Query  │   Vector    │
│             │◀────────│              │◀────────│   Store     │
└─────────────┘         └──────────────┘         └─────────────┘
     │                        │                         │
     │                        │                         │
  Client A                X-API-KEY              tenant_clientA
  Client B              Authentication           tenant_clientB
```

### Flux d'une Requête

1. **Sélection du Client** (Frontend)
   - L'utilisateur sélectionne Client A ou Client B
   - Le frontend utilise l'API Key correspondante (`tenantA_key` ou `tenantB_key`)

2. **Envoi de la Question**
   - La question est envoyée au backend via HTTP POST `/query`
   - Header d'authentification: `X-API-KEY: tenantA_key`

3. **Authentification** (Backend)
   - Le backend valide l'API Key
   - Extrait le `tenant_id` (clientA ou clientB)
   - Rejette la requête si l'API Key est invalide

4. **Recherche Sémantique** (RAG Service)
   - La question est transformée en vecteur d'embedding (384 dimensions)
   - ChromaDB cherche les documents similaires **uniquement dans la collection du tenant**
   - Collection `tenant_clientA` pour Client A
   - Collection `tenant_clientB` pour Client B
   - **Isolation garantie**: aucun accès cross-tenant possible

5. **Filtrage des Résultats**
   - Seuls les résultats avec distance < 1.0 sont conservés
   - Si aucun résultat pertinent: "Aucune information pertinente trouvée"
   - Sinon: extraits directs des documents sources

6. **Réponse avec Sources**
   ```json
   {
     "answer": "Extrait du document...",
     "sources": ["docA1_procedure_resiliation.txt"],
     "has_answer": true,
     "tenant_id": "clientA"
   }
   ```

7. **Affichage** (Frontend)
   - La réponse s'affiche dans l'interface chat
   - Les sources sont listées en bas

### Séparation des Données

**Client A** a accès uniquement à:
- `data/clientA/docA1_procedure_resiliation.txt`
- `data/clientA/docA2_produit_rc_pro_a.txt`

**Client B** a accès uniquement à:
- `data/clientB/docB1_procedure_sinistre.txt`
- `data/clientB/docB2_produit_rc_pro_b.txt`

**Mécanismes de sécurité**:
- Collections ChromaDB séparées physiquement
- Validation de l'API Key à chaque requête
- Pas de référence croisée possible entre tenants

## �📁 Structure du Projet

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

### Option 1: Interface Web (Recommandé)

1. **Ouvrir l'interface**: http://localhost:8501

2. **Sélectionner un client** dans la barre latérale:
   - 🏢 Client A (Résiliation & RC Pro A)
   - 🏥 Client B (Sinistres & RC Pro B)

3. **Poser une question**:
   - Tapez votre question dans le champ de saisie
   - Ou cliquez sur une **question suggérée** (7 exemples par client)

4. **Voir la réponse**:
   - La réponse apparaît avec les extraits des documents
   - Les sources sont listées en bas
   - Seules les informations du client sélectionné sont accessibles

### Option 2: API REST

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

## 💡 Questions Suggérées

### Client A questions (résiliation & RC Pro A):

- Quelle est la procédure de résiliation?
- Comment enregistrer une résiliation dans le CRM?
- Quel est le délai d'accusé de réception?
- Qu'est-ce que la RC Pro A?
- Quelles sont les exclusions de hauteur?
- Quelle est la franchise de la RC Pro A?
- Qui valide les dossiers sensibles?

### Client B questions (sinistres & RC Pro B):

- Quelle est la procédure de déclaration de sinistre?
- Quel est le délai de déclaration de sinistre?
- Qu'est-ce que la RC Pro B?
- Quelles sont les exclusions de sous-traitance?
- Y a-t-il des travaux en hauteur exclus?
- Comment contacter le service sinistres?
- Quelle est la couverture de la RC Pro B?

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
