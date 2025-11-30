import os, re, difflib
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(page_title="Code Mentor AI", page_icon="⚡", layout="wide")

# --- COMPACT CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    section[data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    .card { background: #21262d; border: 1px solid #30363d; border-radius: 8px; padding: 15px; margin-bottom: 10px; }
    .grad-text { background: linear-gradient(90deg, #4285F4, #9B72CB); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; }
    .stTextArea textarea { background: #0d1117; color: #e6edf3; border: 1px solid #30363d; font-family: 'Consolas', monospace; }
    .stButton>button { background: #238636; color: white; border: none; font-weight: 600; border-radius: 6px; width: 100%; transition: 0.2s; }
    .stButton>button:hover { background: #2ea043; transform: scale(1.02); }
    .status-dot { height: 8px; width: 8px; border-radius: 50%; display: inline-block; margin-right: 6px; }
    .on { background: #3fb950; box-shadow: 0 0 5px #3fb950; } .off { background: #f85149; }
</style>
""", unsafe_allow_html=True)

# --- HELPERS ---
def get_code(text): return (re.findall(r"```(?:\w+)?\n(.*?)```", text, re.DOTALL) or [None])[-1]
def get_diff(orig, mod): return "\n".join(difflib.unified_diff(orig.splitlines(), mod.splitlines(), fromfile='Original', tofile='Fixed', lineterm=''))

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## ⚡ <span class='grad-text'>Code Mentor</span>", unsafe_allow_html=True)
    
    # 1. STATUS
    key = os.getenv("GOOGLE_API_KEY")
    if key:
        st.markdown("""
        <div class="card">
            <span class="status-dot on"></span> <b style="color:#e6edf3">System Online</b>
            <div style="margin-top:5px; font-size:0.8rem; color:#8b949e;">Ready to refactor</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div class="card"><span class="status-dot off"></span> <b>System Offline</b></div>', unsafe_allow_html=True)
        key = st.text_input("API Key", type="password", placeholder="Paste Key Here", label_visibility="collapsed")

    # 2. CONFIGURATION (Native Container to fix empty box issue)
    with st.container(border=True):
        st.caption("Settings")
        model = st.selectbox("Model", ("gemini-2.5-pro", "gemini-1.5-pro", "gemini-1.5-flash"))
        lang = st.selectbox("Language", ("Python", "JavaScript", "Java", "C++", "Go", "SQL"))

# --- MAIN WORKSPACE ---
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 📥 <span style='color:#8b949e'>Source Code</span>", unsafe_allow_html=True)
    up = st.file_uploader("Upload", label_visibility="collapsed")
    val = up.read().decode("utf-8") if up else ""
    code = st.text_area("Input", value=val, height=550, placeholder="// Paste code here...", label_visibility="collapsed")
    run = st.button("🚀 Analyze Code")

with col2:
    st.markdown("### 📊 <span style='color:#8b949e'>Intelligence Hub</span>", unsafe_allow_html=True)
    if run:
        if not key or not code.strip():
            st.error("❌ Credentials or Code missing.")
        else:
            with st.spinner("🔮 Analyzing Logic..."):
                try:
                    genai.configure(api_key=key)
                    prompt = f"Role: Senior Dev. Lang: {lang}. Review code. Output Markdown: 1. Verdict 2. Fixes 3. Code Block.\nCode:\n{code}"
                    resp = genai.GenerativeModel(model).generate_content(prompt)
                    fixed = get_code(resp.text)
                    
                    t1, t2 = st.tabs(["📝 Analysis Report", "⚖️ Diff View"])
                    with t1: st.markdown(resp.text)
                    with t2: st.code(get_diff(code, fixed), "diff") if fixed else st.info("No changes.")
                except Exception as e: st.error(f"Error: {e}")
    else:
        # Empty State
        st.markdown("""
        <div class="card" style="text-align:center; color:#8b949e; padding:60px 20px; border-style: dashed;">
            Waiting for input...<br><br>
            ✨ <b>Detect Bugs</b> &nbsp; 🛡️ <b>Security Check</b> &nbsp; ⚡ <b>Performance</b>
        </div>
        """, unsafe_allow_html=True)