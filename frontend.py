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

# Custom CSS for ChatGPT-like interface
st.markdown("""
<style>
    /* Main container */
    .main {
        background-color: #ffffff;
    }
    
    /* Header styling */
    .header-container {
        padding: 1rem 0 2rem 0;
        text-align: center;
        border-bottom: 1px solid #e5e7eb;
        margin-bottom: 2rem;
    }
    
    .main-title {
        font-size: 2rem;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        font-size: 0.95rem;
        color: #6b7280;
    }
    
    /* Client selector */
    .client-selector {
        background: #f9fafb;
        padding: 1rem;
        border-radius: 0.75rem;
        border: 1px solid #e5e7eb;
        margin-bottom: 1.5rem;
    }
    
    /* Message bubbles */
    .user-message {
        background: #f3f4f6;
        padding: 1rem 1.25rem;
        border-radius: 1.25rem;
        margin: 1rem 0;
        color: #1f2937;
        font-size: 0.95rem;
    }
    
    .assistant-message {
        background: #ffffff;
        padding: 1rem 1.25rem;
        border-radius: 1.25rem;
        margin: 1rem 0;
        color: #1f2937;
        font-size: 0.95rem;
        border: 1px solid #e5e7eb;
    }
    
    /* Source tags */
    .source-tag {
        display: inline-block;
        background: #dbeafe;
        color: #1e40af;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        margin: 0.25rem;
        font-weight: 500;
    }
    
    /* Status indicators */
    .status-success {
        color: #059669;
        font-weight: 500;
    }
    
    .status-warning {
        color: #d97706;
        font-weight: 500;
    }
    
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 1.5rem;
        border: 2px solid #e5e7eb;
        padding: 0.75rem 1.25rem;
        font-size: 0.95rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
        border-radius: 1.5rem;
        padding: 0.75rem 2rem;
        font-weight: 500;
        font-size: 0.95rem;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        border-radius: 0.75rem;
        border: 2px solid #e5e7eb;
    }
    
    /* Animation for typing effect */
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0; }
    }
    
    .typing-cursor {
        animation: blink 1s infinite;
    }
</style>
""", unsafe_allow_html=True)

# Titre principal avec style moderne
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

# Client selector in a nice container
with st.container():
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
        <div style="text-align: center; margin: 0.5rem 0 1.5rem 0;">
            <span style="font-size: 1.5rem;">{tenant_info['icon']}</span>
            <span style="color: #6b7280; font-size: 0.9rem; margin-left: 0.5rem;">{tenant_info['description']}</span>
        </div>
        """, unsafe_allow_html=True)

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'<div class="user-message">💬 {message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="assistant-message">{message["content"]}</div>', unsafe_allow_html=True)
        if message.get("sources"):
            sources_html = "".join([f'<span class="source-tag">📄 {src}</span>' for src in message["sources"]])
            st.markdown(f'<div style="margin-top: 0.5rem;">{sources_html}</div>', unsafe_allow_html=True)

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
            
            # Simulate streaming effect (ChatGPT-like)
            displayed_text = ""
            response_container = st.container()
            
            with response_container:
                for i in range(0, len(answer), 3):  # Stream 3 characters at a time
                    displayed_text = answer[:i+3]
                    response_placeholder.markdown(
                        f'<div class="assistant-message">{displayed_text}<span class="typing-cursor">▊</span></div>', 
                        unsafe_allow_html=True
                    )
                    time.sleep(0.01)  # Adjust speed here
                
                # Final display without cursor
                response_placeholder.markdown(
                    f'<div class="assistant-message">{answer}</div>', 
                    unsafe_allow_html=True
                )
                
                # Show sources
                if sources:
                    sources_html = "".join([f'<span class="source-tag">📄 {src}</span>' for src in sources])
                    st.markdown(f'<div style="margin-top: 0.5rem;">{sources_html}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="margin-top: 0.5rem; color: #d97706; font-size: 0.85rem;">⚠️ Aucune source trouvée dans vos documents</div>', unsafe_allow_html=True)
            
            # Add to message history
            st.session_state.messages.append({
                "role": "assistant", 
                "content": answer,
                "sources": sources
            })
            
        elif response.status_code == 401:
            error_msg = "❌ Erreur d'authentification"
            response_placeholder.markdown(f'<div class="assistant-message" style="color: #dc2626;">{error_msg}</div>', unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": error_msg, "sources": []})
        else:
            error_msg = f"❌ Erreur: {response.status_code}"
            response_placeholder.markdown(f'<div class="assistant-message" style="color: #dc2626;">{error_msg}</div>', unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": error_msg, "sources": []})
            
    except httpx.ConnectError:
        error_msg = "❌ Impossible de se connecter au backend"
        response_placeholder.markdown(f'<div class="assistant-message" style="color: #dc2626;">{error_msg}</div>', unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": error_msg, "sources": []})
    except Exception as e:
        error_msg = f"❌ Erreur: {str(e)}"
        response_placeholder.markdown(f'<div class="assistant-message" style="color: #dc2626;">{error_msg}</div>', unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": error_msg, "sources": []})
