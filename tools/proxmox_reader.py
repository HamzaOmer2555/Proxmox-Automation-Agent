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
        client = ProxmoxAPI(
            PROXMOX_HOST,
            port=int(PROXMOX_PORT),
            user=PROXMOX_USER,
            token_name='automation-agent',
            token_value=PROXMOX_TOKEN_SECRET,
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

def get_all_nodes():
    """Returns a list of all nodes in the cluster."""
    if MOCK_MODE or not client:
        print("(Using mock data - Proxmox unavailable)")
        return [
            {"node": "pve1", "status": "online", "uptime": 3600000},
            {"node": "pve2", "status": "online", "uptime": 2800000},
        ]
    
    try:
        print(f"Fetching nodes from Proxmox...")
        nodes = client.nodes.get()
        print(f"✅ Successfully fetched {len(nodes)} nodes")
        return nodes
    except Exception as e:
        print(f"❌ Error fetching nodes: {type(e).__name__}: {str(e)}")
        return []

def get_cluster_resources():
    """Returns all cluster resources (nodes, VMs, containers, etc.)."""
    if MOCK_MODE or not client:
        print("(Using mock data - Proxmox unavailable)")
        return {
            "nodes": [
                {"type": "node", "node": "pve1", "status": "online"},
                {"type": "node", "node": "pve2", "status": "online"},
            ],
            "vms": [
                {"type": "qemu", "vmid": 100, "name": "ubuntu-web", "status": "running", "node": "pve1"},
                {"type": "qemu", "vmid": 101, "name": "debian-db", "status": "running", "node": "pve2"},
                {"type": "lxc", "vmid": 102, "name": "test-container", "status": "stopped", "node": "pve1"},
            ]
        }
    
    try:
        print(f"Fetching cluster resources from Proxmox...")
        resources = client.cluster.resources.get()
        
        # Organize by type
        organized = {
            "nodes": [r for r in resources if r.get("type") == "node"],
            "vms": [r for r in resources if r.get("type") in ["qemu", "lxc"]],
            "storage": [r for r in resources if r.get("type") == "storage"],
        }
        print(f"✅ Successfully fetched cluster resources")
        return organized
    except Exception as e:
        print(f"❌ Error fetching cluster resources: {type(e).__name__}: {str(e)}")
        return {"nodes": [], "vms": [], "storage": []}

def list_all_vms():
    """Returns a list of all VMs and Containers on the cluster with hierarchy info."""
    if MOCK_MODE or not client:
        print("(Using mock data - Proxmox unavailable)")
        return [
            {
                "vmid": 100,
                "name": "ubuntu-web",
                "type": "qemu",
                "status": "running",
                "node": "pve1",
                "cpu": 2,
                "maxcpu": 4,
                "mem": 2147483648,
                "maxmem": 4294967296
            },
            {
                "vmid": 101,
                "name": "debian-db",
                "type": "qemu",
                "status": "running",
                "node": "pve2",
                "cpu": 4,
                "maxcpu": 8,
                "mem": 4294967296,
                "maxmem": 8589934592
            },
            {
                "vmid": 102,
                "name": "test-container",
                "type": "lxc",
                "status": "stopped",
                "node": "pve1",
                "cpu": 1,
                "maxcpu": 2,
                "mem": 0,
                "maxmem": 1073741824
            }
        ]
    
    try:
        print(f"Fetching all VMs and containers from Proxmox...")
        resources = client.cluster.resources.get()
        
        # Filter for VMs (qemu) and containers (lxc)
        vms = [r for r in resources if r.get("type") in ["qemu", "lxc"]]
        
        if len(vms) == 0:
            print(f"✅ No VMs or containers found in cluster")
            return []
        
        print(f"✅ Successfully fetched {len(vms)} VMs/containers")
        return vms
    except Exception as e:
        print(f"❌ Error fetching VMs: {type(e).__name__}: {str(e)}")
        return []

def get_vm_config(vmid: int):
    """Gets the full configuration for a specific VMID."""
    if MOCK_MODE or not client:
        return {
            "vmid": vmid,
            "name": "test-vm",
            "memory": 2048,
            "cores": 2,
            "sockets": 1,
            "node": "pve1"
        }
    
    try:
        print(f"Fetching config for VM {vmid}...")
        # First find which node has this VM
        resources = client.cluster.resources.get()
        vm_resource = None
        for resource in resources:
            if resource.get("vmid") == vmid and resource.get("type") in ["qemu", "lxc"]:
                vm_resource = resource
                break
        
        if not vm_resource:
            return f"VM {vmid} not found"
        
        node = vm_resource.get("node")
        vm_type = vm_resource.get("type")
        
        # Get full config based on type
        if vm_type == "qemu":
            config = client.nodes(node).qemu(vmid).config.get()
        elif vm_type == "lxc":
            config = client.nodes(node).lxc(vmid).config.get()
        else:
            return f"Unknown VM type: {vm_type}"
        
        # Add hierarchy info
        config["vmid"] = vmid
        config["node"] = node
        config["type"] = vm_type
        config["status"] = vm_resource.get("status", "unknown")
        
        print(f"✅ Successfully fetched config for VM {vmid}")
        return config
    except Exception as e:
        print(f"❌ Error fetching VM config: {type(e).__name__}: {str(e)}")
        return {"vmid": vmid, "error": str(e)}

def list_storage_pools():
    """Returns all available storage pools."""
    if MOCK_MODE or not client:
        print("(Using mock data - Proxmox unavailable)")
        return [
            {
                "storage": "local",
                "type": "dir",
                "content": "images,rootdir",
                "enabled": 1,
                "nodes": "pve1,pve2"
            },
            {
                "storage": "local-lvm",
                "type": "lvmthin",
                "content": "images,rootdir",
                "enabled": 1,
                "nodes": "pve1,pve2"
            }
        ]
    
    try:
        print(f"Fetching storage pools from Proxmox...")
        storage = client.storage.get()
        
        if len(storage) == 0:
            print(f"✅ No storage pools found")
            return []
        
        print(f"✅ Successfully fetched {len(storage)} storage pools")
        return storage
    except Exception as e:
        print(f"❌ Error fetching storage pools: {type(e).__name__}: {str(e)}")
        return []

def get_node_vms(node: str):
    """Returns all VMs on a specific node."""
    if MOCK_MODE or not client:
        return [
            {"vmid": 100, "name": "ubuntu-web", "type": "qemu", "status": "running", "node": node},
            {"vmid": 102, "name": "test-container", "type": "lxc", "status": "stopped", "node": node}
        ]
    
    try:
        print(f"Fetching VMs on node {node}...")
        resources = client.cluster.resources.get()
        node_vms = [
            r for r in resources 
            if r.get("type") in ["qemu", "lxc"] and r.get("node") == node
        ]
        print(f"✅ Successfully fetched {len(node_vms)} VMs on node {node}")
        return node_vms
    except Exception as e:
        print(f"❌ Error fetching VMs on node {node}: {type(e).__name__}: {str(e)}")
        return []
