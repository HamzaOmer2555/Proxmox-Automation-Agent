# tools/terraform_manager.py
import subprocess
import os

TERRAFORM_DIR = "terraform_workspace"
TF_FILE_PATH = os.path.join(TERRAFORM_DIR, "main.tf")

# This file provides the Proxmox provider config
PROVIDER_TF = """
terraform {
  required_providers {
    proxmox = {
      source  = "telmate/proxmox"
      version = "2.9.14" # Pin the version
    }
  }
}

# Provider config is loaded from env vars (PM_API_URL, etc.)
provider "proxmox" {}
"""

def _run_command(command: list[str]):
    """Helper to run shell commands in the terraform directory."""
    try:
        result = subprocess.run(
            command,
            cwd=TERRAFORM_DIR,
            capture_output=True,
            text=True,
            check=True,
            env=os.environ # Pass environment variables
        )
        return {"success": True, "output": result.stdout}
    except subprocess.CalledProcessError as e:
        return {"success": False, "output": f"Error: {e.stderr}"}

def generate_and_plan_infrastructure(hcl_code: str):
    """
    Takes a string of Terraform HCL code, writes it to main.tf,
    runs 'terraform init' and 'terraform plan'.
    Returns the plan output or an error.
    This is the main tool for creating or updating infrastructure.
    """
    try:
        full_hcl = f"{PROVIDER_TF}\n\n{hcl_code}"
        with open(TF_FILE_PATH, "w") as f:
            f.write(full_hcl)
    except Exception as e:
        return f"Error writing HCL file: {e}"

    init_result = _run_command(["terraform", "init"])
    if not init_result["success"]:
        return f"Terraform Init Failed: {init_result['output']}"

    plan_result = _run_command(["terraform", "plan"])
    return f"Terraform Plan:\n{plan_result['output']}"

def apply_infrastructure_plan():
    """
    Applies the currently staged terraform plan.
    Should only be called after user confirms the plan.
    """
    apply_result = _run_command(["terraform", "apply", "-auto-approve"])
    return f"Terraform Apply:\n{apply_result['output']}"

def destroy_infrastructure():
    """Destroys all infrastructure defined in main.tf."""
    destroy_result = _run_command(["terraform", "destroy", "-auto-approve"])
    return f"Terraform Destroy:\n{destroy_result['output']}"
