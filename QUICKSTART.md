# 🚀 Quick Start Guide

## Installation Rapide

```bash
# Installer les dépendances
pip install -r req.txt
```

## Lancement

### Option 1 : Script Automatique (Recommandé)

```bash
./start.sh
```

Cela démarre automatiquement le backend et le frontend.

### Option 2 : Lancement Manuel

**Terminal 1 - Backend:**
```bash
python -m uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
streamlit run frontend.py
```

## Accès

- **Interface Web** : http://localhost:8501
- **API Backend** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs

## Test de Séparation

### Test Automatique

```bash
python test_separation.py
```

### Test Manuel via Interface

1. Ouvrir http://localhost:8501
2. Sélectionner "Client A (Tech)"
3. Poser : "Quelle est l'architecture ?" → ✅ Devrait répondre
4. Poser : "Comment traiter le diabète ?" → ❌ Ne devrait PAS répondre
5. Changer pour "Client B (Médical)"
6. Poser : "Comment traiter le diabète ?" → ✅ Devrait répondre
7. Poser : "Quelle est l'architecture ?" → ❌ Ne devrait PAS répondre

### Test via cURL

**Client A (Tech):**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "X-API-KEY: tenantA_key" \
  -H "Content-Type: application/json" \
  -d '{"question": "Quelle est l architecture ?"}'
```

**Client B (Médical):**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "X-API-KEY: tenantB_key" \
  -H "Content-Type: application/json" \
  -d '{"question": "Comment traiter le diabète ?"}'
```

**Test Cross-Tenant (devrait échouer):**
```bash
# Client A essayant d'accéder aux données du Client B
curl -X POST "http://localhost:8000/query" \
  -H "X-API-KEY: tenantA_key" \
  -H "Content-Type: application/json" \
  -d '{"question": "Comment traiter le diabète ?"}'
# Résultat attendu: "Aucune information pertinente trouvée"
```

## Structure du Projet

```
project-test/
├── app/                    # Backend FastAPI
│   ├── config.py          # Configuration (API keys)
│   ├── deps.py            # Authentification
│   ├── document_store.py  # ChromaDB (séparation par tenant)
│   ├── rag_service.py     # Service RAG
│   └── main.py            # API FastAPI
├── data/                   # Documents par tenant
│   ├── clientA/           # Documents techniques
│   └── clientB/           # Documents médicaux
├── frontend.py            # Interface Streamlit
├── test_separation.py     # Tests automatiques
├── req.txt               # Dépendances
├── README.md             # Documentation complète
├── APPROCHE.md           # Explication technique
└── start.sh              # Script de lancement
```

## API Keys

| Client | API Key | Documents |
|--------|---------|-----------|
| Client A | `tenantA_key` | Documents techniques (architecture, API, déploiement) |
| Client B | `tenantB_key` | Documents médicaux (cardiologie, diabète, antibiotiques) |

## Troubleshooting

**Erreur "Backend non accessible":**
```bash
# Vérifier que le backend est lancé
python -m uvicorn app.main:app --reload
```

**Erreur "Module not found":**
```bash
# Réinstaller les dépendances
pip install -r req.txt
```

**Erreur au premier lancement:**
- Le téléchargement des modèles d'embeddings peut prendre 2-3 minutes
- Attendre que les logs affichent "✅ Documents chargés pour clientA/B"

## Points Clés de Validation

✅ **Séparation stricte** : Chaque client voit uniquement ses documents
✅ **Authentification header** : X-API-KEY obligatoire (jamais dans le body)
✅ **Sources traçables** : Chaque réponse indique ses sources
✅ **Gestion "pas de réponse"** : Message clair quand aucune info disponible

## Conformité Test Technique

- [x] Séparation des clients via collections ChromaDB isolées
- [x] Authentification par header X-API-KEY
- [x] Backend FastAPI
- [x] Interface Streamlit simple
- [x] Documents différents (Tech vs Médical)
- [x] README complet avec instructions
- [x] Tests de non-régression
- [x] Explication de l'approche (APPROCHE.md)

Temps de développement : ~4-5 heures
