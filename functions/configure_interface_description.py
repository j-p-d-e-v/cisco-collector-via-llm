import time

def send_command(channel, cmd, pause=1):
    channel.send(cmd + '\n')
    time.sleep(pause)
    return channel.recv(9999).decode()

def configure_interface_description(client, interface, description, hostname,username,password):
    while True:
        try:
            client.connect(hostname=hostname, port=22,username=username, password=password, banner_timeout=60)
            break
        except Exception as e:
            client.close()
            if "Error reading SSH protocol banner" in str(e):
                continue
            else:
                raise Exception(str(e))
    
    channel = client.invoke_shell()
    time.sleep(5)
    channel.recv(9999)

    send_command(channel, 'configure terminal')
    send_command(channel, 'interface {}'.format(interface))
    send_command(channel, 'description {}'.format(description))

    output = send_command(channel, 'end', pause=2)

    print(output)
    if 'commit them before exiting' in output:
        send_command(channel, 'yes', pause=2)

    send_command(channel, 'commit')
    output = send_command(channel, 'show interfaces {}'.format(interface))

    channel.close()
    client.close()
    return output