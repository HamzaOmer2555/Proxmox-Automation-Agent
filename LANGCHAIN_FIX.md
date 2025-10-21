# LangChain Import Error Fix - Complete Guide

## Problem Summary
You were getting this error:
```
ImportError: cannot import name 'create_tool_calling_agent' from 'langchain.agents'
```

## Root Cause
**LangChain 1.0.0** (and recent versions) has deprecated the `AgentExecutor` and `create_tool_calling_agent` function. The project has moved to using **LangGraph** as the recommended agent framework.

### Why the Change?
- `AgentExecutor` is considered legacy and less flexible
- LangGraph provides better control, customization, and performance
- The LangChain team officially recommends using LangGraph for new projects

## Solution - Use LangChain's create_agent

### 1. **Install Required Packages**
```bash
pip install langchain>=0.3.0 langchain-groq langchain-core python-dotenv proxmoxer
```

### 2. **Update Imports**

#### Old (Broken) Code:
```python
from langchain.agents import create_tool_calling_agent
from langchain.agents import AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
```

#### New (Fixed) Code:
```python
from langchain.agents import create_agent
from langchain.tools import tool
```

### 3. **Update Agent Creation**

#### Old (Broken) Code:
```python
prompt = ChatPromptTemplate.from_template(prompt_template)
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
```

#### New (Fixed) Code:
```python
# Use langchain.agents.create_agent with system_prompt parameter
agent_executor = create_agent(llm, tools, system_prompt=master_prompt)
```

### 4. **Update Invocation Logic**

#### Old (Broken) Code:
```python
result = agent_executor.invoke({
    "input": user_input,
    "chat_history": chat_history
})
print(f"Agent: {result['output']}")
```

#### New (Fixed) Code:
```python
from langchain_core.messages import HumanMessage

result = agent_executor.invoke({
    "messages": chat_history + [HumanMessage(content=user_input)]
})

# Extract response from messages
if result["messages"]:
    response = result["messages"][-1].content
    print(f"Agent: {response}")
```

## Key Differences Between Legacy AgentExecutor and LangChain 1.0+ Agents

| Feature | AgentExecutor (Legacy) | LangChain 1.0+ create_agent |
|---------|------------------------|---------------------------|
| Agent Creation | `create_tool_calling_agent()` | `create_agent()` |
| System Prompt | Via `ChatPromptTemplate` | Via `system_prompt` parameter |
| Input Format | `{"input": str, "chat_history": list}` | `{"messages": List[BaseMessage]}` |
| Output Format | `{"output": str}` | `{"messages": List[BaseMessage]}` |
| State Management | Manual | Built-in, automatic |
| Error Handling | Basic | Advanced |
| Customization | Limited | Highly flexible |

## What's New in Your Updated Code

1. **Cleaner Agent Creation**: Just pass the LLM, tools, and system_prompt
2. **Message-Based Communication**: Uses LangChain's message format (HumanMessage, AIMessage)
3. **Built-in State Management**: Agent automatically manages conversation state
4. **Official LangChain Solution**: This is the recommended approach in LangChain 1.0+
5. **Future-Proof**: `create_agent` is part of the main LangChain library, not a deprecated function

## Testing Your Fix

Try running your agent:
```bash
python agent-main.py
```

Then test with a query:
```
User: List all my VMs
```

## Additional Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Migration Guide](https://python.langchain.com/docs/how_to/migrate_agent/)
- [Create React Agent Docs](https://langchain-ai.github.io/langgraph/reference/prebuilt/#langgraph.prebuilt.chat_agent_executor.create_react_agent)

## Next Steps (Optional Improvements)

1. **Add Streaming Support**: LangGraph supports streaming responses
2. **Error Handling**: Add try-catch blocks for tool execution failures
3. **Memory Management**: Implement persistent conversation history
4. **Tool Validation**: Add input validation for your Proxmox tools

```python
# Example: Streaming support
async def run_cli_chat_streaming():
    for event in agent_executor.stream({"messages": [HumanMessage(content=user_input)]}):
        print(event)  # Process streaming updates
```

---

**Status**: ✅ Fixed and Ready to Use!
