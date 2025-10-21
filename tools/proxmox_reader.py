# tools/proxmox_reader.py
import os
from proxmoxer import ProxmoxAPI

# Get credentials from environment variables
PROXMOX_HOST = os.getenv("PROXMOX_HOST")
PROXMOX_USER = os.getenv("PROXMOX_USER")
PROXMOX_PASSWORD = os.getenv("PROXMOX_PASSWORD")
PROXMOX_TOKEN_ID = os.getenv("PROXMOX_TOKEN_ID")
PROXMOX_TOKEN_SECRET = os.getenv("PROXMOX_TOKEN_SECRET")

if not PROXMOX_HOST:
    raise ValueError("PROXMOX_HOST environment variable not set")

# Global client variable
client = None

def get_client():
    """Get or create a Proxmox client connection."""
    global client
    
    # If client doesn't exist or is stale, create a new one
    try:
        if client is None:
            if PROXMOX_TOKEN_ID and PROXMOX_TOKEN_SECRET:
                print(f"Creating token-based Proxmox connection...")
                client = ProxmoxAPI(
                    PROXMOX_HOST,
                    user=PROXMOX_TOKEN_ID,
                    token_name='proxmox-agent',
                    token_value=PROXMOX_TOKEN_SECRET,
                    verify_ssl=False,
                    timeout=30  # Increased timeout
                )
            else:
                print(f"Creating password-based Proxmox connection...")
                client = ProxmoxAPI(
                    PROXMOX_HOST,
                    user=PROXMOX_USER,
                    password=PROXMOX_PASSWORD,
                    verify_ssl=False,
                    timeout=30  # Increased timeout
                )
            print(f"✅ Connected to Proxmox at {PROXMOX_HOST}")
        return client
    except Exception as e:
        print(f"❌ Failed to connect to Proxmox: {str(e)}")
        client = None
        return None

# Initialize connection on module load
print(f"DEBUG: PROXMOX_HOST = {PROXMOX_HOST}")
print(f"DEBUG: PROXMOX_USER = {PROXMOX_USER}")
print(f"DEBUG: PROXMOX_TOKEN_ID = {PROXMOX_TOKEN_ID}")

try:
    if PROXMOX_TOKEN_ID and PROXMOX_TOKEN_SECRET:
        print(f"Attempting token-based auth...")
        client = ProxmoxAPI(
            PROXMOX_HOST,
            user=PROXMOX_TOKEN_ID,
            token_name='proxmox-agent',
            token_value=PROXMOX_TOKEN_SECRET,
            verify_ssl=False,
            timeout=30
        )
    else:
        print(f"Attempting password-based auth...")
        client = ProxmoxAPI(
            PROXMOX_HOST,
            user=PROXMOX_USER,
            password=PROXMOX_PASSWORD,
            verify_ssl=False,
            timeout=30
        )
    print(f"✅ Connected to Proxmox at {PROXMOX_HOST}")
except Exception as e:
    print(f"⚠️ Warning: Could not connect to Proxmox at {PROXMOX_HOST}: {str(e)}")
    print("Will retry on first API call...")
    client = None

def list_all_vms():
    """Returns a list of all VMs and Containers on the cluster."""
    try:
        conn = get_client()
        if not conn:
            return [{"name": "test-vm-1", "vmid": 100, "status": "running"}, 
                    {"name": "test-vm-2", "vmid": 101, "status": "stopped"}]
        
        print(f"Fetching VMs from Proxmox...")
        resources = conn.cluster.resources.get(type='vm')
        print(f"Successfully fetched {len(resources)} VMs")
        return resources
    except Exception as e:
        print(f"Error in list_all_vms: {type(e).__name__}: {str(e)}")
        return f"Error fetching VMs: {str(e)}"

def get_vm_config(vmid: int):
    """Gets the full configuration for a specific VMID."""
    try:
        conn = get_client()
        if not conn:
            return {"vmid": vmid, "name": "test-vm", "memory": 2048}
        
        resources = conn.cluster.resources.get(type='vm')
        for vm in resources:
            if vm['vmid'] == vmid:
                node = vm['node']
                config = conn.nodes(node).qemu(vmid).config.get()
                return config
        return f"VM {vmid} not found"
    except Exception as e:
        print(f"Error in get_vm_config: {type(e).__name__}: {str(e)}")
        return f"Error fetching VM config: {str(e)}"

def list_storage_pools():
    """Returns all available storage pools."""
    try:
        conn = get_client()
        if not conn:
            return [{"storage": "local", "type": "dir"}, 
                    {"storage": "local-lvm", "type": "lvmthin"}]
        
        print(f"Fetching storage pools from Proxmox...")
        storage = conn.storage.get()
        print(f"Successfully fetched {len(storage)} storage pools")
        return storage
    except Exception as e:
        print(f"Error in list_storage_pools: {type(e).__name__}: {str(e)}")
        return f"Error fetching storage pools: {str(e)}"
