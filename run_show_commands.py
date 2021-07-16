# ############################################     PARAMETERS    #######################################################
# Fill in variables below. Username, password, and enable password.
# Use text file switches.txt and paste in ip addresses of the devices. One per line.
# Alternatively, comment out lines 14-16 and uncomment line 17 instead, if number of devices is relatively small.
# Use command_file variable for config lines. Line 18.
# Alternatively, comment out line 18 and uncomment lines 19-21 to specify configs.txt file with lots of configurations.
# One config line per text line inside configs.txt file.
# By default, only cisco platform is supported.
# ######################################################################################################################
user = 'cisco'
password = 'cisco'
enable_password = 'cisco'
# ######################################################################################################################
switchhosts = 'switches.txt'
with open(switchhosts) as f:
    switchhosts = f.read().splitlines()
# switchhosts = ['192.168.56.40', '192.168.56.48']
command_file = ['show ip route', 'show ip ospf nei']
# command_file = 'configs.txt'
# with open(command_file) as g:
#     command_file = g.read().splitlines()
# ######################################################################################################################
platform = 'cisco_ios'
errors = []


def netmiko_show_commands(usr, passw, en_passw, swh, plat, comm):
    from netmiko import ConnectHandler
    print("CONFIG FILES: ")
    print(command_file)
    print("SWITCHES IN THE HOSTS FILE: ")
    print(swh)
    for host in swh:
        print("ESTABLISHING SSH SESSION TO SWITCH: " + str(host))
        try:
            net_connect = ConnectHandler(device_type=plat,
                                         ip=host, username=usr,
                                         password=passw,
                                         secret=en_passw,
                                         )
            net_connect.enable()
            for commandset in comm:
                commandset = commandset.strip()
                print(commandset)
                saveoutput = open(host + "_show_commands.txt", "a")
                saveoutput.write("\n" + "\n" + commandset + "\n")
                output = net_connect.send_command(commandset)
                print(output)
                readoutput = output
                saveoutput.write(readoutput)
                saveoutput.write("\n")
        except:
            errors.append(host)


def tellib_show_commands(usr, passw, en_passw, swh, comm):
    import telnetlib
    incr = 0
    for host in swh:
        host = host.strip()
        try:
            tn = telnetlib.Telnet(host)
            tn.read_until(b"Username: ")
            tn.write(usr.encode('ascii') + b"\n")
            if password:
                tn.read_until(b"Password: ")
                tn.write(passw.encode('ascii') + b"\n")
                tn.write(b"enable\n")
                tn.write(en_passw.encode('ascii') + b"\n")
                tn.write(b"terminal length 0\n")
                print("READING " + host)
                print("===============")
                print("===============")
                print("===============")
                for x in comm:
                    x = x.strip()
                    print(x)
                    output = tn.write(x.encode('ascii') + b"\n")
            incr = incr + 1
            tn.write(b"terminal length 24\n")
            tn.write(b"exit\n")
            # print(tn.read_all().decode('ascii'))
            saveoutput = open(host + "_show_commands.txt", "a")
            readoutput = tn.read_all().decode('ascii')
            saveoutput.write(readoutput)
            saveoutput.write("\n")
        except:
            errors.append(host)


netmiko_show_commands(user, password, enable_password, switchhosts, platform, command_file)
# tellib_show_commands(user, password, enable_password, switchhosts, command_file)

for e in errors:
    print("##############################################")
    print("ERRORS WERE FOUND ON THIS HOST: " + e)
