"""
Sidebar component for the Streamlit UI.
"""
import streamlit as st
import os

# Import utility functions
from app.utils.helpers import authenticate_user, get_all_blueprints

def render_sidebar():
    """Render the sidebar with connection settings and navigation."""
    with st.sidebar:
        st.title("Apstra SNMP Auth")
        
        # Connection settings
        st.markdown("<div class='sidebar-header'>Connection Settings</div>", unsafe_allow_html=True)
        server = st.text_input("Apstra Server", value=st.session_state.server, key="server_input") or "10.28.143.3"
        username = st.text_input("Username", value=st.session_state.username, key="username_input") or "admin"
        password = st.text_input("Password", type="password", key="password_input") or "C1sco123!"
        
        # Connection status
        if st.session_state.api_connected:
            st.markdown("<div><span class='status-indicator status-connected'></span><span class='success'>Connected</span></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div><span class='status-indicator status-disconnected'></span><span class='error'>Disconnected</span></div>", unsafe_allow_html=True)
        
        # Connect button
        if st.button("Connect to Apstra"):
            if not server or not username or not password:
                st.error("Please enter server, username, and password.")
            else:
                with st.spinner("Connecting to Apstra..."):
                    # Store the server and username
                    st.session_state.server = server
                    st.session_state.username = username
                    
                    # Authenticate
                    token = authenticate_user(server, username, password)
                    
                    if token:
                        st.session_state.api_token = token
                        st.session_state.api_connected = True
                        st.success("Connected successfully!")
                        
                        # Fetch blueprints
                        with st.spinner("Fetching blueprints..."):
                            blueprints = get_all_blueprints(server, token)
                            if blueprints:
                                st.session_state.blueprints = blueprints
                            else:
                                st.warning("No blueprints found or error retrieving blueprints.")
                    else:
                        st.error("Authentication failed. Please check your credentials.")
                        st.session_state.api_connected = False
                        st.session_state.api_token = None
        
        st.divider()
        
        # Navigation menu
        st.markdown("<div class='sidebar-header'>Navigation</div>", unsafe_allow_html=True)
        pages = ["Home", "Retrieve Authentication Keys", "Manage Property Sets", "About"]
        
        for page in pages:
            if st.button(page, key=f"nav_{page}", help=f"Navigate to {page} page", 
                         use_container_width=True, 
                         type="primary" if st.session_state.current_page == page else "secondary"):
                st.session_state.current_page = page
                # Reset page-specific state when switching
                if page == "Retrieve Authentication Keys":
                    st.session_state.selected_blueprint = None
                    st.session_state.systems = []
                elif page == "Manage Property Sets":
                    st.session_state.selected_property_set = None
                st.rerun()