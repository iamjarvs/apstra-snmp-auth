"""
Session state management for the Streamlit UI.
"""
import streamlit as st

def set_page_config():
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title="Apstra SNMP Authentication Manager",
        page_icon="🔐",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Apply custom CSS for better styling
    st.markdown("""
        <style>
        .main .block-container {padding-top: 2rem;}
        .stButton button {width: 100%;}
        .success {color: #28a745;}
        .warning {color: #ffc107;}
        .error {color: #dc3545;}
        .info {color: #17a2b8;}
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
        }
        .status-connected {background-color: #28a745;}
        .status-disconnected {background-color: #dc3545;}
        .hide-dataframe-index table {border-collapse: collapse;}
        .hide-dataframe-index thead tr th:first-child {display: none;}
        .hide-dataframe-index tbody tr th {display: none;}
        .masked-text {filter: blur(5px); transition: all 0.3s ease;}
        .masked-text:hover {filter: blur(0px);}
        .sidebar-header {font-size: 1.2rem; font-weight: bold; margin-bottom: 1rem;}
        </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    # Connection state
    if 'api_connected' not in st.session_state:
        st.session_state.api_connected = False
    if 'api_token' not in st.session_state:
        st.session_state.api_token = None
    if 'server' not in st.session_state:
        st.session_state.server = ""
    if 'username' not in st.session_state:
        st.session_state.username = ""
    
    # Navigation state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Home"
    
    # Data state
    if 'blueprints' not in st.session_state:
        st.session_state.blueprints = []
    if 'selected_blueprint' not in st.session_state:
        st.session_state.selected_blueprint = None
    if 'systems' not in st.session_state:
        st.session_state.systems = []
    if 'command_results' not in st.session_state:
        st.session_state.command_results = []
    if 'failed_systems' not in st.session_state:
        st.session_state.failed_systems = []
    if 'property_sets' not in st.session_state:
        st.session_state.property_sets = []
    if 'selected_property_set' not in st.session_state:
        st.session_state.selected_property_set = None
    
    # Settings
    if 'settings' not in st.session_state:
        st.session_state.settings = {
            'verbose_logging': False,
            'default_output_file': 'results.json',
            'default_property_set_name': 'snmp_auth',
            'salt': 'j',
            'rand': 'a',
            'save_credentials': False
        }