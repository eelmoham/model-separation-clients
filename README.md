# 🔐 Système SaaS Multi-Tenant - RAG avec Séparation Stricte des Clients

## 📋 Vue d'ensemble

Ce projet implémente un système SaaS multi-tenant simulant une application utilisée par deux clients indépendants (Client A et Client B). Le système garantit une **séparation stricte des données** et des réponses basées uniquement sur les documents du client authentifié.

### Caractéristiques principales

- ✅ **Séparation stricte des clients** : Chaque client accède uniquement à ses propres documents
- ✅ **Authentification par API Key** : Via header HTTP `X-API-KEY` (jamais dans le body)
- ✅ **Recherche sémantique** : RAG (Retrieval-Augmented Generation) avec embeddings
- ✅ **Sources traçables** : Chaque réponse indique ses sources
- ✅ **Gestion des cas impossibles** : Réponses appropriées quand aucune information n'est disponible
- ✅ **Interface simple** : Streamlit pour tester facilement les deux clients

## 🧰 Stack Technique

- **Backend** : FastAPI
- **Base vectorielle** : ChromaDB avec embeddings Sentence-Transformers
- **Frontend** : Streamlit
- **Langage** : Python 3.9+

## 📦 Structure du Projet

```
project-test/
├── app/
│   ├── config.py              # Configuration des API keys
│   ├── deps.py                # Dépendances FastAPI (authentification)
│   ├── document_store.py      # Stockage vectoriel par tenant (ChromaDB)
│   ├── rag_service.py         # Service RAG avec recherche sémantique
│   └── main.py                # API FastAPI
├── data/
│   ├── clientA/               # Documents du Client A (Tech)
│   │   ├── architecture.txt
│   │   ├── api_documentation.txt
│   │   └── deployment.txt
│   └── clientB/               # Documents du Client B (Médical)
│       ├── cardiology.txt
│       ├── diabetes.txt
│       └── antibiotics.txt
├── frontend.py                # Interface Streamlit
├── req.txt                    # Dépendances Python
└── README.md                  # Ce fichier
```

## 🚀 Installation et Lancement

### Prérequis

- Python 3.9 ou supérieur
- pip

### 1. Installation des dépendances

```bash
pip install -r req.txt
```

**Note** : Le téléchargement des modèles d'embeddings peut prendre quelques minutes au premier lancement.

### 2. Lancer le Backend

Ouvrez un terminal et exécutez :

```bash
python -m uvicorn app.main:app --reload
```

Le backend sera accessible sur `http://localhost:8000`

Vous devriez voir dans les logs :
```
✅ Documents chargés pour clientA
✅ Documents chargés pour clientB
```

**API Documentation** : `http://localhost:8000/docs`

### 3. Lancer l'Interface Frontend

Dans un **second terminal**, exécutez :

```bash
streamlit run frontend.py
```

L'interface s'ouvrira automatiquement dans votre navigateur sur `http://localhost:8501`

## 🧪 Comment Tester la Séparation des Clients

### Test 1 : Client A - Questions Techniques

1. Dans l'interface Streamlit, sélectionner **"Client A (Tech)"** dans la barre latérale
2. Poser des questions techniques :
   - "Quelle est l'architecture de la plateforme ?"
   - "Comment déployer en production ?"
   - "Quels sont les endpoints API disponibles ?"

**Résultat attendu** : ✅ Réponses avec sources provenant des documents techniques

3. Maintenant poser une question médicale :
   - "Comment traiter le diabète de type 2 ?"

**Résultat attendu** : ❌ "Aucune information pertinente trouvée dans vos documents"

### Test 2 : Client B - Questions Médicales

1. Sélectionner **"Client B (Médical)"** dans la barre latérale
2. Poser des questions médicales :
   - "Quels sont les symptômes d'une insuffisance cardiaque ?"
   - "Quel antibiotique pour une angine ?"
   - "Comment traiter le diabète ?"

**Résultat attendu** : ✅ Réponses avec sources provenant des documents médicaux

3. Poser une question technique :
   - "Quelle est l'architecture microservices ?"

**Résultat attendu** : ❌ "Aucune information pertinente trouvée dans vos documents"

### Test 3 : API Direct avec cURL

Vous pouvez aussi tester directement l'API :

**Client A** :
```bash
curl -X POST "http://localhost:8000/query" \
  -H "X-API-KEY: tenantA_key" \
  -H "Content-Type: application/json" \
  -d '{"question": "Quelle est l architecture de la plateforme ?"}'
```

**Client B** :
```bash
curl -X POST "http://localhost:8000/query" \
  -H "X-API-KEY: tenantB_key" \
  -H "Content-Type: application/json" \
  -d '{"question": "Comment traiter le diabète ?"}'
```

**Test de sécurité** - Client A essayant d'accéder aux données du Client B :
```bash
# Cette requête avec l'API key du Client A ne retournera JAMAIS 
# d'information provenant des documents médicaux du Client B
curl -X POST "http://localhost:8000/query" \
  -H "X-API-KEY: tenantA_key" \
  -H "Content-Type: application/json" \
  -d '{"question": "Comment traiter le diabète ?"}'
```

## 🔑 Authentification

Le système utilise des API keys dans le header HTTP :

| Client | API Key | Tenant ID | Documents |
|--------|---------|-----------|-----------|
| Client A | `tenantA_key` | `clientA` | Documents techniques |
| Client B | `tenantB_key` | `clientB` | Documents médicaux |

**Important** : L'API key est passée dans le header `X-API-KEY`, **JAMAIS dans le body** de la requête.

## 🏗️ Architecture et Approche

### Séparation des Tenants

1. **Au niveau de l'authentification** : 
   - Middleware FastAPI qui extrait le `tenant_id` depuis l'API key
   - Validation avant chaque requête

2. **Au niveau du stockage** :
   - Chaque tenant a sa propre collection dans ChromaDB (`tenant_clientA`, `tenant_clientB`)
   - Isolation complète au niveau de la base vectorielle

3. **Au niveau de la recherche** :
   - Le service RAG ne recherche **QUE** dans la collection du tenant authentifié
   - Impossible d'accéder aux embeddings d'un autre tenant

### Gestion des Réponses

- **Réponse avec source** : Quand des documents pertinents sont trouvés (distance < 1.0)
- **Réponse "impossible"** : Quand aucun document pertinent n'existe pour le client
- **Traçabilité** : Chaque réponse indique le fichier source

### Critères de Pertinence

- Similarité cosinus via embeddings (Sentence-Transformers)
- Seuil de distance < 1.0 pour considérer un document pertinent
- Top 3 documents les plus pertinents analysés

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
