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



# Docker Build 

docker buildx build \
-t iamjarvs/apstra_snmp_auth:buildx-latest \
--platform linux/arm64,linux/amd64 \
--push \
.