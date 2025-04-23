"""
Settings page component for the Streamlit UI.
"""
import streamlit as st
import os

def render_settings_page():
    """Render the settings page."""
    st.title("Settings")
    
    st.markdown("""
    Configure application settings to customize behavior.
    These settings will be saved for your current session.
    """)
    
    # Create form for settings
    with st.form("settings_form"):
        st.header("General Settings")
        
        # Logging settings
        verbose_logging = st.checkbox(
            "Enable Verbose Logging", 
            value=st.session_state.settings["verbose_logging"],
            help="Display detailed log messages during operations"
        )
        
        # File settings
        default_output_file = st.text_input(
            "Default Output File", 
            value=st.session_state.settings["default_output_file"],
            help="Default filename for saving results"
        )
        
        # Property set settings
        default_property_set_name = st.text_input(
            "Default Property Set Name", 
            value=st.session_state.settings["default_property_set_name"],
            help="Default name for property sets"
        )
        
        # SNMP settings
        st.header("SNMP Settings")
        col1, col2 = st.columns(2)
        
        with col1:
            salt = st.text_input(
                "Salt Character", 
                value=st.session_state.settings["salt"],
                help="Salt character for Junos encryption",
                max_chars=1
            )
        
        with col2:
            rand = st.text_input(
                "Random Character", 
                value=st.session_state.settings["rand"],
                help="Random character for Junos encryption",
                max_chars=1
            )
        
        # Credential settings
        st.header("Credential Settings")
        save_credentials = st.checkbox(
            "Save Credentials for Session", 
            value=st.session_state.settings["save_credentials"],
            help="Store credentials in environment variables for the current session"
        )
        
        # Submit button
        submitted = st.form_submit_button("Save Settings")
        
        if submitted:
            # Update settings in session state
            st.session_state.settings["verbose_logging"] = verbose_logging
            st.session_state.settings["default_output_file"] = default_output_file
            st.session_state.settings["default_property_set_name"] = default_property_set_name
            st.session_state.settings["salt"] = salt
            st.session_state.settings["rand"] = rand
            st.session_state.settings["save_credentials"] = save_credentials
            
            # Apply settings
            if save_credentials:
                os.environ["APSTRA_SERVER"] = st.session_state.server
                os.environ["APSTRA_USERNAME"] = st.session_state.username
                # We don't save the password in env vars for security
            
            st.success("Settings saved successfully!")
    
    # Reset button
    if st.button("Reset to Defaults"):
        st.session_state.settings = {
            'verbose_logging': False,
            'default_output_file': 'results.json',
            'default_property_set_name': 'snmp_auth',
            'salt': 'j',
            'rand': 'a',
            'save_credentials': False
        }
        st.success("Settings reset to defaults.")
        st.experimental_rerun()