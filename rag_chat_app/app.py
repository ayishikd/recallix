import streamlit as st
import time
import json
from database import init_db, register_user, login_user, create_session, add_message, get_chat_history
from memory_client import MemoryOSClient
from llm_client import OllamaClient

# Page Config
st.set_page_config(page_title="Memoize RAG Chat", page_icon="🧠", layout="wide")

# Initialize DB
init_db()

# Custom CSS for Premium Look
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stButton>button {
        border-radius: 12px;
        font-weight: bold;
    }
    .chat-bubble {
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 10px;
    }
    .user-bubble {
        background-color: #1e1e1e;
        border: 1px solid #333;
    }
    .bot-bubble {
        background-color: #004d4d;
        border: 1px solid #00cccc;
    }
    .memory-log {
        font-size: 0.8em;
        color: #00cccc;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

# Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None
if "api_key" not in st.session_state:
    st.session_state.api_key = None
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "memory_client" not in st.session_state:
    st.session_state.memory_client = None
if "llm_client" not in st.session_state:
    st.session_state.llm_client = OllamaClient()

# Sidebar: Auth and Agent Control
with st.sidebar:
    st.title("🧠 Memoize RAG")
    
    if not st.session_state.logged_in:
        tabs = st.tabs(["Login", "Register"])
        with tabs[0]:
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login"):
                user = login_user(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user[0]
                    st.session_state.username = user[1]
                    st.session_state.api_key = user[2]
                    st.session_state.memory_client = MemoryOSClient(user[2])
                    st.session_state.session_id = create_session(user[0])
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        with tabs[1]:
            new_user = st.text_input("New Username")
            new_pass = st.text_input("New Password", type="password")
            if st.button("Register"):
                if register_user(new_user, new_pass):
                    st.success("User registered! Please log in.")
                else:
                    st.error("Username already exists")
    else:
        st.success(f"Logged in as {st.session_state.username}")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()
        
        st.divider()
        st.subheader("Settings")
        model_choice = st.selectbox("Select Model", ["mistral", "llama3.1:8b"])
        
        # Agent Management
        agents_data = st.session_state.memory_client.list_agents()
        agents = [a['agent_id'] for a in agents_data.get('data', [])] if 'data' in agents_data else ['default_agent']
        selected_agent = st.selectbox("Switch Agent", agents)
        
        if st.button("New Session"):
            st.session_state.session_id = create_session(st.session_state.user_id, selected_agent)
            st.rerun()

# Main Chat Interface
if st.session_state.logged_in:
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header(f"Chat with {model_choice.capitalize()}")
        
        # Display Chat History
        history = get_chat_history(st.session_state.session_id)
        for role, content, ts, status in history:
            with st.container():
                bubble_class = "user-bubble" if role == "user" else "bot-bubble"
                st.markdown(f'<div class="chat-bubble {bubble_class}"><b>{role.upper()}:</b> {content}</div>', unsafe_allow_html=True)
                if status:
                    st.markdown(f'<div class="memory-log">MemoryOS: {status}</div>', unsafe_allow_html=True)

        # Input Area
        prompt = st.chat_input("Say something to remember...")
        if prompt:
            # 1. User Message
            add_message(st.session_state.session_id, "user", prompt)
            
            # 2. RAG: Recall from MemoryOS
            recall_results = st.session_state.memory_client.agent_recall(prompt, selected_agent)
            memories = recall_results.get("data", {}).get("memories", [])
            
            # 3. LLM: Generate Response
            system_prompt = f"You are a helpful assistant talking with user {st.session_state.user_id} via agent {selected_agent}. Use the provided memories to personalize your response."
            response = st.session_state.llm_client.generate(model_choice, system_prompt, prompt, memories)
            
            # 4. MemoryOS: Store Interaction
            store_result = st.session_state.memory_client.agent_store(
                f"User said: {prompt} | Assistant replied: {response}", 
                selected_agent
            )
            
            status_summary = f"Stored with importance {store_result.get('data', {}).get('importance', 'N/A')}"
            
            # 5. Save and Rerun
            add_message(st.session_state.session_id, "assistant", response, status_summary)
            st.rerun()

    with col2:
        st.header("Memory Insights")
        tabs = st.tabs(["Pipeline", "Timeline", "World State", "Profile"])
        
        with tabs[0]:
            st.subheader("Stage Visualizer")
            stats = st.session_state.memory_client.get_stats()
            st.json(stats.get("data", {}))
            
            st.subheader("Latest Store Details")
            # Logic to show the last 12-stage pipe logs
            # This would ideally come from the most recent store response
            pass

        with tabs[1]:
            st.subheader("Event Timeline")
            timeline = st.session_state.memory_client.get_timeline()
            events = timeline.get("data", [])
            for e in events[-10:]: # Show last 10
                st.text(f"[{e.get('timestamp', '...')}] {e.get('content')[:100]}...")

        with tabs[2]:
            st.subheader("Inferred User State")
            states = st.session_state.memory_client.get_world_state()
            st.json(states.get("data", {}))

        with tabs[3]:
            st.subheader("Cognitive Profile")
            profile = st.session_state.memory_client.get_profile()
            st.json(profile.get("data", {}))
else:
    st.info("Please login or register to start chatting.")
    # Show Visual Power of Memoize even when logged out as teaser
    st.image("https://images.unsplash.com/photo-1544027993-37dbfe43562a?q=80&w=2070&auto=format&fit=crop", caption="Memoize Cognitive Architecture")
