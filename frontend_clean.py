import streamlit as st
import httpx
st.set_page_config(
    page_title="SaaS Multi-Tenant RAG",
    page_icon="🔐",
    layout="wide"
)

API_URL = "http://localhost:8000"

TENANTS = {
    "Client A": {
        "api_key": "tenantA_key",
        "tenant_id": "clientA",
        "description": "Documents d'assurance - Résiliation & RC Pro A",
        "icon": "🏢",
        "questions": [
            "Quelle est la procédure de résiliation?",
            "Quel est le délai d'envoi de l'accusé de réception?",
            "Qui valide les dossiers sensibles?",
            "Que couvre la RC Pro A?",
            "Quelles sont les exclusions de la RC Pro A?",
            "Comment déclarer un sinistre pour la RC Pro A?",
            "Quelle est la limite de hauteur pour les travaux?"
        ]
    },
    "Client B": {
        "api_key": "tenantB_key",
        "tenant_id": "clientB",
        "description": "Documents d'assurance - Sinistres & RC Pro B",
        "icon": "🏛️",
        "questions": [
            "Quelle est la procédure de déclaration de sinistre?",
            "Quel est le délai de déclaration d'un sinistre?",
            "Comment est effectué le suivi du sinistre?",
            "Que couvre la RC Pro B?",
            "Quelles sont les exclusions de la RC Pro B?",
            "Comment déclarer un sinistre pour la RC Pro B?",
            "Que se passe-t-il pour la sous-traitance non déclarée?"
        ]
    }
}

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'selected_tenant' not in st.session_state:
    st.session_state.selected_tenant = "Client A"

st.title("🔐 Assistant Multi-Tenant")
st.caption("Recherche documentaire sécurisée")
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    tenant_info = TENANTS[st.session_state.selected_tenant]
    st.info(f"{tenant_info['icon']} **{st.session_state.selected_tenant}**\n\n{tenant_info['description']}")

with col2:
    new_tenant = st.selectbox(
        "Changer de client",
        options=list(TENANTS.keys()),
        index=list(TENANTS.keys()).index(st.session_state.selected_tenant)
    )
    if new_tenant != st.session_state.selected_tenant:
        st.session_state.selected_tenant = new_tenant
        st.session_state.messages = []
        st.rerun()

st.divider()

if len(st.session_state.messages) == 0:
    st.subheader("💡 Questions suggérées")
    st.caption("Cliquez sur une question pour la poser")
    
    tenant_info = TENANTS[st.session_state.selected_tenant]
    cols = st.columns(2)
    for idx, question in enumerate(tenant_info['questions']):
        with cols[idx % 2]:
            if st.button(question, key=f"q_{idx}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": question})
                try:
                    response = httpx.post(
                        f"{API_URL}/query",
                        headers={"X-API-KEY": tenant_info['api_key']},
                        json={"question": question},
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": result['answer'],
                            "sources": result.get('sources', [])
                        })
                    else:
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"❌ Erreur {response.status_code}",
                            "sources": []
                        })
                except Exception as e:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"❌ Erreur: {str(e)}",
                        "sources": []
                    })
                
                st.rerun()
    
    st.divider()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message.get("sources"):
            st.caption("📄 **Sources:** " + ", ".join(message["sources"]))

if prompt := st.chat_input("Posez votre question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.write(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Recherche en cours..."):
            try:
                tenant_info = TENANTS[st.session_state.selected_tenant]
                response = httpx.post(
                    f"{API_URL}/query",
                    headers={"X-API-KEY": tenant_info['api_key']},
                    json={"question": prompt},
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.write(result['answer'])
                    
                    if result.get('sources'):
                        st.caption("📄 **Sources:** " + ", ".join(result['sources']))
                    else:
                        st.warning("⚠️ Aucune source trouvée")
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result['answer'],
                        "sources": result.get('sources', [])
                    })
                else:
                    error = f"❌ Erreur {response.status_code}"
                    st.error(error)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error,
                        "sources": []
                    })
                    
            except Exception as e:
                error = f"❌ Erreur: {str(e)}"
                st.error(error)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error,
                    "sources": []
                })
