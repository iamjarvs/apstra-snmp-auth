# Apstra SNMP Authentication Manager

A tool for network administrators to retrieve and manage SNMP authentication and privacy keys from devices managed by Apstra.

![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/iamjarvs/apstra-snmp-auth/docker-build.yml?branch=main)
![Docker Pulls](https://img.shields.io/docker/pulls/iamjarvs/apstra_snmp_auth)

## Overview

The Apstra SNMP Authentication Manager provides a user-friendly interface for interacting with the Apstra API and automating the SNMP key extraction process. It simplifies the management of SNMP authentication details across multiple network devices in Apstra-managed environments.

This was built with a combination of my own work and Claude's Sonnet 3.7 model.

## Features

- **Authentication Key Retrieval**: Execute commands on network devices to extract SNMP authentication and privacy keys automatically and generate an Apstra property set.
- **Property Set Management**: Store and manage SNMP authentication details in Apstra property sets for easy reference and automation.
- **Bulk Processing**: Process multiple systems at once, with clear status and error reporting.
- **Export Options**: Save results to JSON files or copy to clipboard for use in other tools.
- **User-Friendly Interface**: Streamlit-based UI for easy navigation and operation.

## Demos

Live Demo @ https://apstra-snmp-app.streamlit.app/

Bulk Hash Key Retrieval
![](https://github.com/user-attachments/assets/8cb0a677-3e88-4075-a1f9-5be1f88deaea)

Per Blueprint Key Retrieval
![](https://github.com/user-attachments/assets/fd00a420-141a-43b5-be6f-140a244c341b)

## Installation

### Using Docker (Recommended)

The application is available as a Docker image:

```bash
docker run -d -p 8502:8502 iamjarvs/apstra_snmp_auth:latest
```

### Local Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/iamjarvs/apstra-snmp-auth.git
   cd apstra-snmp-auth
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   streamlit run app/ui/streamlit_app.py
   ```

## Usage

1. **Connect** to your Apstra server using the sidebar.
2. **Select a blueprint** containing the devices you want to work with.
3. **Execute commands** to retrieve SNMP authentication information.
4. **Save or upload** the results as needed.

### Command Line Interface

The application also provides a command-line interface for scripting:

```bash
python app/main.py --server <apstra-server> --username <username> [--password <password>]
```

For more options, run:
```bash
python app/main.py --help
```

## Technical Details

- Built with Python and Streamlit
- Communicates with Apstra API for device management
- Extracts SNMP authentication keys from device configurations
- Supports Junos-format encrypted keys
- Docker-based deployment for easy installation

## Project Structure

```
apstra-snmp-auth/
├── app/                   # Main application code
│   ├── __init__.py
│   ├── main.py            # CLI entry point
│   ├── ui/                # Streamlit UI components
│   │   ├── components/    # UI components
│   │   ├── utils/         # UI utilities
│   │   └── streamlit_app.py  # Main Streamlit application
│   └── utils/             # Utility helper functions
├── tests/                 # Test cases (not created)
├── Dockerfile             # Docker configuration
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Contact

- **GitHub Repository**: [https://github.com/iamjarvs/apstra-snmp-auth](https://github.com/iamjarvs/apstra-snmp-auth)
- **Author**: Adam Jarvis
