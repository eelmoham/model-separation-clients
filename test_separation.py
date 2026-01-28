#!/usr/bin/env python3
"""
Script de test automatique pour valider la séparation des tenants
"""
import httpx
import time
import sys

API_URL = "http://localhost:8000"

TESTS = [
    {
        "name": "Client A - Question technique (devrait réussir)",
        "api_key": "tenantA_key",
        "question": "Quelle est l'architecture de la plateforme ?",
        "should_find_answer": True,
        "expected_tenant": "clientA"
    },
    {
        "name": "Client A - Question médicale (devrait échouer)",
        "api_key": "tenantA_key",
        "question": "Comment traiter le diabète de type 2 ?",
        "should_find_answer": False,
        "expected_tenant": "clientA"
    },
    {
        "name": "Client B - Question médicale (devrait réussir)",
        "api_key": "tenantB_key",
        "question": "Quels sont les symptômes d'une insuffisance cardiaque ?",
        "should_find_answer": True,
        "expected_tenant": "clientB"
    },
    {
        "name": "Client B - Question technique (devrait échouer)",
        "api_key": "tenantB_key",
        "question": "Comment déployer sur Kubernetes ?",
        "should_find_answer": False,
        "expected_tenant": "clientB"
    },
    {
        "name": "API Key invalide (devrait être refusé)",
        "api_key": "invalid_key",
        "question": "Test",
        "should_fail_auth": True
    }
]

def run_tests():
    """Exécute tous les tests"""
    print("🧪 Démarrage des tests de séparation des tenants\n")
    print("=" * 70)
    
    # Vérifier que le backend est accessible
    try:
        response = httpx.get(f"{API_URL}/", timeout=5)
        if response.status_code != 200:
            print("❌ Backend non accessible")
            sys.exit(1)
        print("✅ Backend accessible\n")
    except Exception as e:
        print(f"❌ Erreur de connexion au backend: {e}")
        print("\n💡 Assurez-vous que le backend est lancé:")
        print("   python -m uvicorn app.main:app --reload\n")
        sys.exit(1)
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(TESTS, 1):
        print(f"\nTest {i}/{len(TESTS)}: {test['name']}")
        print("-" * 70)
        
        try:
            headers = {"X-API-KEY": test['api_key']}
            payload = {"question": test['question']}
            
            response = httpx.post(
                f"{API_URL}/query",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # Test d'authentification
            if test.get('should_fail_auth'):
                if response.status_code == 401:
                    print("✅ PASS - Authentification refusée comme attendu")
                    passed += 1
                else:
                    print(f"❌ FAIL - Devrait refuser (401), reçu: {response.status_code}")
                    failed += 1
                continue
            
            if response.status_code != 200:
                print(f"❌ FAIL - Erreur HTTP {response.status_code}: {response.text}")
                failed += 1
                continue
            
            result = response.json()
            
            # Vérifier le tenant
            if result['tenant_id'] != test['expected_tenant']:
                print(f"❌ FAIL - Mauvais tenant: {result['tenant_id']} vs {test['expected_tenant']}")
                failed += 1
                continue
            
            # Vérifier la présence/absence de réponse
            if test['should_find_answer']:
                if result['has_answer'] and result['sources']:
                    print(f"✅ PASS - Réponse trouvée avec sources: {result['sources']}")
                    passed += 1
                else:
                    print(f"❌ FAIL - Devrait trouver une réponse")
                    print(f"   has_answer: {result['has_answer']}")
                    print(f"   sources: {result['sources']}")
                    failed += 1
            else:
                if not result['has_answer']:
                    print(f"✅ PASS - Aucune réponse trouvée (comme attendu)")
                    passed += 1
                else:
                    print(f"❌ FAIL - Ne devrait PAS trouver de réponse")
                    print(f"   has_answer: {result['has_answer']}")
                    print(f"   sources: {result['sources']}")
                    print(f"   ⚠️  VIOLATION DE LA SÉPARATION DES TENANTS!")
                    failed += 1
            
        except Exception as e:
            print(f"❌ FAIL - Exception: {e}")
            failed += 1
    
    # Résumé
    print("\n" + "=" * 70)
    print(f"\n📊 Résultats: {passed} PASS, {failed} FAIL sur {len(TESTS)} tests")
    
    if failed == 0:
        print("\n✅ TOUS LES TESTS SONT PASSÉS!")
        print("   La séparation des tenants fonctionne correctement.")
        return 0
    else:
        print(f"\n❌ {failed} TEST(S) EN ÉCHEC")
        print("   Vérifiez la séparation des tenants.")
        return 1

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
