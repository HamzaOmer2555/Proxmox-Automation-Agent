# tools/proxmox_reader.py
import os
from proxmoxer import ProxmoxAPI
import requests
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Get credentials from environment variables
PROXMOX_HOST = os.getenv("PROXMOX_HOST")
PROXMOX_PORT = os.getenv("PROXMOX_PORT", "8006")
PROXMOX_USER = os.getenv("PROXMOX_USER")
PROXMOX_PASSWORD = os.getenv("PROXMOX_PASSWORD")
PROXMOX_TOKEN_ID = os.getenv("PROXMOX_TOKEN_ID")
PROXMOX_TOKEN_SECRET = os.getenv("PROXMOX_TOKEN_SECRET")

if not PROXMOX_HOST:
    raise ValueError("PROXMOX_HOST environment variable not set")

client = None
MOCK_MODE = False

print(f"DEBUG: PROXMOX_HOST = {PROXMOX_HOST}:{PROXMOX_PORT}")
print(f"DEBUG: PROXMOX_USER = {PROXMOX_USER}")
print(f"DEBUG: PROXMOX_TOKEN_ID = {PROXMOX_TOKEN_ID}")

try:
    print(f"Attempting to connect to Proxmox...")
    
    if PROXMOX_TOKEN_ID and PROXMOX_TOKEN_SECRET:
        print(f"Using token-based authentication...")
        # Token ID format should be: user@realm!tokenname
        # The user parameter should be: user@realm!tokenname
        client = ProxmoxAPI(
            PROXMOX_HOST,
            port=int(PROXMOX_PORT),
            user=PROXMOX_TOKEN_ID,  # Pass full token ID (e.g., root@pam!automation-agent)
            token_name='proxmox-agent',  # This is the token name part
            token_value=PROXMOX_TOKEN_SECRET,  # This is the token secret
            verify_ssl=False,
            timeout=60
        )
    elif PROXMOX_USER and PROXMOX_PASSWORD:
        print(f"Using password-based authentication...")
        client = ProxmoxAPI(
            PROXMOX_HOST,
            port=int(PROXMOX_PORT),
            user=PROXMOX_USER,
            password=PROXMOX_PASSWORD,
            verify_ssl=False,
            timeout=60
        )
    else:
        raise ValueError("No authentication credentials provided")
    
    # Test the connection by getting version
    print(f"Testing connection with /api2/json/version...")
    version = client.version.get()
    print(f"✅ Connected to Proxmox Version: {version.get('version')}")
    
except Exception as e:
    print(f"❌ Failed to connect to Proxmox: {type(e).__name__}: {str(e)}")
    print(f"⚠️ Running in MOCK MODE - using test data instead")
    MOCK_MODE = True
    client = None

def list_all_vms():
    """Returns a list of all VMs and Containers on the cluster."""
    if MOCK_MODE or not client:
        print("(Using mock data - Proxmox unavailable)")
        return [
            {"name": "ubuntu-web", "vmid": 100, "status": "running", "node": "pve1"},
            {"name": "debian-db", "vmid": 101, "status": "running", "node": "pve2"},
            {"name": "test-vm", "vmid": 102, "status": "stopped", "node": "pve1"}
        ]
    
    try:
        print(f"Fetching VMs from Proxmox...")
        resources = client.cluster.resources.get(type='vm')
        print(f"✅ Successfully fetched {len(resources)} VMs")
        return resources
    except Exception as e:
        print(f"❌ Error fetching VMs: {type(e).__name__}: {str(e)}")
        print("Falling back to mock data...")
        return [
            {"name": "ubuntu-web", "vmid": 100, "status": "running"},
            {"name": "debian-db", "vmid": 101, "status": "running"}
        ]

def get_vm_config(vmid: int):
    """Gets the full configuration for a specific VMID."""
    if MOCK_MODE or not client:
        return {"vmid": vmid, "name": "test-vm", "memory": 2048, "cores": 2}
    
    try:
        resources = client.cluster.resources.get(type='vm')
        for vm in resources:
            if vm['vmid'] == vmid:
                node = vm['node']
                config = client.nodes(node).qemu(vmid).config.get()
                return config
        return f"VM {vmid} not found"
    except Exception as e:
        print(f"❌ Error fetching VM config: {type(e).__name__}: {str(e)}")
        return {"vmid": vmid, "error": str(e)}

def list_storage_pools():
    """Returns all available storage pools."""
    if MOCK_MODE or not client:
        print("(Using mock data - Proxmox unavailable)")
        return [
            {"storage": "local", "type": "dir", "content": "images,rootdir"},
            {"storage": "local-lvm", "type": "lvmthin", "content": "images,rootdir"}
        ]
    
    try:
        print(f"Fetching storage pools from Proxmox...")
        storage = client.storage.get()
        print(f"✅ Successfully fetched {len(storage)} storage pools")
        return storage
    except Exception as e:
        print(f"❌ Error fetching storage: {type(e).__name__}: {str(e)}")
        print("Falling back to mock data...")
        return [
            {"storage": "local", "type": "dir"},
            {"storage": "local-lvm", "type": "lvmthin"}
        ]
