# ############################################     PARAMETERS    #######################################################
# Fill in variables below. Username, password, and enable password. Script supports different usernames and passwords
# across devices. For telnet, it is able to detect whether Username has been set, or password only.
# Use text file switches.txt and paste in ip addresses of the devices. One per line.
# Alternatively, comment out lines 15-17 and uncomment line 14 instead, if number of devices is relatively small.
# Use command_file variable for config lines. Line 19.
# Alternatively, comment out line 19 and uncomment lines 20-22 to specify configs.txt file with lots of configurations.
# One config line per text line inside configs.txt file.
# By default, only cisco platform is supported.
# To use telnet comment out line 154 (disable ssh), and uncomment line 155
# ######################################################################################################################
user = ['cisco', 'kisco']
password = ['cisco', 'password']
enable_password = ['cisco', 'password']
# ######################################################################################################################
# switchhosts = ['192.168.56.48', '192.168.56.55']
switchhosts = 'switches.txt'
with open(switchhosts) as f:
    switchhosts = f.read().splitlines()
# ######################################################################################################################
command_file = ['show ip route', 'show ip ospf nei']
# command_file = 'configs.txt'
# with open(command_file) as g:
#     command_file = g.read().splitlines()
# ######################################################################################################################
prompt_list = [b'Username: ', b'Password: ']
platform = 'cisco_ios'
authentication_errors = []
errors = []


def netmiko_find_password(usr, passw, en_passw, swh, plat):
    from netmiko import ConnectHandler
    from paramiko.ssh_exception import AuthenticationException
    for u in usr:
        for p in passw:
            for ep in en_passw:
                try:
                    net_connect = ConnectHandler(device_type=plat, ip=swh, username=u, password=p, secret=ep)
                    net_connect.enable()
                    print("Authentication Success!" + " - " + swh + ": " + u + "/" + p + "/" + ep)
                    return net_connect
                except:
                    if AuthenticationException:
                        authentication_errors.append("Authentication Failure" + " - " + swh + ": " + u + "/" +
                                                     p + "/" + ep)
                    else:
                        errors.append(swh)
    print("##################################################")


def tellib_find_password(ls, usr, pasw, en_pasw, swh):
    import telnetlib
    import re
    tn = telnetlib.Telnet(swh)
    auth = tn.expect(ls)
    prompt_parser = re.compile(r'Username:|Password:')
    prompt_type = prompt_parser.search(auth[1].group(0).decode('ascii'))
    tn.close()
    if prompt_type[0] == 'Password:':
        for p in pasw:
            tn = telnetlib.Telnet(swh)
            tn.read_until(b"Password: ")
            tn.write(p.encode('ascii') + b"\n")
            try:
                response = tn.read_until(b">", timeout=1)
            except EOFError as e:
                print("Connection closed: %s" % e)
            if b">" in response:
                tn.write(b"enable\n")
                for ep in en_pasw:
                    tn.write(ep.encode('ascii') + b"\n")
                    try:
                        response = tn.read_until(b"#", timeout=1)
                    except EOFError as e:
                        print("Connection closed: %s" % e)
                    if b"#" in response:
                        return tn

    elif prompt_type[0] == 'Username:':
        for u in usr:
            for p in pasw:
                tn = telnetlib.Telnet(swh)
                tn.read_until(b"Username: ")
                tn.write(u.encode('ascii') + b"\n")
                tn.read_until(b"Password: ")
                tn.write(p.encode('ascii') + b"\n")
                try:
                    response = tn.read_until(b">", timeout=1)
                except EOFError as e:
                    print("Connection closed: %s" % e)
                if b">" in response:
                    tn.write(b"enable\n")
                    for ep in en_pasw:
                        tn.write(ep.encode('ascii') + b"\n")
                        try:
                            response = tn.read_until(b"#", timeout=1)
                        except EOFError as e:
                            print("Connection closed: %s" % e)
                        if b"#" in response:
                            return tn


def netmiko_show_commands(usr, passw, en_passw, swh, plat, comm):
    print("CONFIG FILES: ")
    print(command_file)
    print("SWITCHES IN THE HOSTS FILE: ")
    print(swh)
    for host in swh:
        print("##############################################")
        print("ESTABLISHING SSH SESSION TO SWITCH: " + str(host))
        try:
            net_connect = netmiko_find_password(usr, passw, en_passw, host, plat)
            for commandset in comm:
                commandset = commandset.strip()
                print(commandset)
                saveoutput = open(host + "_show_commands.txt", "a")
                saveoutput.write("\n" + "\n" + commandset + "\n")
                output = net_connect.send_command(commandset)
                print(output)
                # readoutput = output
                saveoutput.write(output)
                saveoutput.write("\n")
        except:
            errors.append(host)


def tellib_show_commands(usr, passw, en_passw, swh, comm):
    incr = 0
    for host in swh:
        host = host.strip()
        try:
            tn = tellib_find_password(prompt_list, usr, passw, en_passw, host)
            tn.write(b"terminal length 0\n")
            print("===============")
            print("READING " + host)
            print("===============")
            for x in comm:
                x = x.strip()
                print(x)
                tn.write(x.encode('ascii') + b"\n")
            incr = incr + 1
            tn.write(b"terminal length 24\n")
            tn.write(b"exit\n")
            saveoutput = open(host + "_show_commands.txt", "a")
            readoutput = tn.read_all().decode('ascii')
            saveoutput.write(readoutput)
            saveoutput.write("\n")
            print(readoutput)
        except:
            errors.append(host)


# ############################################     PARAMETERS    #######################################################
netmiko_show_commands(user, password, enable_password, switchhosts, platform, command_file)
# tellib_show_commands(user, password, enable_password, switchhosts, command_file)
# ######################################################################################################################

for e in errors:
    print("##############################################")
    print("ERRORS WERE FOUND ON THIS HOST: " + e)
for a in authentication_errors:
    print("##############################################")
    print(a)
