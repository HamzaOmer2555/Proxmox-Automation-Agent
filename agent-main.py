# agent_main.py
import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

from langchain_groq import ChatGroq
from langchain.tools import tool
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from tools.proxmox_reader import (
    list_all_vms, 
    get_vm_config, 
    list_storage_pools
)

# 1. Define Tools with better error handling
@tool
def get_proxmox_vms():
    """
    Get a list of all VMs running on the Proxmox cluster.
    Use this for questions like 'how many VMs', 'list VMs', 'what VMs exist'.
    """
    try:
        result = list_all_vms()
        print(f"DEBUG: get_proxmox_vms returned: {result}")
        if isinstance(result, str) and "Error" in result:
            return f"Failed to fetch VMs: {result}"
        return result
    except Exception as e:
        print(f"DEBUG: get_proxmox_vms exception: {type(e).__name__}: {str(e)}")
        return f"Error fetching VMs: {str(e)}"

@tool
def get_specific_vm_config(vmid: int):
    """
    Get detailed configuration for a specific VM by ID.
    Use this when the user asks about a specific VM's configuration.
    """
    try:
        result = get_vm_config(vmid)
        print(f"DEBUG: get_specific_vm_config({vmid}) returned: {result}")
        return result
    except Exception as e:
        print(f"DEBUG: get_specific_vm_config exception: {type(e).__name__}: {str(e)}")
        return f"Error fetching VM config: {str(e)}"

@tool
def get_proxmox_storage():
    """
    Get a list of all storage pools available on the Proxmox cluster.
    Use this for questions like 'what storage', 'list storage', 'available storage'.
    """
    try:
        result = list_storage_pools()
        print(f"DEBUG: get_proxmox_storage returned: {result}")
        if isinstance(result, str) and "Error" in result:
            return f"Failed to fetch storage: {result}"
        return result
    except Exception as e:
        print(f"DEBUG: get_proxmox_storage exception: {type(e).__name__}: {str(e)}")
        return f"Error fetching storage: {str(e)}"

@tool
def plan_infrastructure_changes(hcl_code: str):
    """
    Plans infrastructure changes using Terraform.
    First generates HCL code based on the user's request, then shows the plan.
    The user must approve before applying.
    """
    try:
        from tools.terraform_manager import generate_and_plan_infrastructure
        result = generate_and_plan_infrastructure(hcl_code)
        print(f"DEBUG: plan_infrastructure_changes returned: {result}")
        return result
    except Exception as e:
        print(f"DEBUG: plan_infrastructure_changes exception: {type(e).__name__}: {str(e)}")
        return f"Error planning infrastructure: {str(e)}"

@tool
def execute_infrastructure_changes():
    """
    Applies the currently staged Terraform plan.
    ONLY call this after 'plan_infrastructure_changes' has been
    run AND the user has given explicit approval.
    """
    try:
        from tools.terraform_manager import apply_infrastructure_plan
        result = apply_infrastructure_plan()
        print(f"DEBUG: execute_infrastructure_changes returned: {result}")
        return result
    except Exception as e:
        print(f"DEBUG: execute_infrastructure_changes exception: {type(e).__name__}: {str(e)}")
        return f"Error applying infrastructure: {str(e)}"

@tool
def destroy_all_managed_infrastructure():
    """
    Destroys all infrastructure managed by the terraform file.
    Get explicit user confirmation before using.
    """
    try:
        from tools.terraform_manager import destroy_infrastructure
        result = destroy_infrastructure()
        print(f"DEBUG: destroy_all_managed_infrastructure returned: {result}")
        return result
    except Exception as e:
        print(f"DEBUG: destroy_all_managed_infrastructure exception: {type(e).__name__}: {str(e)}")
        return f"Error destroying infrastructure: {str(e)}"

tools = [
    get_proxmox_vms,
    get_specific_vm_config,
    get_proxmox_storage,
    plan_infrastructure_changes,
    execute_infrastructure_changes,
    destroy_all_managed_infrastructure
]

# 2. Define the LLM
llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0,
    timeout=60
)

# 3. Define the Master Prompt
master_prompt = """
You are an expert Proxmox administrator and Terraform engineer.
Your name is 'Prox-Agent'.
You have access to a set of tools to read from and write to a Proxmox cluster.

IMPORTANT RULES:
1.  **READ-ONLY:** For any question that just asks for information (list, get, show, what is), 
    use the read-only tools like `get_proxmox_vms` or `get_proxmox_storage`.
2.  **WRITE/DESTROY:** For any request that involves creating, deleting, or modifying 
    a resource (VM, network, etc.), you MUST use the Terraform workflow.
3.  **TERRAFORM WORKFLOW:**
    a.  First, call the `plan_infrastructure_changes` tool. You must generate the HCL code 
        for the user's request. The user must not provide the code.
    b.  Show the output (the 'plan') to the user.
    c.  Ask the user for explicit confirmation (e.g., "Do you want to apply this plan?").
    d.  If and ONLY IF the user says yes, call the `execute_infrastructure_changes` tool.
4.  **Context:** Be aware of the user's environment. You can use read tools to 
    find out available nodes, templates, and storage pools to make better HCL.

Begin!
"""

# 4. Create agent
agent_executor = create_agent(llm, tools, system_prompt=master_prompt)

def run_cli_chat():
    """Run the CLI chat loop."""
    chat_history = []
    
    while True:
        try:
            user_input = input("User: ").strip()
            
            if user_input.lower() == 'exit':
                print("Goodbye!")
                break
            
            if not user_input:
                continue
            
            print("Agent is thinking...\n")
            
            result = agent_executor.invoke({
                "messages": chat_history + [HumanMessage(content=user_input)]
            })
            
            if result.get("messages"):
                response = result["messages"][-1].content
                print(f"Agent: {response}\n")
                chat_history.append(HumanMessage(content=user_input))
                chat_history.append(result["messages"][-1])
            else:
                print("Agent: No response received\n")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {type(e).__name__}: {str(e)}\n")

if __name__ == "__main__":
    print("Proxmox Agent is ready. Type 'exit' to quit.\n")
    run_cli_chat()