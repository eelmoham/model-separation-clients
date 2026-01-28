#!/bin/bash

# Script de lancement rapide du backend et frontend

echo "🚀 Lancement du système SaaS Multi-Tenant"
echo "========================================"
echo ""

# Vérifier que les dépendances sont installées
if ! python -c "import fastapi" 2>/dev/null; then
    echo "⚠️  Les dépendances ne sont pas installées"
    echo "Installation en cours..."
    pip install -r req.txt
    echo "✅ Dépendances installées"
    echo ""
fi

# Tuer les processus existants si nécessaire
pkill -f "uvicorn app.main:app" 2>/dev/null
pkill -f "streamlit run frontend.py" 2>/dev/null

echo "🔧 Lancement du backend FastAPI..."
python -m uvicorn app.main:app --reload &
BACKEND_PID=$!

# Attendre que le backend démarre
sleep 3

echo "🎨 Lancement de l'interface Streamlit..."
streamlit run frontend.py &
FRONTEND_PID=$!

echo ""
echo "✅ Système démarré!"
echo ""
echo "📍 URLs:"
echo "   - Backend API: http://localhost:8000"
echo "   - Documentation: http://localhost:8000/docs"
echo "   - Frontend: http://localhost:8501"
echo ""
echo "🔑 API Keys:"
echo "   - Client A (Tech): tenantA_key"
echo "   - Client B (Médical): tenantB_key"
echo ""
echo "Pour arrêter: Ctrl+C"
echo ""

# Attendre les processus
wait
