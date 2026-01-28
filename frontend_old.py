"""
Interface Streamlit pour le système SaaS multi-tenant
"""
import streamlit as st
import httpx
import json
import time

# Configuration de la page
st.set_page_config(
    page_title="SaaS Multi-Tenant RAG",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# URL de l'API
API_URL = "http://localhost:8000"

# Configuration des tenants
TENANTS = {
    "Client A": {
        "api_key": "tenantA_key",
        "tenant_id": "clientA",
        "description": "📄 Documents d'assurance - Résiliation & RC Pro A",
        "icon": "🏢"
    },
    "Client B": {
        "api_key": "tenantB_key",
        "tenant_id": "clientB",
        "description": "📋 Documents d'assurance - Sinistres & RC Pro B",
        "icon": "🏛️"
    }
}

# Simple, Clean CSS
st.markdown("""
<style>
    /* Clean white background */
    .main {
        background-color: #f8f9fa;
    }
    
    .block-container {
        padding: 2rem 1rem;
        max-width: 800px;
    }
    
    /* Simple header */
    .header-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .main-title {
        font-size: 1.75rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        font-size: 0.9rem;
        color: #666;
    }
    
    /* Client card */
    .client-card {
        background: white;
        padding: 1.25rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    /* Simple message bubbles */
    .user-message {
        background: #0066cc;
        color: white;
        padding: 1rem 1.25rem;
        border-radius: 18px 18px 4px 18px;
        margin: 1rem 0;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    .assistant-message {
        background: white;
        color: #1a1a1a;
        padding: 1rem 1.25rem;
        border-radius: 18px 18px 18px 4px;
        margin: 1rem 0;
        font-size: 0.95rem;
        line-height: 1.5;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    /* Source tags */
    .source-tag {
        display: inline-block;
        background: #e8f4f8;
        color: #0066cc;
        padding: 0.35rem 0.75rem;
        border-radius: 16px;
        font-size: 0.85rem;
        margin: 0.25rem;
        font-weight: 500;
    }
    
    /* Chat container */
    .chat-container {
        background: transparent;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        min-height: 400px;
        max-height: 600px;
        overflow-y: auto;
    }
    
    /* Clean scrollbar */
    .chat-container::-webkit-scrollbar {
        width: 6px;
    }
    
    .chat-container::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    .chat-container::-webkit-scrollbar-thumb {
        background: #ccc;
        border-radius: 10px;
    }
    
    .chat-container::-webkit-scrollbar-thumb:hover {
        background: #999;
    }
    
    /* Hide streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Simple selectbox */
    .stSelectbox > div > div {
        background: white;
        border-radius: 8px;
        border: 1px solid #ddd;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-size: 0.9rem;
        font-weight: 500;
        margin: 0.5rem 0;
    }
    
    .status-success {
        background: #d4edda;
        color: #155724;
    }
    
    .status-warning {
        background: #fff3cd;
        color: #856404;
    }
    
    .status-error {
        background: #f8d7da;
        color: #721c24;
    }
    
    /* Client info */
    .client-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .client-description {
        color: #666;
        font-size: 0.9rem;
    }
    
    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 3rem 1rem;
        color: #999;
    }
    
    /* Typing cursor */
    .typing-cursor {
        animation: blink 1s infinite;
        color: #0066cc;
    }
    
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
</style>
""", unsafe_allow_html=True)

# Header with modern design
st.markdown("""
<div class="header-container">
    <div class="main-title">🔐 Assistant Multi-Tenant</div>
    <div class="subtitle">Recherche documentaire sécurisée avec séparation stricte des clients</div>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'selected_tenant' not in st.session_state:
    st.session_state.selected_tenant = "Client A"

# Client selector in premium card
st.markdown('<div class="client-card">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    selected_tenant = st.selectbox(
        "👤 Sélectionner le client",
        options=list(TENANTS.keys()),
        key="tenant_selector",
        label_visibility="collapsed",
        index=list(TENANTS.keys()).index(st.session_state.selected_tenant)
    )
    
    if selected_tenant != st.session_state.selected_tenant:
        st.session_state.selected_tenant = selected_tenant
        st.session_state.messages = []
        st.rerun()
    
    tenant_info = TENANTS[selected_tenant]
    st.markdown(f"""
    <div style="text-align: center; margin: 0.75rem 0;">
        <div class="client-icon">{tenant_info['icon']}</div>
        <div class="client-description">{tenant_info['description']}</div>
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Display chat messages with enhanced design
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'<div class="user-message">💬 {message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="assistant-message">🤖 {message["content"]}</div>', unsafe_allow_html=True)
        if message.get("sources"):
            sources_html = "".join([f'<span class="source-tag">📄 {src}</span>' for src in message["sources"]])
            st.markdown(f'<div style="margin-top: 0.75rem; padding: 0 0.5rem;">{sources_html}</div>', unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("""
    <div class="empty-state">
        <div style="font-size: 3rem; margin-bottom: 1rem;">💬</div>
        <div style="font-size: 1.1rem; font-weight: 500; color: #666;">Commencez une conversation</div>
        <div style="font-size: 0.9rem; margin-top: 0.5rem;">Posez une question sur vos documents</div>
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Question input at the bottom
st.markdown("<br>", unsafe_allow_html=True)
question = st.chat_input("Posez votre question ici...")

if question:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": question})
    
    # Display user message immediately
    st.markdown(f'<div class="user-message">💬 {question}</div>', unsafe_allow_html=True)
    
    # Create placeholder for streaming response
    response_placeholder = st.empty()
    
    try:
        # Call API
        tenant_info = TENANTS[st.session_state.selected_tenant]
        headers = {"X-API-KEY": tenant_info['api_key']}
        payload = {"question": question}
        
        # Show loading
        with st.spinner("🔍 Recherche en cours..."):
            response = httpx.post(
                f"{API_URL}/query",
                headers=headers,
                json=payload,
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            answer = result['answer']
            sources = result.get('sources', [])
            
            # Simulate streaming effect (ChatGPT-like) with enhanced animation
            displayed_text = ""
            response_container = st.container()
            
            with response_container:
                for i in range(0, len(answer), 2):  # Stream 2 characters at a time
                    displayed_text = answer[:i+2]
                    response_placeholder.markdown(
                        f'<div class="assistant-message">🤖 {displayed_text}<span class="typing-cursor">▊</span></div>', 
                        unsafe_allow_html=True
                    )
                    time.sleep(0.008)  # Faster, smoother streaming
                
                # Final display without cursor
                response_placeholder.markdown(
                    f'<div class="assistant-message">🤖 {answer}</div>', 
                    unsafe_allow_html=True
                )
                
                # Show sources with enhanced styling
                if sources:
                    sources_html = "".join([f'<span class="source-tag">📄 {src}</span>' for src in sources])
                    st.markdown(f'<div style="margin-top: 0.75rem; padding: 0 0.5rem;">{sources_html}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="status-badge status-warning" style="margin-top: 0.75rem;">⚠️ Aucune source trouvée</div>', unsafe_allow_html=True)
            
            # Add to message history
            st.session_state.messages.append({
                "role": "assistant", 
                "content": answer,
                "sources": sources
            })
            
        elif response.status_code == 401:
            error_msg = "Erreur d'authentification - API key invalide"
            response_placeholder.markdown(f'<div class="status-badge status-error">❌ {error_msg}</div>', unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": error_msg, "sources": []})
        else:
            error_msg = f"Erreur du serveur: {response.status_code}"
            response_placeholder.markdown(f'<div class="status-badge status-error">❌ {error_msg}</div>', unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": error_msg, "sources": []})
            
    except httpx.ConnectError:
        error_msg = "Impossible de se connecter au backend - Vérifiez que le serveur est démarré"
        response_placeholder.markdown(f'<div class="status-badge status-error">❌ {error_msg}</div>', unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": error_msg, "sources": []})
    except Exception as e:
        error_msg = f"Erreur inattendue: {str(e)}"
        response_placeholder.markdown(f'<div class="status-badge status-error">❌ {error_msg}</div>', unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": error_msg, "sources": []})
