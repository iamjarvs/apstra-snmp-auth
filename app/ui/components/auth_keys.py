"""
Authentication keys retrieval component for the Streamlit UI.
"""
import streamlit as st
import pandas as pd
import json
import time

# Import utility functions - ensure these paths are correct
try:
    from app.utils.helpers import (
        get_system_ids,
        execute_command_on_system,
        extract_snmp_auth_keys,
        format_results_to_json,
        get_property_sets,
        find_property_set_by_label,
        update_property_set,
        create_property_set
    )
# Use Mock functions if actual helpers are not found (for standalone testing)
except ImportError:
    st.warning("Could not import helper functions from 'app.utils.helpers'. Using mock functions.")
    # --- Mock functions (replace with your actual imports if structure differs) ---
    def get_system_ids(server, token, blueprint_id):
        print(f"Mock: Getting systems for blueprint {blueprint_id}")
        time.sleep(1)
        return [{"hostname": "spine1", "system_id": "sys1", "role": "spine"}, {"hostname": "leaf1", "system_id": "sys2", "role": "leaf"}]

    def execute_command_on_system(server, token, system_id, command):
        print(f"Mock: Executing '{command}' on {system_id}")
        time.sleep(0.5)
        if system_id == "sys1":
             # Simulate successful result with keys
             return json.dumps({
                 "configuration": {
                     "snmp": {
                         "v3": {
                             "usm": {
                                 "local": {
                                     "user": {
                                         "admin": {
                                             "authentication-sha": {"key": "mock_auth_key_123"},
                                             "privacy-aes128": {"key": "mock_priv_key_456"}
                                         }
                                     }
                                 }
                             }
                         }
                     }
                 }
             })
        elif system_id == "sys2":
            # Simulate result needing extraction but maybe missing a key
            return json.dumps({"configuration": {"snmp": {}}}) # Missing keys structure
        else:
            # Simulate command failure
            return None

    def extract_snmp_auth_keys(result_json):
        print(f"Mock: Extracting keys from {result_json}")
        try:
            user_data = result_json['configuration']['snmp']['v3']['usm']['local']['user']
            # Find first user (simplistic mock)
            user = list(user_data.values())[0]
            auth_key = user.get('authentication-sha', {}).get('key')
            priv_key = user.get('privacy-aes128', {}).get('key')
            if not auth_key or not priv_key:
                 return {"error": "Authentication or privacy key not found in mock data"}
            return {"authentication_key": auth_key, "privacy_key": priv_key}
        except (KeyError, IndexError, TypeError) as e:
            return {"error": f"Mock extraction failed: {e}"}

    def format_results_to_json(results):
        print("Mock: Formatting results for Property Set JSON")
        # Simulate specific format needed by property set API
        formatted = {}
        for r in results:
             formatted[r['hostname']] = r['snmp-auth']
        # Example wrapper - adjust if needed
        return json.dumps({"device_snmp_keys": formatted}, indent=2)


    def get_property_sets(server, token):
        print(f"Mock: Getting property sets from {server}")
        # Simulate existing sets
        return [{"id": "set1", "label": "Existing Set A"}, {"id": "set2", "label": "DefaultSet"}]

    def find_property_set_by_label(sets, label):
        print(f"Mock: Searching for label '{label}'")
        for s in sets:
            if s["label"] == label:
                return s
        return None

    def update_property_set(server, token, set_id, name, payload):
        print(f"Mock: Updating property set {set_id} on {server} with name '{name}'")
        # Simulate success or failure
        if "fail" in name.lower():
             return {"error": "Simulated update failure"}
        return {"status": "success", "id": set_id, "label": name}

    def create_property_set(server, token, name, payload):
        print(f"Mock: Creating property set on {server} with name '{name}'")
        if "fail" in name.lower():
             return {"error": "Simulated creation failure"}
        import uuid
        return {"id": str(uuid.uuid4()), "label": name}
    # --- End Mock functions ---

# --- Initialize Session State ---
# These should ideally be initialized in your main app script,
# but we add checks here for robustness if this file is run standalone or imported.

# Connection state (assuming set in main app)
if 'api_connected' not in st.session_state:
    st.session_state.api_connected = False # Default if not set elsewhere

# Apstra connection details (assuming set in main app)
if 'server' not in st.session_state:
    st.session_state.server = ""
if 'api_token' not in st.session_state:
    st.session_state.api_token = ""

# Blueprint and system data
if 'blueprints' not in st.session_state:
    st.session_state.blueprints = [] # Expects list of dicts {'label': '...', 'id': '...'}
if 'selected_blueprint' not in st.session_state:
    st.session_state.selected_blueprint = None
if 'systems' not in st.session_state:
    st.session_state.systems = [] # Expects list of dicts from get_system_ids

# Results storage
if 'command_results' not in st.session_state:
    st.session_state.command_results = []
if 'failed_systems' not in st.session_state:
    st.session_state.failed_systems = []

# Settings (provide defaults)
if 'settings' not in st.session_state:
    st.session_state.settings = {
        'default_output_file': 'snmp_keys_output.json',
        'default_property_set_name': 'snmp_auth'
    }
else: # Ensure default keys exist even if settings dict exists
    if 'default_output_file' not in st.session_state.settings:
        st.session_state.settings['default_output_file'] = 'snmp_keys_output.json'
    if 'default_property_set_name' not in st.session_state.settings:
        st.session_state.settings['default_property_set_name'] = 'snmp_auth'


# State for the property set upload UI
if 'show_upload_options' not in st.session_state:
    st.session_state.show_upload_options = False
if 'property_set_name_input_value' not in st.session_state:
    # Use default from settings if available, otherwise empty string
    st.session_state.property_set_name_input_value = st.session_state.settings.get('default_property_set_name', '')

# --- Main Page Rendering Function ---

def render_retrieve_keys_page():
    """Render the retrieve authentication keys page."""
    st.title("Retrieve Authentication Keys")

    if not st.session_state.get('api_connected', False): # Check state safely
        st.error("Please connect to Apstra server first (API connection state not found or False).")
        return

    # Check if blueprints list exists and is a list
    if not isinstance(st.session_state.get('blueprints'), list):
         st.error("Blueprint data is missing or not in the expected format.")
         # Optionally try to fetch blueprints here if appropriate
         return

    # Display blueprints for selection
    st.header("1. Blueprint Selection")

    # Prepare options safely, handling potential missing 'label'
    blueprint_options = ["-- Select a Blueprint --"] + \
                        [bp.get('label', f"ID: {bp.get('id', 'Unknown')}") for bp in st.session_state.blueprints]

    # Use a key that reflects the purpose
    blueprint_index = st.selectbox(
        "Select a blueprint:",
        options=range(len(blueprint_options)),
        format_func=lambda i: blueprint_options[i],
        key="retrieve_keys_blueprint_selector",
        # Reset dependent state if selection changes
        on_change=lambda: st.session_state.update({
            'systems': [],
            'command_results': [],
            'failed_systems': [],
            'selected_blueprint': None,
            'show_upload_options': False # Hide upload options if BP changes
            })
    )

    # Proceed only if a valid blueprint is selected
    if blueprint_index > 0:
        # Store selected blueprint ID/label safely
        selected_bp_data = st.session_state.blueprints[blueprint_index - 1]
        st.session_state.selected_blueprint = {
            'id': selected_bp_data.get('id'),
            'label': selected_bp_data.get('label', 'Unknown')
        }
        blueprint_id = st.session_state.selected_blueprint.get('id')
        blueprint_label = st.session_state.selected_blueprint.get('label')

        if not blueprint_id:
            st.error("Selected blueprint is missing an ID.")
            return

        st.info(f"Selected Blueprint: **{blueprint_label}** (ID: {blueprint_id})")

        # --- System Loading ---
        st.header("2. Load and Select Systems")
        if st.button(f"Load Systems from '{blueprint_label}'", key="load_systems_button"):
            # Reset results when loading new systems
            st.session_state.command_results = []
            st.session_state.failed_systems = []
            st.session_state.show_upload_options = False

            with st.spinner(f"Loading systems..."):
                try:
                    systems = get_system_ids(st.session_state.server, st.session_state.api_token, blueprint_id)
                    if systems is not None: # Check for None in case of API error
                        st.session_state.systems = systems
                        st.success(f"Loaded {len(systems)} systems.")
                        if not systems:
                            st.warning("No systems found in this blueprint.")
                    else:
                        st.error("Failed to retrieve systems (API returned None or error).")
                        st.session_state.systems = [] # Ensure it's an empty list on failure
                except Exception as e:
                    st.error(f"Error loading systems: {e}")
                    st.session_state.systems = []

        # --- System Selection and Command Execution ---
        # Proceed only if systems have been loaded successfully
        if st.session_state.get('systems'): # Check if list is not empty
            st.subheader("Select Systems")

            # Create DataFrame for selection
            try:
                systems_data = [{
                    "Hostname": system.get('hostname', 'Unknown'),
                    "System ID": system.get('system_id', 'Unknown'),
                    "Role": system.get('role', 'Unknown'),
                    "Selected": True # Default to selected
                } for system in st.session_state.systems]

                df = pd.DataFrame(systems_data)

                # Use st.data_editor for selection
                edited_df = st.data_editor(
                    df,
                    hide_index=True,
                    key="systems_editor",
                    column_config={
                        "Selected": st.column_config.CheckboxColumn(
                            "Select", # Shorter title
                            help="Select systems to retrieve auth keys from",
                            default=True
                        ),
                         "Hostname": st.column_config.TextColumn(width="medium"),
                         "System ID": st.column_config.TextColumn(width="medium"),
                         "Role": st.column_config.TextColumn(width="small"),
                    },
                    use_container_width=True,
                    num_rows="fixed" # Or "dynamic" if preferred
                )
            except Exception as e:
                 st.error(f"Error creating system selection table: {e}")
                 return # Stop if table fails

            # --- Command Execution Section ---
            st.header("3. Execute Command")
            command = st.text_input(
                "Command to Execute",
                value="show configuration snmp", # Sensible default
                key="command_input",
                help="The command to run on selected systems (e.g., 'show configuration snmp')."
            )

            if st.button("Retrieve SNMP Keys", key="execute_button"):
                # Get selected systems from the potentially edited DataFrame
                selected_indices = edited_df[edited_df["Selected"]].index
                selected_systems_info = [st.session_state.systems[i] for i in selected_indices]


                if not selected_systems_info:
                    st.warning("Please select at least one system.")
                    return # Use return to stop execution

                # Reset previous results
                st.session_state.command_results = []
                st.session_state.failed_systems = []
                st.session_state.show_upload_options = False # Hide upload options until new results

                progress_bar = st.progress(0, text="Initializing command execution...")
                status_text = st.empty()
                total_systems = len(selected_systems_info)

                for i, system_info in enumerate(selected_systems_info):
                    hostname = system_info.get('hostname', 'Unknown')
                    system_id = system_info.get('system_id')
                    progress = (i + 1) / total_systems
                    status_text.text(f"Processing system {i+1}/{total_systems}: {hostname} ({system_id or 'No ID'})...")
                    progress_bar.progress(progress, text=f"Processing system {i+1}/{total_systems}: {hostname}")

                    if not system_id:
                        st.session_state.failed_systems.append({
                            "hostname": hostname, "reason": "Missing system_id in loaded data"
                        })
                        continue # Skip to next system

                    try:
                        raw_result = execute_command_on_system(
                            st.session_state.server,
                            st.session_state.api_token,
                            system_id,
                            command
                        )

                        if raw_result:
                            try:
                                result_json = json.loads(raw_result)
                                keys_result = extract_snmp_auth_keys(result_json)

                                if "error" in keys_result:
                                    st.session_state.failed_systems.append({
                                        "hostname": hostname, "reason": f"Key extraction error: {keys_result['error']}"
                                    })
                                else:
                                    # Store successful result
                                    st.session_state.command_results.append({
                                        "hostname": hostname,
                                        "system_id": system_id,
                                        "snmp-auth": { # Match expected structure
                                            "authentication_key": keys_result.get("authentication_key"),
                                            "privacy_key": keys_result.get("privacy_key")
                                        }
                                    })
                            except json.JSONDecodeError:
                                st.session_state.failed_systems.append({
                                    "hostname": hostname, "reason": "Command output was not valid JSON"
                                })
                            except Exception as e: # Catch errors during extraction
                                 st.session_state.failed_systems.append({
                                    "hostname": hostname, "reason": f"Error processing result: {e}"
                                })
                        else:
                            st.session_state.failed_systems.append({
                                "hostname": hostname, "reason": "Command execution failed or returned no output"
                            })
                    except Exception as e: # Catch errors during API call
                        st.session_state.failed_systems.append({
                            "hostname": hostname, "reason": f"API Error: {e}"
                        })
                        # Optional: Add a small delay or break if API fails repeatedly
                        # time.sleep(1)

                # --- Cleanup and Summary ---
                progress_bar.empty()
                status_text.empty()
                num_success = len(st.session_state.command_results)
                num_failed = len(st.session_state.failed_systems)
                if num_success > 0:
                    st.success(f"Command execution complete. Retrieved keys for {num_success} system(s).")
                if num_failed > 0:
                    st.warning(f"{num_failed} system(s) failed. See details below.")
                if num_success == 0 and num_failed == 0 and total_systems > 0:
                     st.info("Command execution finished, but no results were successfully processed.")


            # --- Display Results Section ---
            # Show results if there are any successful or failed attempts
            if st.session_state.get('command_results') or st.session_state.get('failed_systems'):
                display_results()

# --- Results Display Function ---

def display_results():
    """Display the command execution results and action buttons."""
    st.header("4. Results and Actions")

    results_data = []
    # Add successful results
    for result in st.session_state.get('command_results', []):
        results_data.append({
            "Hostname": result.get("hostname", "N/A"),
            "System ID": result.get("system_id", "N/A"),
            # Safely access nested keys
            "Authentication Key": result.get("snmp-auth", {}).get("authentication_key", "Not Found"),
            "Privacy Key": result.get("snmp-auth", {}).get("privacy_key", "Not Found"),
            "Status": "Success"
        })

    # Add failed systems
    for failure in st.session_state.get('failed_systems', []):
        results_data.append({
            "Hostname": failure.get("hostname", "N/A"),
            "System ID": "N/A",
            "Authentication Key": "N/A",
            "Privacy Key": "N/A",
            "Status": f"Failed: {failure.get('reason', 'Unknown reason')}"
        })

    if not results_data:
        st.info("No results to display.")
        return

    results_df = pd.DataFrame(results_data)

    st.dataframe(
        results_df,
        column_config={
             "Authentication Key": st.column_config.TextColumn(width="medium"),
             "Privacy Key": st.column_config.TextColumn(width="medium"),
             "Status": st.column_config.TextColumn(width="large"), # Wider status
             "Hostname": st.column_config.TextColumn(width="medium"),
             "System ID": st.column_config.TextColumn(width="medium"),
        },
        hide_index=True,
        use_container_width=True
    )

        # --- Display Failed Systems ---
    if st.session_state.get('failed_systems'):
        st.subheader("Failed Systems Summary")
        with st.expander("Click to view details of failed systems"):
            failed_df = pd.DataFrame(st.session_state.failed_systems)
            st.dataframe(failed_df, hide_index=True, use_container_width=True)

    # --- Action Buttons ---
    st.subheader("Actions")
    # Only show actions if there are successful results
    if st.session_state.get('command_results'):


        tab1, tab2, tab3 = st.tabs(["Upload Property Set", "Copy to Clipboard", "Save to File"])

        with tab1:
            st.header("Upload Property Set")
            # Call the corrected property set upload handler
            handle_property_set_upload()
        with tab2:
            st.header("Copy to Clipboard")
            if st.button("Copy to Clipboard", key="copy_clipboard_button"):
                # Format the results for clipboard
                clipboard_json = json.dumps({
                    "snmp-auth": st.session_state.command_results
                }, indent=2)
                
                # Use st.code to display copyable text
                st.code(clipboard_json, language="json")
                st.info("Use the copy button in the top-right corner to copy the data.")
        with tab3:
            st.header("Save to File")
            # Button to Save Results to File
            if st.button("Save to File", key="save_file_button"):
                # Format specifically for file output (match original structure if needed)
                file_payload = {"snmp-auth": st.session_state.command_results}
                try:
                    output_file = st.session_state.settings.get('default_output_file', 'snmp_keys_output.json')
                    with open(output_file, 'w') as f:
                        json.dump(file_payload, f, indent=2)
                    st.success(f"Results saved to `{output_file}`")
                except Exception as e:
                    st.error(f"Failed to save file: {e}")


def handle_property_set_upload():
    """
    Handle uploading results to a property set using st.session_state
    to manage UI flow correctly.
    """
    # Ensure required session state variables exist
    if 'server' not in st.session_state or 'api_token' not in st.session_state:
        # This button shouldn't even be visible if connection failed, but double-check
        st.error("Server or API token missing. Cannot upload.")
        return
    if not st.session_state.get('command_results'):
        st.warning("No results available to upload.")
        # Disable the button directly
        st.button("Upload to Property Set", key="upload_property_set_button_disabled", disabled=True)
        return

    # Button to toggle the visibility of upload options
    if st.button("Upload to Property Set", key="upload_property_set_button"):
        st.session_state.show_upload_options = not st.session_state.show_upload_options # Toggle visibility
        # Set default name when showing options
        if st.session_state.show_upload_options:
             st.session_state.property_set_name_input_value = st.session_state.settings.get('default_property_set_name', '')
        st.rerun() # Rerun to show/hide the options

    # Conditionally display upload options and the second button
    if st.session_state.get('show_upload_options', False): # Check state safely
        st.markdown("---") # Separator

        # Text input bound to session state
        st.session_state.property_set_name_input_value = st.text_input(
            "Property Set Name",
            value=st.session_state.property_set_name_input_value,
            key="property_set_name_input_stateful",
            help="Enter the name for the new or existing Apstra Property Set."
        )

        property_set_payload = None
        # Attempt to format the results using the helper function
        try:
            # Important: Ensure format_results_to_json returns a JSON *string* or a dict
            # that the create/update functions expect. Adjust if necessary.
            property_set_payload = format_results_to_json(st.session_state.command_results)
            # If it returns a dict, you might not need json.dumps later,
            # If it returns a string, the API functions must handle a string payload.
            # Assuming the helper functions expect the direct output of format_results_to_json
        except Exception as e:
            st.error(f"Error formatting results for Property Set: {e}")
            # Disable upload button if formatting fails
            st.button("Upload", key="confirm_upload_button_disabled_format", disabled=True)
            return # Stop here if formatting failed

        # Check if formatting produced a result
        if property_set_payload is None:
             st.warning("Formatted payload is empty. Cannot upload.")
             upload_disabled = True
        else:
             upload_disabled = False

        # The actual "Upload" button
        if st.button("Confirm Upload", key="confirm_upload_button", disabled=upload_disabled):
            property_set_name = st.session_state.property_set_name_input_value.strip() # Use the state value and strip whitespace

            if not property_set_name:
                st.warning("Property Set Name cannot be empty.")
                return # Stop if name is empty

            # Start processing spinner
            with st.spinner(f"Processing property set '{property_set_name}'..."):
                try:
                    # 1. Check if property set exists
                    property_sets = get_property_sets(
                        st.session_state.server,
                        st.session_state.api_token
                    )
                    existing_set = find_property_set_by_label(property_sets, property_set_name)

                    if existing_set:
                        # 2. Property Set Exists - Confirm Update (using a checkbox)
                        update_key = f"update_check_{existing_set.get('id', property_set_name)}" # Unique key
                        if st.checkbox(f"Update existing set '{property_set_name}'?", key=update_key, value=True): # Default to True maybe?
                            with st.spinner(f"Updating property set '{property_set_name}'..."):
                                result = update_property_set(
                                    st.session_state.server,
                                    st.session_state.api_token,
                                    existing_set["id"],
                                    property_set_name,
                                    property_set_payload # Pass the formatted payload
                                )
                                if "error" in result and "status" not in result: # Check for specific error structure
                                    st.error(f"Failed to update: {result.get('error', 'Unknown error')}")
                                else:
                                    st.success(f"Successfully updated property set '{property_set_name}'")
                                    st.session_state.show_upload_options = False # Hide on success
                                    st.rerun()
                        else:
                             st.info("Update cancelled by user.") # Checkbox not ticked

                    else:
                        # 3. Property Set Does Not Exist - Create New
                        with st.spinner(f"Creating property set '{property_set_name}'..."):
                            result = create_property_set(
                                st.session_state.server,
                                st.session_state.api_token,
                                property_set_name,
                                property_set_payload # Pass the formatted payload
                            )
                            if "error" in result: # Check for specific error structure
                                st.error(f"Failed to create: {result.get('error', 'Unknown error')}")
                            else:
                                st.success(f"Successfully created property set '{property_set_name}'")
                                st.session_state.show_upload_options = False # Hide on success
                                st.rerun()

                except Exception as e:
                    st.error(f"An error occurred during property set operation: {e}")
                    # Log the detailed error for debugging if possible
                    print(f"Property Set Upload Error: {e}") # Server-side log


        # Add a cancel button within the options section
        if st.button("Cancel Upload", key="cancel_upload_options"):
            st.session_state.show_upload_options = False
            st.rerun()
