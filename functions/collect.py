def execute_command(client, command, hostname,username,password):
    client.connect(hostname=hostname, port=22,username=username, password=password, banner_timeout=60)
    _, output, _ = client.exec_command(command)
    return output.read().decode()