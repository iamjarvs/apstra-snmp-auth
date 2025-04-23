"""
Property sets management component for the Streamlit UI.
"""
import streamlit as st
import pandas as pd
import json
import re

# Import utility functions
from app.utils.helpers import (
    get_property_sets,
    create_property_set
)

def render_property_sets_page():
    """Render the manage property sets page."""
    st.title("Manage Property Sets")
    
    if not st.session_state.api_connected:
        st.error("Please connect to Apstra server first.")
        return
    
    # Fetch property sets
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Refresh Property Sets", key="refresh_property_sets"):
            with st.spinner("Fetching property sets..."):
                property_sets = get_property_sets(st.session_state.server, st.session_state.api_token)
                if property_sets:
                    st.session_state.property_sets = property_sets
                    st.success(f"Found {len(property_sets)} property sets.")
                else:
                    st.error("Failed to retrieve property sets.")
    
    with col1:
        st.header("Available Property Sets")
    
    # Display property sets if available
    if not st.session_state.property_sets:
        with st.spinner("Fetching property sets..."):
            property_sets = get_property_sets(st.session_state.server, st.session_state.api_token)
            if property_sets:
                st.session_state.property_sets = property_sets
                st.success(f"Found {len(property_sets)} property sets.")
            else:
                st.error("Failed to retrieve property sets.")
    
    if st.session_state.property_sets:
        display_property_sets_list()
        
        # Display selected property set details
        if st.session_state.selected_property_set:
            display_property_set_details()
        
        # Create new property set section
        create_new_property_set()

def display_property_sets_list():
    """Display the list of available property sets."""
    # Create a DataFrame for display
    property_sets_data = []
    for prop_set in st.session_state.property_sets:
        # Calculate size of values
        values_size = len(json.dumps(prop_set.get("values", {})))
        
        property_sets_data.append({
            "Name": prop_set.get("label", "Unknown"),
            "ID": prop_set.get("id", "Unknown"),
            "Created": prop_set.get("created_at", "Unknown"),
            "Last Updated": prop_set.get("updated_at", "Unknown"),
            "Size": f"{values_size} bytes"
        })
    
    # Display as DataFrame
    df = pd.DataFrame(property_sets_data)
    
    # Display the dataframe without Button column
    st.dataframe(df, hide_index=True)
    
    # Add separate selection mechanism
    selected_index = st.selectbox(
        "Select a property set to view:",
        options=range(len(property_sets_data)),
        format_func=lambda i: property_sets_data[i]["Name"],
        key="property_set_selector"
    )
    
    if st.button("View Selected Property Set"):
        if selected_index is not None:
            property_set_id = property_sets_data[selected_index]["ID"]
            selected_set = next(
                (ps for ps in st.session_state.property_sets if ps.get("id") == property_set_id),
                None
            )
            
            if selected_set:
                st.session_state.selected_property_set = selected_set
                # Force rerun to show the selected property set
                st.rerun()

def display_property_set_details():
    """Display details of the selected property set."""
    selected_set = st.session_state.selected_property_set
    
    st.header(f"Property Set: {selected_set.get('label', 'Unknown')}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**ID:** {selected_set.get('id', 'Unknown')}")
    with col2:
        st.markdown(f"**Created:** {selected_set.get('created_at', 'Unknown')}")
    with col3:
        st.markdown(f"**Last Updated:** {selected_set.get('updated_at', 'Unknown')}")
    
    # Display the values
    st.subheader("Values")
    
    # Add search functionality
    search_query = st.text_input("Search in Values", key="property_set_search")
    
    values = selected_set.get("values", {})
    
    # Filter values if search query provided
    if search_query:
        # Convert to string for searching
        values_str = json.dumps(values)
        if search_query.lower() in values_str.lower():
            # Highlight matches using regex
            pattern = re.compile(re.escape(search_query), re.IGNORECASE)
            highlighted_str = pattern.sub(f"**{search_query}**", values_str)
            # Convert back to JSON for display
            try:
                values_filtered = json.loads(values_str)
            except:
                values_filtered = values
        else:
            st.warning(f"No matches found for '{search_query}'")
            values_filtered = values
    else:
        values_filtered = values
    
    # Display the values as JSON
    st.json(values_filtered)
    
    # Create a download link
    json_str = json.dumps(values, indent=2)
    st.download_button(
        label="Download JSON File",
        data=json_str,
        file_name=f"{selected_set.get('label', 'property_set')}.json",
        mime="application/json",
        key="download_button"
        )

def create_new_property_set():
    """Provide UI for creating a new property set."""
    st.header("Create New Property Set")
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_property_set_name = st.text_input("Property Set Name", key="new_property_set_name")
    
    with col2:
        upload_method = st.radio(
            "Upload Method",
            options=["Upload JSON File", "Paste JSON Text"],
            key="upload_method"
        )
    
    if upload_method == "Upload JSON File":
        handle_file_upload(new_property_set_name)
    else:  # Paste JSON Text
        handle_text_paste(new_property_set_name)

def handle_file_upload(property_set_name):
    """Handle creating a property set from a file upload."""
    uploaded_file = st.file_uploader("Upload JSON File", type=["json"], key="json_file_upload")
    
    if uploaded_file:
        try:
            json_content = uploaded_file.read().decode("utf-8")
            property_set_values = json.loads(json_content)
            st.success("JSON file uploaded successfully!")
            
            # Preview
            with st.expander("Preview JSON"):
                st.json(property_set_values)
            
            if st.button("Create Property Set", key="create_from_file"):
                if not property_set_name:
                    st.error("Please enter a name for the property set.")
                else:
                    with st.spinner("Creating property set..."):
                        result = create_property_set(
                            st.session_state.server,
                            st.session_state.api_token,
                            property_set_name,
                            property_set_values
                        )
                        
                        if "error" in result:
                            st.error(f"Failed to create property set: {result['error']}")
                        else:
                            st.success(f"Successfully created property set '{property_set_name}'")
                            # Refresh property sets
                            property_sets = get_property_sets(st.session_state.server, st.session_state.api_token)
                            if property_sets:
                                st.session_state.property_sets = property_sets
        
        except json.JSONDecodeError:
            st.error("Invalid JSON file. Please check the file contents.")
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")

def handle_text_paste(property_set_name):
    """Handle creating a property set from pasted text."""
    json_text = st.text_area("Paste JSON Content", key="json_paste", height=200)
    
    if json_text:
        try:
            property_set_values = json.loads(json_text)
            
            # Preview
            with st.expander("Preview JSON"):
                st.json(property_set_values)
            
            if st.button("Create Property Set", key="create_from_paste"):
                if not property_set_name:
                    st.error("Please enter a name for the property set.")
                else:
                    with st.spinner("Creating property set..."):
                        result = create_property_set(
                            st.session_state.server,
                            st.session_state.api_token,
                            property_set_name,
                            property_set_values
                        )
                        
                        if "error" in result:
                            st.error(f"Failed to create property set: {result['error']}")
                        else:
                            st.success(f"Successfully created property set '{property_set_name}'")
                            # Refresh property sets
                            property_sets = get_property_sets(st.session_state.server, st.session_state.api_token)
                            if property_sets:
                                st.session_state.property_sets = property_sets
        
        except json.JSONDecodeError:
            st.error("Invalid JSON text. Please check the content.")
        except Exception as e:
            st.error(f"Error processing JSON: {str(e)}")