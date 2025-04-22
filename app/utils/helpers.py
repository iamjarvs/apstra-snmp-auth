"""
Helper functions for the Apstra System Command Tool.
"""
import os
import time
import requests
import json
import urllib3

# Suppress insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def authenticate_user(server, username, password):
    """
    Authenticate with Apstra and get an API token.
    
    Args:
        server (str): Apstra server address
        username (str): Apstra username
        password (str): Apstra password
        
    Returns:
        str: API token if successful, None otherwise
    """
    # Construct the API URL
    url = f"https://{server}/api/aaa/login"
    
    # Set up the request body
    body = {
        "username": username,
        "password": password
    }
    
    # Set up the headers
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        # Make the request, ignoring SSL verification for now
        response = requests.post(
            url,
            json=body,
            headers=headers,
            verify=False
        )
        
        # Check if the request was successful (any 2xx status code)
        if 200 <= response.status_code < 300:
            data = response.json()
            if "token" in data:
                return data["token"]
        
        # Better error handling
        try:
            error_data = response.json()
            if "error" in error_data:
                print(f"Authentication failed: {error_data['error']}")
            else:
                print(f"Authentication failed. Status code: {response.status_code}")
                print(f"Response: {error_data}")
        except json.JSONDecodeError:
            print(f"Authentication failed. Status code: {response.status_code}")
            print(f"Response: {response.text}")
        
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Apstra server: {e}")
        return None
    
def get_all_blueprints(server, token):
    """
    Get all blueprints from the Apstra server.
    
    Args:
        server (str): Apstra server address
        token (str): API token
        
    Returns:
        list: List of dictionaries containing blueprint details
    """
    # Construct the API URL
    url = f"https://{server}/api/blueprints"
    
    # Set up the headers
    headers = {
        "AuthToken": token
    }
    
    try:
        # Make the request
        response = requests.get(
            url,
            headers=headers,
            verify=False
        )
        
        # Check if the request was successful
        if 200 <= response.status_code < 300:
            data = response.json()
            if "items" in data:
                return data["items"]
            else:
                print("No blueprints found in response")
                return []
        
        # Handle errors
        try:
            error_data = response.json()
            print(f"Failed to get blueprints. Status code: {response.status_code}")
            print(f"Response: {error_data}")
        except json.JSONDecodeError:
            print(f"Failed to get blueprints. Status code: {response.status_code}")
            print(f"Response: {response.text}")
        
        return []
        
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Apstra server: {e}")
        return []

def select_blueprint(blueprints):
    """
    Present a list of blueprints to the user and let them select one.
    
    Args:
        blueprints (list): List of blueprint dictionaries
        
    Returns:
        dict: Selected blueprint or None if no selection made
    """
    if not blueprints:
        print("No blueprints available to select.")
        return None
    
    print("\nAvailable Blueprints:")
    print("---------------------")
    for idx, blueprint in enumerate(blueprints, 1):
        print(f"{idx}. {blueprint.get('label', 'Unknown')} (ID: {blueprint.get('id', 'Unknown')})")
    
    # Get user selection
    while True:
        try:
            selection = input("\nSelect a blueprint (number) or 'q' to quit: ")
            
            if selection.lower() == 'q':
                return None
            
            idx = int(selection) - 1
            if 0 <= idx < len(blueprints):
                return blueprints[idx]
            else:
                print(f"Invalid selection. Please enter a number between 1 and {len(blueprints)}.")
        except ValueError:
            print("Please enter a valid number or 'q' to quit.")

def get_system_ids(server, token, blueprint_id):
    """
    Get a list of all system IDs in the selected blueprint.
    
    Args:
        server (str): Apstra server address
        token (str): API token
        blueprint_id (str): ID of the selected blueprint
        
    Returns:
        list: List of dictionaries containing system details
    """
    # Construct the API URL for query engine
    url = f"https://{server}/api/blueprints/{blueprint_id}/qe"
    
    # Set up the headers
    headers = {
        "AuthToken": token,
        "Content-Type": "application/json"
    }
    
    # Query for systems with type 'system' and system_type 'switch'
    body = {
        "query": "node(type='system', name='switch_nodes', system_type='switch')"
    }
    
    try:
        # Make the request
        response = requests.post(
            url,
            json=body,
            headers=headers,
            verify=False
        )
        
        # Check if the request was successful
        if 200 <= response.status_code < 300:
            data = response.json()
            if "items" in data:
                # Process items to extract system details
                systems = []
                for item in data["items"]:
                    if "switch_nodes" in item:
                        node = item["switch_nodes"]
                        systems.append({
                            "id": node.get("id"),
                            "name": node.get("label", "Unknown"),
                            "hostname": node.get("hostname", "Unknown"),
                            "system_id": node.get("system_id", "Unknown"),
                            "role": node.get("role", "Unknown")
                        })
                return systems
            else:
                print("No systems found in response")
                return []
        
        # Handle errors
        try:
            error_data = response.json()
            print(f"Failed to get systems. Status code: {response.status_code}")
            print(f"Response: {error_data}")
        except json.JSONDecodeError:
            print(f"Failed to get systems. Status code: {response.status_code}")
            print(f"Response: {response.text}")
        
        return []
        
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Apstra server: {e}")
        return []
    
def execute_command_on_system(server, token, system_id, command):
    """
    Execute a command on a specific system and return the result.
    
    Args:
        server (str): Apstra server address
        token (str): API token
        system_id (str): ID of the system to run the command on
        command (str): Command to execute
        
    Returns:
        dict: Command result data
    """
    # Construct the API URL for command execution
    url = f"https://{server}/api/telemetry/fetchcmd"
    
    # Set up the headers
    headers = {
        "AuthToken": token,
        "Content-Type": "text/plain;charset=UTF-8"
    }
    
    # Command body
    body = {
        "system_id": system_id,
        "output_format": "json",
        "command_text": command
    }
    
    try:
        # Make the request to execute the command
        response = requests.post(
            url,
            json=body,
            headers=headers,
            verify=False
        )
        
        # Check if the request was successful
        if 200 <= response.status_code < 300:
            data = response.json()
            if "request_id" in data:
                request_id = data["request_id"]
                print(f"Command initiated, request ID: {request_id}")
                
                # Poll the request status until complete
                result = poll_command_result(server, token, request_id)
                
                # Clean up - delete the job
                delete_command_job(server, token, request_id)

                return result
            else:
                print("No request ID found in response")
                return None
        
        # Handle errors
        try:
            error_data = response.json()
            print(f"Failed to execute command. Status code: {response.status_code}")
            print(f"Response: {error_data}")
        except json.JSONDecodeError:
            print(f"Failed to execute command. Status code: {response.status_code}")
            print(f"Response: {response.text}")
        
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Apstra server: {e}")
        return None

def poll_command_result(server, token, request_id, max_attempts=30, delay=3):
    """
    Poll for command execution result.
    
    Args:
        server (str): Apstra server address
        token (str): API token
        request_id (str): ID of the request to poll
        max_attempts (int): Maximum number of polling attempts
        delay (int): Delay between polling attempts in seconds
        
    Returns:
        str: Command result data
    """
    # Construct the API URL for checking request status
    url = f"https://{server}/api/telemetry/fetchcmd/{request_id}?keep=true"
    
    # Set up the headers
    headers = {
        "AuthToken": token
    }
    
    for attempt in range(max_attempts):
        try:
            # Make the request
            response = requests.get(
                url,
                headers=headers,
                verify=False
            )
            
            # Check if the request was successful
            if 200 <= response.status_code < 300:
                data = response.json()
                
                # Check if the command has completed
                if "result" in data and data["result"] == "success":
                    output = data.get("output", "")
                    print("Command execution completed successfully.")
                    return output
                
                # Command is still running, wait and try again
                print(f"Command still running (attempt {attempt+1}/{max_attempts})...")
                time.sleep(delay)
            else:
                # Handle errors
                try:
                    error_data = response.json()
                    print(f"Failed to check command status. Status code: {response.status_code}")
                    print(f"Response: {error_data}")
                except json.JSONDecodeError:
                    print(f"Failed to check command status. Status code: {response.status_code}")
                    print(f"Response: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to Apstra server: {e}")
            return None
    
    print(f"Command timed out after {max_attempts} attempts")
    return None

def delete_command_job(server, token, request_id):
    """
    Delete a completed command job.
    
    Args:
        server (str): Apstra server address
        token (str): API token
        request_id (str): ID of the request to delete
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    # Construct the API URL for deleting the job
    url = f"https://{server}/api/telemetry/fetchcmd/{request_id}"
    
    # Set up the headers
    headers = {
        "AuthToken": token,
        "Content-Type": "application/json"
    }
    
    # Request body
    body = {
        "request_id": request_id
    }
    
    try:
        # Make the request
        response = requests.delete(
            url,
            json=body,
            headers=headers,
            verify=False
        )
        
        # Check if the request was successful
        if 200 <= response.status_code < 300:
            print(f"Successfully deleted command job: {request_id}")
            return True
        else:
            print(f"Failed to delete command job. Status code: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Apstra server: {e}")
        return False

def extract_snmp_engine_id(result_data):
    """
    Extract SNMP engine ID from command result.
    
    Args:
        result_data (dict): Parsed command result data
        
    Returns:
        str: Extracted SNMP engine ID or error message
    """
    try:
        # Navigate through the nested JSON structure
        snmp_info = result_data.get("snmp-v3-information", [])[0]
        general_info = snmp_info.get("snmp-v3-general-information", [])[0]
        engine_info = general_info.get("snmp-v3-engine-information", [])[0]
        engine_id_container = engine_info.get("engine-id", [])[0]
        engine_id = engine_id_container.get("data", "")
        
        # Return the engine ID
        return engine_id.strip()
    except (IndexError, KeyError, AttributeError) as e:
        # Return specific error message
        return f"extraction_error: {str(e)}"
    except Exception as e:
        # Catch any other errors
        return f"unexpected_error: {str(e)}"

import hashlib
import binascii
import hmac
import random
import string
from itertools import repeat
from functools import partial

# Constants for junos_encrypt9
MAGIC = "$9$"
FAMILY = [
    "QzF3n6/9CAtpu0O",
    "B1IREhcSyrleKvMW8LXx",
    "7N-dVbwsY2g4oaJZGUDj",
    "iHkq.mPf5T",
]
EXTRA = {}
for counter, value in enumerate(FAMILY):
    for character in value:
        EXTRA[character] = 3 - counter

NUM_ALPHA = [x for x in "".join(FAMILY)]
ALPHA_NUM = {NUM_ALPHA[x]: x for x in range(0, len(NUM_ALPHA))}

ENCODING = [
    [1, 4, 32],
    [1, 16, 32],
    [1, 8, 32],
    [1, 64],
    [1, 32],
    [1, 4, 16, 128],
    [1, 32, 64],
]

# Constants for SNMP v3
LOCAL_ENGINE_PREFIX = "80000a4c04"

def generate_snmp_keys(engine_id, password, salt='j', rand='a'):
    """
    Generate SNMP v3 authentication and privacy keys from a password and engine ID.
    
    Args:
        engine_id (str): SNMP engine ID (format: "xx xx xx xx xx...")
        password (str): Clear text password
        salt (str): Salt character for encryption (default: 'j')
        rand (str): Random character for encryption (default: 'a')
        
    Returns:
        dict: Dictionary containing authentication_key and privacy_key
    """
    # Remove spaces from engine ID
    engine_id_clean = engine_id.replace(" ", "")
    
    # Generate authentication key
    auth_key = junos_snmpv3_auth_hash(password, engine_id_clean, hash_alg='sha1')
    encrypted_auth_key = junos_encrypt9(auth_key, salt, rand)
    
    # Generate privacy key
    priv_key = junos_snmpv3_priv_hash(password, engine_id_clean, hash_alg='sha1')
    encrypted_priv_key = junos_encrypt9(priv_key, salt, rand)
    
    return {
        "authentication_key": encrypted_auth_key,
        "privacy_key": encrypted_priv_key
    }

# SNMP v3 Key Generation Functions
def hashgen_hash(bytes_data, alg=hashlib.sha1, name=None, raw=False):
    """
    Generate a hash of the provided bytes.
    
    Args:
        bytes_data (bytes): Data to hash
        alg (function): Hash algorithm function
        name (str): Name of the algorithm (not used)
        raw (bool): Whether to return raw bytes or hex string
        
    Returns:
        bytes or str: Hash digest
    """
    digest = alg(bytes_data).digest()
    return digest if raw else digest.hex()

def hashgen_expand(substr, target_len):
    """
    Expand a substring to the target length by repeating it.
    
    Args:
        substr (str): Substring to expand
        target_len (int): Target length
        
    Returns:
        str: Expanded string
    """
    reps = (target_len // len(substr) + 1)
    return "".join(list(repeat(substr, reps)))[:target_len]

def hashgen_kdf(password, alg_func=None):
    """
    Key derivation function.
    
    Args:
        password (str): Password to derive key from
        alg_func (function): Hash algorithm function
        
    Returns:
        bytes: Derived key
    """
    alg_func = partial(hashgen_hash, alg=hashlib.sha1, name="sha1") if alg_func is None else alg_func
    
    data = hashgen_expand(password, 1048576).encode("utf-8")
    return alg_func(data, raw=True)

def hashgen_derive_msg(passphrase, engine, alg_func):
    """
    Derive message for SNMP v3 key generation.
    
    Args:
        passphrase (str): Passphrase
        engine (str): Engine ID (hex string)
        alg_func (function): Hash algorithm function
        
    Returns:
        bytes: Derived message
    """
    Ku = hashgen_kdf(passphrase, alg_func)
    E = bytearray.fromhex(engine)
    
    return b"".join([Ku, E, Ku])

def junos_snmpv3_engine_id(value, engine_type="local"):
    """
    Generate SNMP v3 engine ID.
    
    Args:
        value (str): Value to use for engine ID
        engine_type (str): Engine type (only 'local' supported)
        
    Returns:
        str: Engine ID
    """
    if engine_type == "local":
        return f"{LOCAL_ENGINE_PREFIX}{bytes(value.encode('utf-8')).hex()}"
    else:
        raise ValueError(f"No engine type named {engine_type}")

def junos_snmpv3_auth_hash(value, engine_id, hash_alg='sha1'):
    """
    Generate SNMP v3 authentication hash.
    
    Args:
        value (str): Password
        engine_id (str): Engine ID
        hash_alg (str): Hash algorithm
        
    Returns:
        str: Authentication hash
    """
    alg_func = partial(hashgen_hash, alg=getattr(hashlib, hash_alg), name=hash_alg)
    Kul_auth = hashgen_derive_msg(value, engine_id, alg_func)
    return alg_func(Kul_auth)

def junos_snmpv3_priv_hash(value, engine_id, hash_alg='sha1'):
    """
    Generate SNMP v3 privacy hash.
    
    Args:
        value (str): Password
        engine_id (str): Engine ID
        hash_alg (str): Hash algorithm
        
    Returns:
        str: Privacy hash
    """
    alg_func = partial(hashgen_hash, alg=getattr(hashlib, hash_alg), name=hash_alg)
    Kul_priv = hashgen_derive_msg(value, engine_id, alg_func)
    if hash_alg == "sha1":
        return alg_func(Kul_priv)[:32]
    else:
        return alg_func(Kul_priv)

# Junos Encryption Functions
def __nibble(cref, length):
    """
    Extract a nibble from a string.
    
    Args:
        cref (str): String to extract from
        length (int): Length of nibble
        
    Returns:
        tuple: (nibble, rest)
    """
    nib = cref[0:length]
    rest = cref[length:]
    
    if len(nib) != length:
        raise Exception(f"Ran out of characters: hit '{nib}', expecting {length} chars")
    
    return nib, rest

def __gap(c1, c2):
    """
    Calculate gap between two characters.
    
    Args:
        c1 (str): First character
        c2 (str): Second character
        
    Returns:
        int: Gap value
    """
    return (ALPHA_NUM[str(c2)] - ALPHA_NUM[str(c1)]) % (len(NUM_ALPHA)) - 1

def __gap_decode(gaps, dec):
    """
    Decode gaps to character.
    
    Args:
        gaps (list): Gap values
        dec (list): Decode values
        
    Returns:
        str: Decoded character
    """
    num = 0
    
    if len(gaps) != len(dec):
        raise Exception("Nibble and decode size not the same.")
    
    for x in range(0, len(gaps)):
        num += gaps[x] * dec[x]
    
    return chr(num % 256)

def __reverse(current):
    """
    Reverse a list.
    
    Args:
        current (list): List to reverse
        
    Returns:
        list: Reversed list
    """
    reversed_list = list(current)
    reversed_list.reverse()
    return reversed_list

def __gap_encode(pc, prev, encode):
    """
    Encode a character using gap values.
    
    Args:
        pc (str): Character to encode
        prev (str): Previous character
        encode (list): Encoding values
        
    Returns:
        str: Encoded string
    """
    __ord = ord(pc)
    
    crypt = ""
    gaps = []
    for mod in __reverse(encode):
        gaps.insert(0, int(__ord / mod))
        __ord %= mod
    
    for gap in gaps:
        gap += ALPHA_NUM[prev] + 1
        prev = NUM_ALPHA[gap % len(NUM_ALPHA)]
        crypt += prev
    
    return crypt

def __randc(counter=0):
    """
    Generate random characters.
    
    Args:
        counter (int): Number of characters to generate
        
    Returns:
        str: Random characters
    """
    return_value = ""
    for _ in range(counter):
        return_value += NUM_ALPHA[random.randrange(len(NUM_ALPHA))]
    return return_value

def is_encrypted(value):
    """
    Check if a value is already encrypted.
    
    Args:
        value (str): Value to check
        
    Returns:
        bool: True if encrypted, False otherwise
    """
    return value.startswith(MAGIC)

def junos_encrypt9(value, salt=None, rand=None):
    """
    Encrypt a value using Junos encrypt9 algorithm.
    
    Args:
        value (str): Value to encrypt
        salt (str): Salt character
        rand (str): Random characters
        
    Returns:
        str: Encrypted value
    """
    if not value:
        return ""
    
    if is_encrypted(value):
        return value
    
    if not salt and rand:
        raise Exception("When rand is set, salt must be set as well")
    
    if not salt:
        salt = __randc(1)
    
    if not rand:
        rand = __randc(EXTRA[salt])
    elif EXTRA[salt] != len(rand):
        raise Exception(f"Salt set to {salt} but rand doesn't have the proper length ({len(rand)} instead of {EXTRA[salt]})")
    
    position = 0
    previous = salt
    crypted = MAGIC + salt + rand
    
    for x in value:
        encode = ENCODING[position % len(ENCODING)]
        crypted += __gap_encode(x, previous, encode)
        previous = crypted[-1]
        position += 1
    
    return crypted

def get_property_sets(server, token):
    """
    Get all property sets from the Apstra server.
    
    Args:
        server (str): Apstra server address
        token (str): API token
        
    Returns:
        list: List of dictionaries containing property set details
    """
    # Construct the API URL
    url = f"https://{server}/api/property-sets"
    
    # Set up the headers
    headers = {
        "AuthToken": token,
        "Accept": "application/json"
    }
    
    try:
        # Make the request
        response = requests.get(
            url,
            headers=headers,
            verify=False
        )
        
        # Check if the request was successful
        if 200 <= response.status_code < 300:
            data = response.json()
            if "items" in data:
                return data["items"]
            else:
                print("No property sets found in response")
                return []
        
        # Handle errors
        try:
            error_data = response.json()
            print(f"Failed to get property sets. Status code: {response.status_code}")
            print(f"Response: {error_data}")
        except json.JSONDecodeError:
            print(f"Failed to get property sets. Status code: {response.status_code}")
            print(f"Response: {response.text}")
        
        return []
        
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Apstra server: {e}")
        return []

def create_property_set(server, token, label, values):
    """
    Create a new property set on the Apstra server.
    
    Args:
        server (str): Apstra server address
        token (str): API token
        label (str): Label for the property set
        values (dict): Values for the property set
        
    Returns:
        dict: Response from the server
    """
    # Construct the API URL
    url = f"https://{server}/api/property-sets"
    
    # Set up the headers
    headers = {
        "AuthToken": token,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Create request body
    body = {
        "label": label,
        "values": values
    }
    
    try:
        # Make the request
        response = requests.post(
            url,
            json=body,
            headers=headers,
            verify=False
        )
        
        # Check if the request was successful
        if 200 <= response.status_code < 300:
            return response.json()
        
        # Handle errors
        try:
            error_data = response.json()
            print(f"Failed to create property set. Status code: {response.status_code}")
            print(f"Response: {error_data}")
            return {"error": error_data}
        except json.JSONDecodeError:
            print(f"Failed to create property set. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return {"error": response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Apstra server: {e}")
        return {"error": str(e)}

def update_property_set(server, token, property_set_id, label, values):
    """
    Update an existing property set on the Apstra server.
    
    Args:
        server (str): Apstra server address
        token (str): API token
        property_set_id (str): ID of the property set to update
        label (str): Label for the property set
        values (dict): Values for the property set
        
    Returns:
        dict: Response from the server
    """
    # Construct the API URL
    url = f"https://{server}/api/property-sets/{property_set_id}"
    
    # Set up the headers
    headers = {
        "AuthToken": token,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Create request body
    body = {
        "label": label,
        "values": values
    }
    
    try:
        # Make the request
        response = requests.put(
            url,
            json=body,
            headers=headers,
            verify=False
        )
        
        # Check if the request was successful
        if 200 <= response.status_code < 300:
            return response.json()
        
        # Handle errors
        try:
            error_data = response.json()
            print(f"Failed to update property set. Status code: {response.status_code}")
            print(f"Response: {error_data}")
            return {"error": error_data}
        except json.JSONDecodeError:
            print(f"Failed to update property set. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return {"error": response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Apstra server: {e}")
        return {"error": str(e)}

def find_property_set_by_label(property_sets, label):
    """
    Find a property set by its label.
    
    Args:
        property_sets (list): List of property sets
        label (str): Label to search for
        
    Returns:
        dict or None: Property set if found, None otherwise
    """
    for prop_set in property_sets:
        if prop_set.get("label") == label:
            return prop_set
    return None

def manage_property_set_upload(server, token, json_payload, property_set_name="snmp_auth"):
    """
    Handle the upload of the JSON payload to a property set.
    
    Args:
        server (str): Apstra server address
        token (str): API token
        json_payload (dict): JSON payload to upload
        property_set_name (str): Name of the property set
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Get all property sets
    print(f"\nChecking for existing property set '{property_set_name}'...")
    property_sets = get_property_sets(server, token)
    
    if not property_sets:
        print("Failed to retrieve property sets from Apstra server.")
        return False
    
    # Look for an existing property set with the same name
    existing_property_set = find_property_set_by_label(property_sets, property_set_name)
    
    if existing_property_set:
        print(f"Property set '{property_set_name}' already exists with ID: {existing_property_set['id']}")
        
        # Ask the user what to do
        print("\nOptions:")
        print("1. Update the existing property set")
        print("2. Create a new property set with a different name")
        print("3. Cancel")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == "1":
            # Update existing property set
            print(f"\nUpdating property set '{property_set_name}'...")
            result = update_property_set(
                server, 
                token, 
                existing_property_set["id"], 
                property_set_name, 
                json_payload
            )
            
            if "error" in result:
                print(f"Failed to update property set: {result['error']}")
                return False
            
            print(f"Successfully updated property set '{property_set_name}'.")
            return True
            
        elif choice == "2":
            # Create new property set with different name
            new_name = input("\nEnter a new name for the property set: ")
            
            if not new_name:
                print("No name provided. Cancelling.")
                return False
            
            print(f"\nCreating new property set '{new_name}'...")
            result = create_property_set(server, token, new_name, json_payload)
            
            if "error" in result:
                print(f"Failed to create property set: {result['error']}")
                return False
            
            print(f"Successfully created property set '{new_name}'.")
            return True
            
        else:
            # Cancel
            print("\nCancelled. No property set was created or updated.")
            return False
            
    else:
        # No existing property set, create a new one
        print(f"\nCreating new property set '{property_set_name}'...")
        result = create_property_set(server, token, property_set_name, json_payload)
        
        if "error" in result:
            print(f"Failed to create property set: {result['error']}")
            return False
        
        print(f"Successfully created property set '{property_set_name}'.")
        return True

def format_results_to_json(systems_results):
    """
    Format command results into the required JSON structure.
    
    Args:
        systems_results (list): List of dictionaries containing system results
        
    Returns:
        dict: Formatted JSON payload
    """
    # Create the final JSON structure
    json_payload = {
        "snmp_auth": systems_results
    }
    
    return json_payload