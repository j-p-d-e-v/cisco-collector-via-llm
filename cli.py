import json
from agent import send_prompt
def main():
    while True:
        prompt = input("Enter your prompt(Ctrl+C to exit): ")
        if len(prompt) == 0:
            continue
        output = send_prompt(prompt)
        print(json.dumps(output,indent=4))
        
main()