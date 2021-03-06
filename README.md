# cisco-cli-show-commands

Summary:

Purpose of this script is to run show commands on multiple Cisco devices. For example: pulling routing table and ospf neighbors
from multiple routers. SSH enabled by default. Telnet is supported.
This was tested primarily in virtual Cisco environment and might have different effect on specific physical Cisco models.


Requirements:

1) Interpreter: Python 3.8.0+
2) Python Packages: telnetlib, netmiko, paramiko, re

How to run:

1) Open run_show_commands.py file with a text editor of your choice. Replace example configurations in the PARAMETERS
   section. Lines 12-24. By default, ip addresses must be added to switches.txt file, one per line in the same directory
   with the script. Uncomment line 16, and comment out lines 17-19 to use small list of ip addresses. Small set of 
   commands can be applied at line 21, or use lines 22-24 to specify configs.txt file (has to be in the same directory 
   with the script).
   

2) By default, script will use SSH to establish connection. Telnet is supported.
    1) To disable SSH, comment out Line 155.
    2) To enable Telnet, uncomment Line 156.
   

3) Run python3 run_show_commands.py in the terminal. Output will be saved in <ip_address>_show_commands.txt files in the 
   same directory from which script was initiated.