"""
Main Streamlit application for Apstra SNMP Authentication Manager.
This file serves as the entry point for the Streamlit UI.
"""
import streamlit as st
import sys
import os
from pathlib import Path

sys.path.append(os.getcwd())  # Add the current directory to the Python path

# Add the parent directory to the path for imports
parent_dir = Path(__file__).resolve().parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Import UI components
from app.ui.components.sidebar import render_sidebar
from app.ui.components.home import render_home_page
from app.ui.components.auth_keys import render_retrieve_keys_page
from app.ui.components.property_sets import render_property_sets_page
from app.ui.components.settings import render_settings_page
from app.ui.components.about import render_about_page
from app.ui.utils.session_state import initialize_session_state, set_page_config

def main():
    """Main entry point for the Streamlit application."""
    # Set up page configuration
    set_page_config()
    
    # Initialize session state
    initialize_session_state()
    
    # Render the sidebar
    render_sidebar()
    
    # Render the appropriate page based on current selection
    if st.session_state.current_page == "Home":
        render_home_page()
    elif st.session_state.current_page == "Retrieve Authentication Keys":
        render_retrieve_keys_page()
    elif st.session_state.current_page == "Manage Property Sets":
        render_property_sets_page()
    # elif st.session_state.current_page == "Settings":
    #     render_settings_page()
    elif st.session_state.current_page == "About":
        render_about_page()
    else:
        # Default to home page if unknown
        render_home_page()

if __name__ == "__main__":
    main()