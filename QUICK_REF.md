# Quick Reference - Proxmox Agent Commands

## Start the Agent
```bash
cd ~/Documents/Projects/Proxmox-Automation-Agent
source proxmox-agent-env/bin/activate
python agent-main.py
```

## Common Queries

### Information Queries (Read-Only)
```
"How many VMs do I have?"
"List all storage pools"
"What's the config of VM with ID 100?"
"Show me all my containers"
```

### Infrastructure Changes (Write Mode)
```
"Create a new VM with 4 cores and 8GB RAM"
"Add a second network interface to VM 105"
"Increase storage allocation for backup pool"
```

## Model Information

**Current Model:** `llama-3.3-70b-versatile`
- 70 Billion parameters
- 280 tokens/second
- Best for: Code generation, complex reasoning

**Alternative (faster):** `llama-3.1-8b-instant`
- 8 Billion parameters  
- 560 tokens/second
- Best for: Quick queries, prototyping

## Key Files

| File | Purpose |
|------|---------|
| `agent-main.py` | Main agent code |
| `tools/proxmox_reader.py` | Proxmox API reader |
| `tools/terraform_manager.py` | Terraform HCL generator |
| `LANGCHAIN_FIX.md` | LangChain setup guide |
| `MODEL_UPDATE.md` | Model information |
| `SETUP_COMPLETE.md` | Full setup documentation |

## Environment Setup

```bash
# Set Groq API key
export GROQ_API_KEY="your-key-here"

# Or add to .env file (loaded automatically)
echo "GROQ_API_KEY=your-key-here" > .env
```

## Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `GROQ_API_KEY` | Groq API authentication | `sk-xxxxx` |
| `PROXMOX_HOST` | Proxmox server URL | `https://pve.local:8006` |
| `PROXMOX_USER` | Proxmox username | `root@pam` |
| `PROXMOX_PASSWORD` | Proxmox password | `*****` |

## Useful Python Commands

```python
# Test Groq connection
from langchain_groq import ChatGroq
llm = ChatGroq(model_name="llama-3.3-70b-versatile")
print(llm.invoke("Hello!"))

# List Groq models
from groq import Groq
client = Groq()
for model in client.models.list().data:
    print(model.id)

# Test Proxmox connection  
from tools.proxmox_reader import list_all_vms
print(list_all_vms())
```

## Exit Commands

```
Type in agent: exit
Keyboard shortcut: Ctrl+C
```

## Status Checks

**Check Python Environment:**
```bash
python --version
which python
pip list | grep langchain
```

**Check Groq API:**
```bash
curl -H "Authorization: Bearer $GROQ_API_KEY" https://api.groq.com/openai/v1/models
```

**Check Proxmox Connection:**
```bash
python -c "from tools.proxmox_reader import list_all_vms; print(list_all_vms())"
```

## Troubleshooting Quick Fixes

| Error | Fix |
|-------|-----|
| `GROQ_API_KEY not set` | `export GROQ_API_KEY="..."` |
| `Model not found` | Check `MODEL_UPDATE.md` for valid models |
| `Connection refused` | Check Proxmox server is running |
| `Import errors` | `pip install langchain langchain-groq` |
| `Rate limited` | Wait 60 seconds, or use smaller model |

---

**For full documentation, see SETUP_COMPLETE.md**
