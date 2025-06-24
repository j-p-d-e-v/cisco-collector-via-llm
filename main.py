import os
from paramiko.client import SSHClient
import paramiko
import textfsm
import requests
import json
from colorama import Fore, Style

parsers = {
    "show version": "templates/show_version.textfsm",
    "show clock": "templates/show_clock.textfsm",
    "show arp": "templates/show_arp.textfsm",
}

def send_prompt(prompt):
    
    LLM_API = os.environ.get("LLM_BASE_URL")
    url = "{}/v1/chat/completions".format(LLM_API)
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "model": "/gemma-3-1b-it-model",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a JSON generator for network automation workflows. Always return a JSON array with "
                    "exactly two actions: collect and parse. Only include the commands mentioned in the user input. "
                    "The collect action must include username, password, host, and commands. The parse action must include "
                    "the exact same commands. Do not invent, add, or infer extra commands."
                )
            },
            {
                "role": "user",
                "content": "Collect show version and show clock from 10.10.10.1 with username admin and password router123"
            },
            {
                "role": "assistant",
                "content": "[{\"action\": \"collect\", \"username\": \"admin\", \"password\": \"router123\", \"host\": \"10.10.10.1\", \"commands\": [\"show version\", \"show clock\"]} ]"
            },
            {
                "role": "user",
                "content": "Collect show version, show arp, and show clock from 10.10.10.1 with username admin and password router123"
            },
            {
                "role": "assistant",
                "content": "[{\"action\": \"collect\", \"username\": \"admin\", \"password\": \"router123\", \"host\": \"10.10.10.1\", \"commands\": [\"show version\",\"show arp\", \"show clock\"]} ]"
            },
            {
                "role": "user",
                "content": prompt  # This is your dynamic input
            }
        ]
    }
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        content = response.json()["choices"][0]["message"]["content"]
        return content
    else:
        print("Request failed with status:", response.status_code)
        print(response.text)

def parse(command,output):
    template_path = parsers.get(command)
    if template_path == None:
        raise Exception("template path for this command {} not found".format(command))
    
    with open(template_path) as template_file:
        fsm = textfsm.TextFSM(template_file)
        parsed_results = fsm.ParseText(output)
        structured_data = [dict(zip(fsm.header, row)) for row in parsed_results]
        return structured_data

def collect(client, command, hostname,username,password):
    client.connect(hostname=hostname, port=22,username=username, password=password, banner_timeout=600)
    _, output, _ = client.exec_command(command)
    return output.read().decode()

def main():
    
    SANDBOX_HOST = os.environ.get("SANDBOX_HOST")
    SANDBOX_USERNAME = os.environ.get("SANDBOX_USERNAME")
    SANDBOX_PASSWORD = os.environ.get("SANDBOX_PASSWORD")
    #SANDBOX_PORT = os.environ.get("SANDBOX_PORT")
    prompt = "Collect show clock, show route ipv4, show arp, show run interface, and show version from {} with username {} and password {}".format(SANDBOX_HOST,SANDBOX_USERNAME,SANDBOX_PASSWORD)
    output = send_prompt(prompt)
    print("{}PROMPT:\n{}{}".format(Fore.RED,prompt,Style.RESET_ALL))
    if "```" in output:
        output = output.replace("```json","")
        output = output.replace("```","")
    instructions = json.loads(output)
    print("{}INSTRUCTION: {}{}".format(Fore.BLUE,json.dumps(instructions, indent=4),Style.RESET_ALL))
    client = SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print("{}EXECUTING COLLECTION{}".format(Fore.CYAN,Style.RESET_ALL))    
    for item in instructions:
        if item["action"] == "collect":
            hostname = item["host"]
            username = item["username"]
            password = item["password"]
            for command in item["commands"]:
                print("{}COLLECTING: {}{}".format(Fore.GREEN,command,Style.RESET_ALL))  
                command_output = collect(client,command,hostname=hostname,username=username,password=password)                
                print("{}COMMAND OUTPUT: {}\n{}{}".format(Fore.YELLOW,command, command_output,Style.RESET_ALL))  
                try:
                    parsed_output = parse(command,command_output)
                    print("{}COMMAND PARSER OUTPUT: {}\n{}{}".format(Fore.MAGENTA,command, json.dumps(parsed_output,indent=4),Style.RESET_ALL))  
                except Exception as e:
                    print("{}COMMAND PARSER ERROR: {} {}".format(Fore.RED,str(e),Style.RESET_ALL)) 

main()