#!/usr/bin/env python3
"""
Apstra System Command Tool.

This tool authenticates with Apstra, retrieves system IDs from the data center fabric,
runs commands on each system, and formats the results into JSON.
"""
import os
import sys
import argparse
import json
from getpass import getpass

from utils.helpers import (
    authenticate_user,
    get_all_blueprints,
    select_blueprint,
    get_system_ids,
    execute_command_on_system,
    extract_snmp_engine_id,
    generate_snmp_keys,
    manage_property_set_upload,
    format_results_to_json
)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Apstra System Command Tool")
    
    parser.add_argument(
        "--server", "-s",
        help="Apstra server address (default: from APSTRA_SERVER env var)",
        default=os.environ.get("APSTRA_SERVER", "")
    )
    
    parser.add_argument(
        "--username", "-u",
        help="Apstra username (default: from APSTRA_USERNAME env var)",
        default=os.environ.get("APSTRA_USERNAME", "")
    )
    
    parser.add_argument(
        "--password", "-p",
        help="Apstra password (default: from APSTRA_PASSWORD env var)",
        default=os.environ.get("APSTRA_PASSWORD", "")
    )

    parser.add_argument(
        "--output", "-o",
        help="Output file for results (JSON format)",
        default="results.json"
    )
    
    parser.add_argument(
        "--save-credentials",
        help="Save credentials as environment variables",
        action="store_true"
    )

    parser.add_argument(
        "--snmp-password",
        help="SNMP password to use for key generation",
        default=""
    )
    
    parser.add_argument(
        "--salt",
        help="Salt character for Junos encryption (default: j)",
        default="j"
    )
    
    parser.add_argument(
        "--rand",
        help="Random character for Junos encryption (default: a)",
        default="a"
    )
    
    return parser.parse_args()

def main():
    """Main entry point for the application."""
    args = parse_arguments()
    
    # Get server address
    server = args.server
    if not server:
        server = input("Enter Apstra server address: ")
    
    # Get username
    username = args.username
    if not username:
        username = input("Enter Apstra username: ")
    
    # Get password (not from arguments for security reasons)
    password = os.environ.get("APSTRA_PASSWORD", "")
    if not password:
        password = getpass("Enter Apstra password: ")
    
    # Get SNMP password for key generation
    snmp_password = args.snmp_password
    if not snmp_password:
        snmp_password = getpass("Enter SNMP password for key generation: ")
    
    # Get salt and rand characters
    salt = args.salt
    rand = args.rand
    
    # Save credentials if requested
    if args.save_credentials:
        os.environ["APSTRA_SERVER"] = server
        os.environ["APSTRA_USERNAME"] = username
        os.environ["APSTRA_PASSWORD"] = password
        print("Credentials saved to environment variables for this session.")

    # Authenticate with Apstra
    print(f"Authenticating with Apstra server {server}...")
    token = authenticate_user(server, username, password)
    
    if not token:
        print("\n" + "="*80)
        print("ERROR: Authentication failed. Please check your credentials.")
        print("="*80 + "\n")
        sys.exit(1)
    
    print("Authentication successful!")
    
    # Get all blueprints
    print("Retrieving blueprints from Apstra server...")
    blueprints = get_all_blueprints(server, token)
    
    if not blueprints:
        print("\n" + "="*80)
        print("ERROR: No blueprints found or error retrieving blueprints.")
        print("="*80 + "\n")
        sys.exit(1)
    
    print(f"Found {len(blueprints)} blueprints.")
    
    # Let user select a blueprint
    selected_blueprint = select_blueprint(blueprints)
    
    if not selected_blueprint:
        print("No blueprint selected. Exiting.")
        sys.exit(0)
    
    blueprint_id = selected_blueprint.get('id')
    print(f"Selected blueprint: {selected_blueprint.get('label')} (ID: {blueprint_id})")
    
    # Get system IDs for the selected blueprint
    print(f"Retrieving system IDs for blueprint '{selected_blueprint.get('label')}'...")
    systems = get_system_ids(server, token, blueprint_id)
    
    if not systems:
        print("\n" + "="*80)
        print("ERROR: No systems found or error retrieving systems.")
        print("="*80 + "\n")
        sys.exit(1)
    
    print(f"Found {len(systems)} systems.")
    
    # Execute command on each system
    systems_results = []
    failed_systems = []
    command = "show snmp v3"
    print(f"Command to execute on all systems: '{command}'")
    
    for idx, system in enumerate(systems, 1):
        hostname = system.get('hostname', 'Unknown')
        system_id = system.get('system_id')
        
        if not system_id:
            print(f"[{idx}/{len(systems)}] WARNING: Skipping system {hostname} - No system_id available.")
            failed_systems.append({
                "hostname": hostname,
                "reason": "Missing system_id"
            })
            continue
            
        print(f"[{idx}/{len(systems)}] Running command on system {hostname} (ID: {system_id})...")
        result = execute_command_on_system(server, token, system_id, command)
        
        if result:
            # Parse the result string as JSON
            try:
                result_json = json.loads(result)
                
                # Extract SNMP auth
                engine_id = extract_snmp_engine_id(result_json)
                
                # Check if we got an error during extraction
                if engine_id.startswith("extraction_error") or engine_id.startswith("unexpected_error"):
                    print(f"[{idx}/{len(systems)}] WARNING: Could not extract SNMP engine ID from {hostname}: {engine_id}")
                    failed_systems.append({
                        "hostname": hostname,
                        "reason": engine_id
                    })
                else:
                    # Generate SNMP keys
                    try:
                        keys = generate_snmp_keys(engine_id, snmp_password, salt, rand)
                        
                        # Store the result for this system
                        systems_results.append({
                            "hostname": hostname,
                            "snmp_auth": {
                                "engine_id": engine_id,
                                "authentication_key": keys["authentication_key"],
                                "privacy_key": keys["privacy_key"]
                            }
                        })
                        print(f"[{idx}/{len(systems)}] Command execution and key generation successful for {hostname}.")
                    except Exception as e:
                        print(f"[{idx}/{len(systems)}] WARNING: Key generation failed for {hostname}: {e}")
                        failed_systems.append({
                            "hostname": hostname,
                            "reason": f"Key generation error: {str(e)}"
                        })
            except json.JSONDecodeError as e:
                print(f"[{idx}/{len(systems)}] WARNING: Could not parse command result from {hostname}: {e}")
                failed_systems.append({
                    "hostname": hostname,
                    "reason": f"JSON parse error: {str(e)}"
                })
        else:
            print(f"[{idx}/{len(systems)}] WARNING: Command execution failed for {hostname}.")
            failed_systems.append({
                "hostname": hostname,
                "reason": "Command execution failed"
            })
    
    # Display summary of failures
    if failed_systems:
        print("\n" + "="*80)
        print(f"WARNING: Failed to collect data from {len(failed_systems)} out of {len(systems)} systems:")
        print("="*80)
        for i, failure in enumerate(failed_systems, 1):
            print(f"{i}. {failure['hostname']}: {failure['reason']}")
        print("="*80 + "\n")
    
    if not systems_results:
        print("\n" + "="*80)
        print("ERROR: No results collected. Exiting.")
        print("="*80 + "\n")
        sys.exit(1)
    
     # Format results
    print("Formatting results into final JSON payload...")
    json_payload = {
        "snmp_auth": systems_results
    }
    
    # Save to file
    output_file = args.output
    with open(output_file, 'w') as f:
        json.dump(json_payload, f, indent=2)
    
    print(f"Results saved to {output_file}")
    
    # Upload as property set
    print("\nWould you like to upload these results as a property set to Apstra?")
    choice = input("Enter 'y' to continue, any other key to skip: ")
    
    if choice.lower() == 'y':
        # Upload the results as a property set
        success = manage_property_set_upload(server, token, json_payload)
        
        if success:
            print("\nProperty set operation completed successfully.")
        else:
            print("\nProperty set operation failed or was cancelled.")
    else:
        print("\nSkipping property set upload.")
    
    # Print summary of results
    print("\nResults summary:")
    print(f"Successfully collected data from {len(systems_results)} out of {len(systems)} systems")
    print("Sample of JSON payload:")
    
    # Format a sample of the JSON for display
    sample_json = json.dumps(json_payload, indent=2)
    if len(sample_json) > 500:
        print(sample_json[:500] + "...")
    else:
        print(sample_json)

if __name__ == "__main__":
    main()