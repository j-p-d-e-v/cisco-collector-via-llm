from paramiko.client import SSHClient
import paramiko
import json
import time
from colorama import Fore, Style
from llm import prompt_llm
from parsers import parse
from functions import execute_command, configure_interface_description


def prepare_output(action,data):
    return {
        "action": action,
        "data": data
    }

def send_prompt(prompt):
    print("{}TRAINING LLM{}".format(Fore.YELLOW,Style.RESET_ALL))
    output = prompt_llm(prompt)
    print("{}PROMPT:\n{}{}".format(Fore.RED,prompt,Style.RESET_ALL))
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
            collection_data = []
            for command in item["commands"]:
                print("{}COLLECTING: {}{}".format(Fore.GREEN,command,Style.RESET_ALL))
                result = {
                    "raw": "",
                    "parsed": "",
                    "error":""
                }
                while True:
                    try:  
                        result["raw"] = execute_command(client,command,hostname=hostname,username=username,password=password)                
                        print("{}COMMAND OUTPUT: {}\n{}{}".format(Fore.YELLOW,command, result["raw"],Style.RESET_ALL))  
                        break
                    except Exception as e:
                        print("{}COMMAND EXECUTION ERROR: {}\n{}{}".format(Fore.RED,command, str(e),Style.RESET_ALL))  
                try:
                    result["parsed"] = parse(command,result["raw"])
                    print("{}COMMAND PARSER OUTPUT: {}\n{}{}".format(Fore.MAGENTA,command, json.dumps(result["parsed"],indent=4),Style.RESET_ALL))  
                except Exception as e:
                    result["error"] = str(e)
                    print("{}COMMAND PARSER ERROR: {} {}".format(Fore.RED,str(e),Style.RESET_ALL)) 
                collection_data.append(result)
            return prepare_output(item["action"],collection_data)
        elif item["action"] == "configure-interface-description":
            hostname = item["host"]
            username = item["username"]
            password = item["password"]
            interface = item["interface"]
            description = item["description"]
            config_output = configure_interface_description(client, interface, description, hostname,username,password)
            return prepare_output(item["action"],config_output)
        else:
            return prepare_output("error","invalid action")