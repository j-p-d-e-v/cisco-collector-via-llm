import textfsm

parsers = {
    "show version": "templates/show_version.textfsm",
    "show clock": "templates/show_clock.textfsm",
    "show arp": "templates/show_arp.textfsm",
}

def parse(command,output):
    template_path = parsers.get(command)
    if template_path == None:
        raise Exception("template path for this command {} not found".format(command))
    
    with open(template_path) as template_file:
        fsm = textfsm.TextFSM(template_file)
        parsed_results = fsm.ParseText(output)
        structured_data = [dict(zip(fsm.header, row)) for row in parsed_results]
        return structured_data