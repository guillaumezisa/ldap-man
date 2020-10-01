#!/usr/bin/env python3
# Guillaume Zisa - 01/10/20 - v1.0
# This script help you to setup your client to communicate with the ldap server

import os
import getpass

# VARIABLES

whoami = getpass.getuser()

# FUNCTIONS

def header():
    print("=========================================================================")
    print("   ██╗     ██████╗  █████╗ ██████╗       ███╗   ███╗ █████╗ ███╗   ██╗")
    print("   ██║     ██╔══██╗██╔══██╗██╔══██╗      ████╗ ████║██╔══██╗████╗  ██║")
    print("   ██║     ██║  ██║███████║██████╔╝█████╗██╔████╔██║███████║██╔██╗ ██║")
    print("   ██║     ██║  ██║██╔══██║██╔═══╝ ╚════╝██║╚██╔╝██║██╔══██║██║╚██╗██║")
    print("   ███████╗██████╔╝██║  ██║██║           ██║ ╚═╝ ██║██║  ██║██║ ╚████║")
    print("   ╚══════╝╚═════╝ ╚═╝  ╚═╝╚═╝           ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝")
    print("=========================================================================")

def install():
    os.system("apt install libnss-ldap -y")
    os.system("sed -i 's/passwd:         files systemd/passwd:         files systemd ldap/g' /etc/nsswitch.conf")
    os.system("sed -i 's/group:          files systemd/group:          files systemd ldap/g' /etc/nsswitch.conf")
    os.system("sed -i 's/shadow:         files/shadow:         files ldap/g' /etc/nsswitch.conf")
    os.system("sed -i 's/gshadow:        files/gshadow:        files ldap/g' /etc/nsswitch.conf")

def reconfigure():
    os.system("dpkg-reconfigure libnss-ldap -y")

def main_loop():
    if whoami == "root":
        while True:
            header()
            print("     [0] - Install")
            print("     [1] - Reconfigure")
            choice = input("     Enter your choice : ")
            if choice == "0":
                print("Install")
                install()
                input("Press enter to continue ...")
            elif choice == "1":
                print("Reconfigure")
                reconfigure()
                input("Press enter to continue ...")
    else:
        print("You have to be root")

main_loop()