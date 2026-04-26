import os
import autogen
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("NVIDIA_API_KEY")

from autogen.oai.client import OpenAIWrapper
original_create = OpenAIWrapper.create

def patched_create(self, **params):
    messages = params.get("messages", [])
    new_messages = []
    
    # Extract system message
    system_msgs = [m for m in messages if m["role"] == "system"]
    other_msgs = [m for m in messages if m["role"] != "system"]
    
    new_messages.extend(system_msgs)
    
    expected_role = "user"
    for m in other_msgs:
        if m["role"] == expected_role:
            new_messages.append(m)
            expected_role = "assistant" if expected_role == "user" else "user"
        else:
            if m["role"] == "assistant" and expected_role == "user":
                new_messages.append({"role": "user", "content": "Let's discuss."})
                new_messages.append(m)
                expected_role = "user"
            elif m["role"] == "user" and expected_role == "assistant":
                # Combine consecutive user messages by just changing the current one to assistant?
                # No, the API requires alternating. So we inject a dummy assistant message.
                new_messages.append({"role": "assistant", "content": "Go on."})
                new_messages.append(m)
                expected_role = "assistant"
                
    params["messages"] = new_messages
    return original_create(self, **params)

OpenAIWrapper.create = patched_create

llm_config = {
    "config_list": [{
        "model": "meta/llama-3.1-70b-instruct",
        "api_key": api_key,
        "base_url": "https://integrate.api.nvidia.com/v1"
    }]
}

agent1 = autogen.ConversableAgent("Agent1", llm_config=llm_config, human_input_mode="NEVER")
agent2 = autogen.ConversableAgent("Agent2", llm_config=llm_config, human_input_mode="NEVER")

agent1.initiate_chat(agent2, message="Hello!", max_turns=2)
