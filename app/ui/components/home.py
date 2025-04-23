"""
Home page component for the Streamlit UI.
"""
import streamlit as st

def render_home_page():
    """Render the home page."""
    st.title("Apstra SNMP Authentication Manager")
    
    st.markdown("""
    Welcome to the Apstra SNMP Authentication Manager! This tool helps you retrieve and manage SNMP authentication keys
    from devices in your Apstra-managed network.
    
    ### Key Features:
    - Retrieve SNMP authentication and privacy keys from network devices
    - Save keys to Apstra property sets for easy reference
    - Manage and update property sets
    - Export data in JSON format
    """)
    
    # Quick start section
    st.header("Quick Start")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("1. Connect")
        st.markdown("Enter your Apstra server details and credentials in the sidebar, then click 'Connect to Apstra'.")
    with col2:
        st.subheader("2. Retrieve Keys")
        st.markdown("Select a blueprint and retrieve SNMP authentication keys from your devices.")
    with col3:
        st.subheader("3. Manage")
        st.markdown("Save keys to property sets or export them to JSON files for use in automation.")
    
    # Status dashboard
    st.header("Status Dashboard")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Connection Status")
        if st.session_state.api_connected:
            st.success("Connected to Apstra server")
            st.markdown(f"**Server:** {st.session_state.server}")
            st.markdown(f"**Username:** {st.session_state.username}")
        else:
            st.error("Not connected to Apstra server")
            st.markdown("Please connect using the settings in the sidebar.")
    
    with col2:
        st.subheader("Available Resources")
        if st.session_state.api_connected:
            st.markdown(f"**Blueprints:** {len(st.session_state.blueprints)}")
            if st.session_state.selected_blueprint:
                st.markdown(f"**Selected Blueprint:** {st.session_state.selected_blueprint.get('label', 'Unknown')}")
                st.markdown(f"**Systems:** {len(st.session_state.systems)}")
        else:
            st.markdown("Connect to Apstra to view available resources.")