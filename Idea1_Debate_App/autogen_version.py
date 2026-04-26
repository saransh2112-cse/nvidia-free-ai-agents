import os
import autogen
from dotenv import load_dotenv

load_dotenv()

# We need the API key to be set
api_key = os.getenv("NVIDIA_API_KEY")

if not api_key:
    print("Please set your NVIDIA_API_KEY in the .env file")
    exit(1)

# Configure the LLMs
llm_config_llama = {
    "config_list": [{
        "model": "meta/llama-3.1-70b-instruct",
        "api_key": api_key,
        "base_url": "https://integrate.api.nvidia.com/v1"
    }],
    "temperature": 0.7
}

llm_config_mixtral = {
    "config_list": [{
        "model": "mistralai/mixtral-8x22b-instruct-v0.1",
        "api_key": api_key,
        "base_url": "https://integrate.api.nvidia.com/v1"
    }],
    "temperature": 0.7
}

llama_agent = autogen.ConversableAgent(
    name="Llama_Debater",
    llm_config=llm_config_llama,
    system_message="You are Llama 3. You are participating in a debate. You firmly believe that critical thinking is the most important skill. Defend your position logically and concisely (max 2 paragraphs per response).",
    human_input_mode="NEVER"
)

mixtral_agent = autogen.ConversableAgent(
    name="Mixtral_Debater",
    llm_config=llm_config_mixtral,
    system_message="You are Mixtral. You are participating in a debate. You firmly believe that adaptability and continuous learning are the most important skills. Defend your position logically and concisely (max 2 paragraphs per response).",
    human_input_mode="NEVER"
)

# Start the debate
topic = "What is the most important skill for a software engineer in the age of AI?"
print(f"Starting debate on topic: {topic}\n")

chat_result = llama_agent.initiate_chat(
    mixtral_agent,
    message=topic,
    max_turns=2
)
