import requests
import os
import json


def llm_request(messages):
    
    LLM_API = os.environ.get("LLM_BASE_URL")
    url = "{}/v1/chat/completions".format(LLM_API)
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "model": "/gemma-3-1b-it-model",
        "messages": messages
    }
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        content = response.json()["choices"][0]["message"]["content"]
        if "```" in content:
            content = content.replace("```json","")
            content = content.replace("```","")
        return content
    else:
        print("Request failed with status:", response.status_code)
        return response.text


def prompt_llm(prompt):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a JSON generator for network automation workflows. Always return a JSON array with "
                "exactly two actions: collect and parse. Only include the commands mentioned in the user input. "
                "The collect action must include username, password, host, and commands."
                "The configure interface description action must include username, password, host, interface, and description."
                "Do not invent, add, or infer extra commands."
            )
        }
    ]
    for prompts_file in [
        "collect-prompts.json",
        "configure-interface-description-prompts.json"
    ]:
        with open(os.path.join("prompts",prompts_file),"r") as f:
            prompt_data = json.loads("\n".join(f.readlines()))
            messages += prompt_data 
    messages += [
        {
            "role": "user",
            "content": prompt.strip()
        }
    ]
    return llm_request(messages)
