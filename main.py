import os
from paramiko.client import SSHClient
import paramiko
import textfsm
import requests
import json
import time
from colorama import Fore, Style

parsers = {
    "show version": "templates/show_version.textfsm",
    "show clock": "templates/show_clock.textfsm",
    "show arp": "templates/show_arp.textfsm",
}

def interact_llm(prompt):
    
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
                    "The collect action must include username, password, host, and commands."
                    "The configure interface description action must include username, password, host, interface, and description."
                    "Do not invent, add, or infer extra commands."
                )
            },
            {
                "role": "user",
                "content": "Collect show version and show clock from 10.10.10.1 with username admin and password router123"
            },
            {
                "role": "assistant",
                "content": "[{\"action\": \"collect\", \"username\": \"admin\", \"password\": \"router123\", \"host\": \"10.10.10.1\", \"commands\": [\"show version\", \"show clock\"]}, ]"
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
                "content": "Configure Loopback1 interface description to \"this is my description\" of 10.10.10.1 with username admin and password router123"
            },
            {
                "role": "assistant",
                "content": "[\n  {\n    \"action\": \"configure-interface-description\",\n    \"username\": \"admin\",\n    \"password\": \"router123\",\n    \"host\": \"10.10.10.1\",\n    \"interface\": \"Loopback1\",\n    \"description\": \"this is my description\"\n  }\n]"
            },

            {
                "role": "user",
                "content": "Set interface GigabitEthernet0/1 description to \"Uplink to Core Switch\" on 192.168.0.1 using user netops and password cisco"
            },
            {
                "role": "assistant",
                "content": "[\n  {\n    \"action\": \"configure-interface-description\",\n    \"username\": \"netops\",\n    \"password\": \"cisco\",\n    \"host\": \"192.168.0.1\",\n    \"interface\": \"GigabitEthernet0/1\",\n    \"description\": \"Uplink to Core Switch\"\n  }\n]"
            },
            {
                "role": "user",
                "content": "Change description of interface Ethernet1/1 to \"Customer Edge\" on device 172.16.1.1 with username admin and password pass123"
            },
            {
                "role": "assistant",
                "content": "[\n  {\n    \"action\": \"configure-interface-description\",\n    \"username\": \"admin\",\n    \"password\": \"pass123\",\n    \"host\": \"172.16.1.1\",\n    \"interface\": \"Ethernet1/1\",\n    \"description\": \"Customer Edge\"\n  }\n]"
            },
            {
                "role": "user",
                "content": "On 10.0.0.1, configure Loopback0 with description \"Backup Tunnel\" using username sysadmin and password secret321"
            },
            {
                "role": "assistant",
                "content": "[\n  {\n    \"action\": \"configure-interface-description\",\n    \"username\": \"sysadmin\",\n    \"password\": \"secret321\",\n    \"host\": \"10.0.0.1\",\n    \"interface\": \"Loopback0\",\n    \"description\": \"Backup Tunnel\"\n  }\n]"
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

def send_command(channel, cmd, pause=1):
    channel.send(cmd + '\n')
    time.sleep(pause)
    return channel.recv(9999).decode()

def configure_interface_description(client, interface, description, hostname,username,password):
    client.connect(hostname=hostname, port=22,username=username, password=password, banner_timeout=600)
    config = """
        configure terminal
        interface GigabitEthernet0/1
        description Uplink to Core Switch
        end

    """
    channel = client.invoke_shell()
    time.sleep(1)
    channel.recv(9999)  # flush banner

    # Enter config mode
    send_command(channel, 'configure terminal')
    send_command(channel, 'interface {}'.format(interface))
    send_command(channel, 'description {}'.format(description))

    # Try exiting config mode — and answer 'yes' when asked
    output = send_command(channel, 'end', pause=2)

    if 'commit them before exiting' in output:
        send_command(channel, 'yes', pause=2)

    # Optionally save config if you want to persist to startup
    send_command(channel, 'commit')
    output = send_command(channel, 'show interfaces {}'.format(interface))

    channel.close()
    client.close()
    return output

def send_promp(prompt):
    output = interact_llm(prompt)
    print("{}PROMPT:\n{}{}".format(Fore.RED,prompt,Style.RESET_ALL))
    if "```" in output:
        output = output.replace("```json","")
        output = output.replace("```","")
    instructions = json.loads(output)
    print("{}INSTRUCTION: {}{}".format(Fore.BLUE,json.dumps(instructions, indent=4),Style.RESET_ALL))
    client = SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print("{}EXECUTING INSTRUCTION{}".format(Fore.CYAN,Style.RESET_ALL))    
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
        elif item["action"] == "configure-interface-description":
            hostname = item["host"]
            username = item["username"]
            password = item["password"]
            interface = item["interface"]
            description = item["description"]
            config_output = configure_interface_description(client, interface, description, hostname,username,password)
            print(config_output)
def main():
    
    SANDBOX_HOST = os.environ.get("SANDBOX_HOST")
    SANDBOX_USERNAME = os.environ.get("SANDBOX_USERNAME")
    SANDBOX_PASSWORD = os.environ.get("SANDBOX_PASSWORD")
    #SANDBOX_PORT = os.environ.get("SANDBOX_PORT")
    prompt = "Collect show clock, show route ipv4, show arp, show run interface, and show version from {} with username {} and password {}".format(SANDBOX_HOST,SANDBOX_USERNAME,SANDBOX_PASSWORD)
    send_promp(prompt)
    prompt = "Configure Loopback1 interface description to \"hello cisco ai 123\" of {} with username {} and password {}".format(SANDBOX_HOST,SANDBOX_USERNAME,SANDBOX_PASSWORD)
    send_promp(prompt)
main()