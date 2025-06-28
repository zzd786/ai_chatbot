"""
Streamlit Frontend for AI SQL Chatbot

Main interface for the text-to-SQL chatbot application.
Handles user queries, displays results, and manages UI state.
"""

import streamlit as st
import requests
import pandas as pd
import time
import random
import json

def check_backend_status():
    """Quick health check for the backend API"""
    try:
        resp = requests.get("http://localhost:8000/health", timeout=5)
        return resp.status_code == 200
    except requests.exceptions.RequestException:
        return False


# App configuration
st.set_page_config(
    page_title="AI SQL Chatbot",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styles
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .ai-analysis-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1px;
        margin: 1rem 0;
    }
    .ai-analysis-content {
        background: #ffffff;
        border-radius: 11px;
        padding: 1.5rem;
        color: #2d3748;
        line-height: 1.6;
        font-size: 0.95rem;
    }
    .ai-analysis-header {
        color: #4a5568;
        font-weight: 600;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .ai-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Session state setup
session_vars = {
    "language": "en",
    "last_question": "",
    "last_sql": "",
    "last_result": pd.DataFrame(),
    "last_answer": "",
    "schema": None,
    "error": "",
    "query_count": 0,
    "total_rows_fetched": 0,
    "backend_status": None,
    "query_in_progress": False,
    "schema_fetch_in_progress": False,
}

for var, default_val in session_vars.items():
    if var not in st.session_state:
        st.session_state[var] = default_val

# Helper function for in progress checking
def is_processing():
    return st.session_state.query_in_progress or st.session_state.schema_fetch_in_progress

# Random loading messages for better UX
loading_messages = [
    "Processing your query...",
    "Translating natural language to SQL...",
    "Executing database query...",
    "Analyzing query results...",
    "Generating AI analysis...",
    "Fetching data from database...",
    "Preparing results..."
]

# Main header
st.markdown('<h1 class="main-header">🤖 AI SQL Chatbot</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Transform natural language into SQL queries with AI-powered database analysis</p>', unsafe_allow_html=True)

# Top metrics row
col_metric1, col_metric2, col_metric3 = st.columns(3)

with col_metric1:
    st.metric("🚀 Queries Run", st.session_state.query_count, delta=1 if st.session_state.query_count > 0 else 0)

with col_metric2:
    st.metric("📊 Rows Fetched", st.session_state.total_rows_fetched)

with col_metric3:
    # Checking backend health on first load
    if st.session_state.backend_status is None:
        st.session_state.backend_status = check_backend_status()
    
    ai_status = "🟢 Ready" if st.session_state.backend_status else "🔴 Offline"
    col_status, col_refresh = st.columns([3, 1])
    with col_status:
        st.metric("🧠 AI Status", ai_status)
    with col_refresh:
        if st.button("🔄", help="Refresh AI status", key="refresh_ai_status", type="secondary", disabled=is_processing()):
            st.session_state.backend_status = check_backend_status()
            st.rerun()

# Sidebar controls
with st.sidebar:
    st.markdown("### ⚙️ Control Center")
    
    # Language picker
    languages = {"English": "en", "Deutsch": "de", "Français": "fr", "Español": "es", "العربية": "ar", "اردو": "ur"}
    selected_language = st.selectbox(
        "🌍 Choose your language:",
        options=list(languages.keys()),
        index=list(languages.values()).index(st.session_state.language),
        disabled=is_processing()
    )
    st.session_state.language = languages[selected_language]
    
    # SQL display toggle
    show_sql = st.toggle("🔍 Show generated SQL", key="sql_toggle", disabled=is_processing())
    
    # Sample queries
    st.markdown("### 💡 Sample Queries")
    sample_queries = [
        "Show me all customers from Germany",
        "Which products are out of stock?",
        "Top 5 customers by total orders",
        "Best selling products",
        "Orders from 1997",
        "How many employees do we have?",
        "All seafood products",
        "Sales by category"
    ]
    
    for query in sample_queries[:8]:
        if st.button(query, key=f"sample_{query}", use_container_width=True, disabled=st.session_state.query_in_progress):
            st.session_state.last_question = query
            st.rerun()
    
    # Divider before schema section
    st.markdown("---")
    
    # Database schema explorer
    schema_button_text = "Fetching Schema..." if st.session_state.schema_fetch_in_progress else "📋 Fetch Database Schema"
    if st.button(schema_button_text, help="Load database schema information", type="secondary", disabled=is_processing()):
        st.session_state.schema_fetch_in_progress = True
        st.rerun()
    
    # Handle schema fetching
    if st.session_state.schema_fetch_in_progress:
        with st.spinner(random.choice(loading_messages)):
            try:
                resp = requests.get("http://localhost:8000/schema")
                resp.raise_for_status()
                st.session_state.schema = resp.json()
                st.success("Schema loaded successfully!")
            except Exception as e:
                st.error(f"Schema fetch error: {e}")
            finally:
                st.session_state.schema_fetch_in_progress = False
                st.rerun()
    
    # Show schema if loaded
    if st.session_state.schema:
        with st.expander("📊 Database Schema", expanded=False):
            for table, columns in st.session_state.schema.items():
                st.markdown(f"**🏢 {table}**")
                for col in columns[:3]:  # Show first 3 columns
                    st.write(f"• {col['column']} ({col['data_type']})")
                if len(columns) > 3:
                    st.write(f"... and {len(columns) - 3} more")
                st.divider()

# Main query interface
if st.session_state.query_in_progress:
    st.info("🔄 Processing your query... Please wait.")
elif st.session_state.schema_fetch_in_progress:
    st.info("🔄 Fetching database schema... Please wait.")

st.markdown("### 💬 Ask Your Question")

# Query input box
user_query = st.text_area(
    "What would you like to know about the data?",
    value=st.session_state.last_question,
    height=120,
    placeholder="Example: 'Show me customers from France' or 'What are our top products?'",
    disabled=st.session_state.query_in_progress
)

# Action buttons
col_btn1, col_btn2 = st.columns([3, 1])

with col_btn1:
    button_text = "Processing Query..." if st.session_state.query_in_progress else "Execute Query"
    if st.button(button_text, type="primary", use_container_width=True, disabled=is_processing()):
        if not user_query.strip():
            st.warning("Please enter a question first.")
        else:
            st.session_state.error = ""
            st.session_state.last_question = user_query
            st.session_state.query_count += 1
            st.session_state.query_in_progress = True
            st.rerun()
    
    # Handle query execution
    if st.session_state.query_in_progress:
        with st.spinner(random.choice(loading_messages)):
            time.sleep(0.5)
            try:
                payload = {"query": st.session_state.last_question, "language": st.session_state.language}
                resp = requests.post("http://localhost:8000/query", json=payload, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                
                st.session_state.last_sql = data.get("sql", "")
                result_rows = data.get("db_result", [])
                
                if result_rows:
                    st.session_state.last_result = pd.DataFrame(result_rows)
                    st.session_state.total_rows_fetched += len(result_rows)
                else:
                    st.session_state.last_result = pd.DataFrame()
                
                st.session_state.error = data.get("error", "")
                st.session_state.last_answer = data.get("answer", "")
                
                if not st.session_state.error:
                    st.success("✅ Query executed successfully!")
                
            except requests.exceptions.Timeout:
                st.session_state.error = "Request timed out. Please try again."
            except requests.exceptions.ConnectionError:
                st.session_state.error = "Cannot connect to the backend. Please ensure the server is running."
            except Exception as e:
                st.session_state.error = f"API error: {str(e)}"
            finally:
                st.session_state.query_in_progress = False
                st.rerun()

with col_btn2:
    if st.button("Clear", use_container_width=True, disabled=is_processing()):
        st.session_state.last_question = ""
        st.session_state.last_sql = ""
        st.session_state.last_result = pd.DataFrame()
        st.session_state.last_answer = ""
        st.session_state.error = ""
        st.rerun()

# Error handling
if st.session_state.error:
    st.error(f"Error: {st.session_state.error}")

# SQL query display
if show_sql and st.session_state.last_sql:
    st.markdown("### 🔍 Generated SQL Query")
    st.code(st.session_state.last_sql, language="sql")

# Results table
if not st.session_state.last_result.empty:
    st.markdown("### 📊 Query Results")
    
    # Quick stats
    num_rows, num_cols = st.session_state.last_result.shape
    st.info(f"Results: **{num_rows}** rows and **{num_cols}** columns")
    
    # Data table
    st.dataframe(
        st.session_state.last_result,
        use_container_width=True,
        hide_index=True
    )
    
    # CSV download
    csv = st.session_state.last_result.to_csv(index=False)
    st.download_button(
        label="Download as CSV",
        data=csv,
        file_name=f"northwind_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True,
        disabled=is_processing()
    )

# AI response section
if st.session_state.last_answer:
    st.markdown("""
    <div class="ai-analysis-header">
        <span>🤖</span>
        <span>AI Analysis</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Extract summary from JSON response
    try:
        if st.session_state.last_answer.startswith("{"):
            answer_data = json.loads(st.session_state.last_answer)
            display_text = answer_data.get("summary", "No summary available")
        else:
            display_text = st.session_state.last_answer
    except json.JSONDecodeError:
        display_text = st.session_state.last_answer
    
    st.markdown(f"""
    <div class="ai-analysis-container">
        <div class="ai-analysis-content">
            {display_text}
        </div>
    </div>
    """, unsafe_allow_html=True)

# App info footer
st.markdown("---")
col_footer1, col_footer2, col_footer3 = st.columns(3)

with col_footer1:
    st.markdown("""
    **🔧 Built with:**
    - 🚀 Streamlit
    - ⚡ FastAPI  
    - 🧠 OpenAI GPT-4.1
    - 🐘 PostgreSQL
    """)

with col_footer2:
    st.markdown("""
    **🛡️ Security:**
    - 🔒 Read-only queries
    - 🚫 No data modification
    - ✅ SQL validation
    """)

with col_footer3:
    st.markdown("""
    **📊 Database:**
    - 🏢 Northwind Trading Co.
    - 📅 1996-1998 data
    - 🌍 Global customers
    """)