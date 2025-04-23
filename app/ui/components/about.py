"""
About page component for the Streamlit UI.
"""
import streamlit as st

def render_about_page():
    """Render the about page."""
    st.title("About Apstra SNMP Authentication Manager")
    
    st.markdown("""
    ## Overview
    
    The Apstra SNMP Authentication Manager is a tool designed to help network administrators retrieve and manage
    SNMP authentication and privacy keys from devices managed by Apstra. It provides a user-friendly interface 
    for interacting with the Apstra API and automating the key extraction process.
    
    ## Features
    
    - **Authentication Key Retrieval**: Execute commands on network devices to extract SNMP authentication
      and privacy keys automatically.
    
    - **Property Set Management**: Store and manage SNMP authentication details in Apstra property sets
      for easy reference and automation.
    
    - **Bulk Processing**: Process multiple systems at once, with clear status and error reporting.
    
    - **Export Options**: Save results to JSON files or copy to clipboard for use in other tools.
    
    ## Technical Details
    
    - Built with Python and Streamlit
    - Communicates with Apstra API for device management
    - Extracts SNMP authentication keys from device configurations
    - Supports Junos-format encrypted keys
    
    ## Usage Guidelines
    
    1. **Connect** to your Apstra server using the sidebar.
    2. **Select a blueprint** containing the devices you want to work with.
    3. **Execute commands** to retrieve SNMP authentication information.
    4. **Save or upload** the results as needed.
    
    ## Version Information
    
    - **Version**: 1.0.0
    - **Updated**: April 2025
    """)
    
    # Contact information
    st.header("Contact & Support")
    st.markdown("""
    For issues, feature requests, or contributions:
    
    - **GitHub Repository**: [https://github.com/iamjarvs/apstra-snmp-auth]
    - **Author**: Adam Jarvis
    """)
    
    # Disclaimer
    st.header("Disclaimer")
    st.markdown("""
    This tool is provided as-is without any warranties. Please use responsibly and ensure
    you have appropriate access rights to the systems you are managing.
    """)