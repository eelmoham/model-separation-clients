"""
Interface Streamlit pour le système SaaS multi-tenant - Modern Chatbot Design
"""
import streamlit as st
import httpx
import json
import time

# Configuration de la page
st.set_page_config(
    page_title="SaaS Multi-Tenant RAG",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# URL de l'API
API_URL = "http://localhost:8000"

# Configuration des tenants
TENANTS = {
    "Client A": {
        "api_key": "tenantA_key",
        "tenant_id": "clientA",
        "description": "Documents d'assurance - Résiliation & RC Pro A",
        "icon": "🏢",
        "color": "blue",
        "gradient": "from-blue-500 to-blue-600"
    },
    "Client B": {
        "api_key": "tenantB_key",
        "tenant_id": "clientB",
        "description": "Documents d'assurance - Sinistres & RC Pro B",
        "icon": "🏛️",
        "color": "purple",
        "gradient": "from-purple-500 to-purple-600"
    }
}

# Enhanced Tailwind CSS + Custom Styles
st.markdown("""
<script src="https://cdn.tailwindcss.com"></script>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main background */
    .main {
        background: #f8fafc;
    }
    
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    header {visibility: hidden;}
    
    /* Chat container */
    .stChatFloatingInputContainer {
        bottom: 20px;
        background: transparent;
        padding: 0 2rem;
    }
    
    /* Chat input styling */
    .stChatInputContainer {
        background: white;
        border-radius: 24px;
        border: 2px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .stChatInputContainer:focus-within {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    /* Message styling */
    .stChatMessage {
        background: transparent !important;
        padding: 1rem 2rem !important;
    }
    
    /* User message bubble */
    [data-testid="chat-message-user"] {
        background: transparent !important;
    }
    
    /* Assistant message bubble */
    [data-testid="chat-message-assistant"] {
        background: transparent !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
    
    /* Animations */
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .message-animation {
        animation: slideIn 0.3s ease-out;
    }
    
    /* Typing indicator */
    .typing-indicator {
        display: inline-flex;
        gap: 4px;
        padding: 12px 16px;
        background: white;
        border-radius: 18px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .typing-dot {
        width: 8px;
        height: 8px;
        background: #94a3b8;
        border-radius: 50%;
        animation: typing 1.4s infinite;
    }
    
    .typing-dot:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .typing-dot:nth-child(3) {
        animation-delay: 0.4s;
    }
    
    @keyframes typing {
        0%, 60%, 100% {
            transform: translateY(0);
            opacity: 0.7;
        }
        30% {
            transform: translateY(-10px);
            opacity: 1;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'selected_tenant' not in st.session_state:
    st.session_state.selected_tenant = "Client A"

# Get current tenant info
tenant_info = TENANTS[st.session_state.selected_tenant]

# Fixed header with client selector
st.markdown(f"""
<div class="fixed top-0 left-0 right-0 z-50 bg-white border-b border-gray-200" style="padding: 0;">
    <div class="max-w-4xl mx-auto">
        <!-- Header -->
        <div class="flex items-center justify-between p-4">
            <div class="flex items-center space-x-3">
                <div class="w-12 h-12 bg-gradient-to-br {tenant_info['gradient']} rounded-xl flex items-center justify-center text-2xl shadow-lg">
                    {tenant_info['icon']}
                </div>
                <div>
                    <h1 class="text-xl font-bold text-gray-900">Assistant Multi-Tenant</h1>
                    <p class="text-sm text-gray-500">{tenant_info['description']}</p>
                </div>
            </div>
            <div class="flex items-center space-x-2">
                <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span class="text-sm text-gray-600 font-medium">En ligne</span>
            </div>
        </div>
    </div>
</div>

<!-- Spacer for fixed header -->
<div style="height: 88px;"></div>
""", unsafe_allow_html=True)

# Client selector dropdown (collapsible)
with st.expander("🔄 Changer de client", expanded=False):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        selected_tenant = st.selectbox(
            "Sélectionnez un client",
            options=list(TENANTS.keys()),
            index=list(TENANTS.keys()).index(st.session_state.selected_tenant),
            label_visibility="collapsed"
        )
        
        if selected_tenant != st.session_state.selected_tenant:
            st.session_state.selected_tenant = selected_tenant
            st.session_state.messages = []
            st.rerun()

# Welcome message if no messages
if len(st.session_state.messages) == 0:
    st.markdown(f"""
    <div class="max-w-2xl mx-auto text-center py-12">
        <div class="mb-6">
            <div class="inline-block w-20 h-20 bg-gradient-to-br {tenant_info['gradient']} rounded-full flex items-center justify-center text-4xl shadow-xl mb-4">
                {tenant_info['icon']}
            </div>
        </div>
        <h2 class="text-3xl font-bold text-gray-900 mb-3">Bonjour! 👋</h2>
        <p class="text-lg text-gray-600 mb-8">Comment puis-je vous aider aujourd'hui?</p>
        
        <!-- Suggestion cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-8">
            <div class="bg-white rounded-xl p-5 shadow-md border border-gray-200 hover:shadow-lg transition-shadow cursor-pointer">
                <div class="text-3xl mb-3">📄</div>
                <h3 class="font-semibold text-gray-900 mb-2">Rechercher un document</h3>
                <p class="text-sm text-gray-600">Posez une question sur vos documents</p>
            </div>
            <div class="bg-white rounded-xl p-5 shadow-md border border-gray-200 hover:shadow-lg transition-shadow cursor-pointer">
                <div class="text-3xl mb-3">💡</div>
                <h3 class="font-semibold text-gray-900 mb-2">Obtenir des informations</h3>
                <p class="text-sm text-gray-600">Trouvez rapidement ce que vous cherchez</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Display chat messages with modern bubble design
for idx, message in enumerate(st.session_state.messages):
    if message["role"] == "user":
        # User message (right-aligned)
        st.markdown(f"""
        <div class="flex justify-end mb-4 message-animation px-4">
            <div class="max-w-[70%]">
                <div class="bg-gradient-to-br {tenant_info['gradient']} text-white rounded-3xl rounded-tr-md px-5 py-3 shadow-md">
                    <p class="text-[15px] leading-relaxed">{message["content"]}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Assistant message (left-aligned)
        sources_html = ""
        if message.get("sources"):
            sources_badges = " ".join([
                f'<span class="inline-flex items-center bg-blue-50 text-blue-700 text-xs font-medium px-3 py-1.5 rounded-full mr-2 mb-2 border border-blue-200">'
                f'<svg class="w-3 h-3 mr-1.5" fill="currentColor" viewBox="0 0 20 20"><path d="M9 2a2 2 0 00-2 2v8a2 2 0 002 2h6a2 2 0 002-2V6.414A2 2 0 0016.414 5L14 2.586A2 2 0 0012.586 2H9z"/><path d="M3 8a2 2 0 012-2v10h8a2 2 0 01-2 2H5a2 2 0 01-2-2V8z"/></svg>'
                f'{src}</span>'
                for src in message["sources"]
            ])
            sources_html = f'<div class="mt-3 flex flex-wrap">{sources_badges}</div>'
        elif message.get("content") and "Aucune source trouvée" not in message.get("content", ""):
            sources_html = '<div class="mt-3 bg-yellow-50 border border-yellow-200 rounded-lg p-3 flex items-start"><svg class="w-5 h-5 text-yellow-600 mr-2 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/></svg><p class="text-sm text-yellow-800">Aucune source trouvée dans vos documents</p></div>'
        
        st.markdown(f"""
        <div class="flex justify-start mb-4 message-animation px-4">
            <div class="flex items-start max-w-[70%]">
                <div class="w-8 h-8 bg-gradient-to-br from-gray-100 to-gray-200 rounded-full flex items-center justify-center text-lg mr-3 flex-shrink-0 shadow-sm">
                    🤖
                </div>
                <div>
                    <div class="bg-white rounded-3xl rounded-tl-md px-5 py-3 shadow-md border border-gray-200">
                        <p class="text-[15px] leading-relaxed text-gray-800">{message["content"]}</p>
                    </div>
                    {sources_html}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Add spacing at the bottom for the floating input
st.markdown('<div style="height: 120px;"></div>', unsafe_allow_html=True)

# Chat input
question = st.chat_input("💬 Tapez votre message ici...")

if question:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": question})
    
    # Call API
    try:
        tenant_info = TENANTS[st.session_state.selected_tenant]
        headers = {"X-API-KEY": tenant_info['api_key']}
        payload = {"question": question}
        
        with st.spinner(""):
            # Show typing indicator
            st.markdown("""
            <div class="flex justify-start mb-4 px-4">
                <div class="flex items-start">
                    <div class="w-8 h-8 bg-gradient-to-br from-gray-100 to-gray-200 rounded-full flex items-center justify-center text-lg mr-3 shadow-sm">
                        🤖
                    </div>
                    <div class="typing-indicator">
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            response = httpx.post(
                f"{API_URL}/query",
                headers=headers,
                json=payload,
                timeout=60
            )
        
        if response.status_code == 200:
            result = response.json()
            answer = result['answer']
            sources = result.get('sources', [])
            
            # Add to history
            st.session_state.messages.append({
                "role": "assistant", 
                "content": answer,
                "sources": sources
            })
            
        elif response.status_code == 401:
            error_msg = "❌ Erreur d'authentification - API key invalide"
            st.session_state.messages.append({"role": "assistant", "content": error_msg, "sources": []})
        else:
            error_msg = f"❌ Erreur du serveur: {response.status_code}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg, "sources": []})
            
    except httpx.ConnectError:
        error_msg = "❌ Impossible de se connecter au backend - Vérifiez que le serveur est démarré"
        st.session_state.messages.append({"role": "assistant", "content": error_msg, "sources": []})
    except Exception as e:
        error_msg = f"❌ Erreur: {str(e)}"
        st.session_state.messages.append({"role": "assistant", "content": error_msg, "sources": []})
    
    st.rerun()