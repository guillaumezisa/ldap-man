#!/usr/bin/env python3
# Guillaume Zisa - 01/10/20 - v1.0
# This script help you to install and manage your ldap serveur
import os
import getpass

#CONSTANTS

DOMAIN_NAME = ""
HOST_NAME = ""
IP = ""

#VARIABLES
dc = DOMAIN_NAME.split(".")
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
    if whoami == "root":
        os.system("apt install slapd")
        os.system("echo '"+IP+" "+HOST_NAME+"."+DOMAIN_NAME+"' | sudo tee -a /etc/hosts")
        os.system("hostnamectl set-hostname "+HOST_NAME+"."+DOMAIN_NAME+" --static")
        os.system("apt update -y")
        os.system("apt upgrade -y")
        os.system("apt install slapd -y")
        os.system("dpkg-reconfigure slapd ") 
        os.system("apt install ldap-utils libnss-ldap -y")
        os.system("mkdir -p /etc/ssl/openldap/private")
        os.system("mkdir -p /etc/ssl/openldap/certs")
        os.system("mkdir -p /etc/ssl/openldap/newcerts")
        os.system("cp /usr/lib/ssl/openssl.cnf /usr/lib/ssl/openssl.cnf.default")
        os.system("sed -i 's/.\/demoCA/\/etc\/ssl\/openldap/g' /usr/lib/ssl/openssl.cnf")
        os.system("echo '1001' > /etc/ssl/openldap/serial")
        os.system("touch /etc/ssl/openldap/index.txt")
        os.system("openssl genrsa -aes256 -out /etc/ssl/openldap/private/cakey.pem 2048")
        os.system("openssl rsa -in /etc/ssl/openldap/private/cakey.pem -out /etc/ssl/openldap/private/cakey.pem")
        os.system("openssl req -new -x509 -days 3650 -key /etc/ssl/openldap/private/cakey.pem -out /etc/ssl/openldap/certs/cacert.pem")
        os.system("openssl genrsa -aes256 -out /etc/ssl/openldap/private/ldapserver-key.key 2048")
        os.system("openssl rsa -in /etc/ssl/openldap/private/ldapserver-key.key -out /etc/ssl/openldap/private/ldapserver-key.key")
        os.system("openssl req -new -key /etc/ssl/openldap/private/ldapserver-key.key -out /etc/ssl/openldap/certs/ldapserver-cert.csr")
        os.system("openssl ca -keyfile /etc/ssl/openldap/private/cakey.pem -cert /etc/ssl/openldap/certs/cacert.pem -in /etc/ssl/openldap/certs/ldapserver-cert.csr -out /etc/ssl/openldap/certs/ldapserver-cert.crt")
        os.system("openssl verify -CAfile /etc/ssl/openldap/certs/cacert.pem /etc/ssl/openldap/certs/ldapserver-cert.crt")
        os.system("chown -R openldap: /etc/ssl/openldap/")
        ldif = ["dn: cn=config",
                "changetype: modify",
                "add: olcTLSCACertificateFile",
                "olcTLSCACertificateFile: /etc/ssl/openldap/certs/cacert.pem",
                "-",
                "replace: olcTLSCertificateFile",
                "olcTLSCertificateFile: /etc/ssl/openldap/certs/ldapserver-cert.crt",
                "-",
                "replace: olcTLSCertificateKeyFile",
                "olcTLSCertificateKeyFile: /etc/ssl/openldap/private/ldapserver-key.key"
                ]
        for i in range(len(ldif)):
            os.system("echo "+ldif[i]+" >> /etc/ldap/ldap-tls.ldif")
        os.system("ldapmodify -Y EXTERNAL -H ldapi:/// -f /etc/ldap/ldap-tls.ldif")
        os.system("cp /etc/ldap/ldap.conf /etc/ldap/ldap.conf.default") 
        os.system("sed -i 's/\/etc\/ssl\/certs\/ca-certificates.crt/\/etc\/ssl\/openldap\/certs\/cacert.pem/g' /etc/ldap/ldap.conf")   
        ldif = ["dn: cn=config",
                "changeType: modify",
                "replace: olcLogLevel",
                "olcLogLevel: stats"
                ]
        for i in range(len(ldif)):
            os.system("echo "+ldif[i]+" >> /etc/ldap/ldap_logs.ldif")
        os.system("ldapmodify -Y EXTERNAL -H ldapi:/// -f /etc/ldap/ldap_logs.ldif")
        os.system("rm /etc/ldap/ldap_logs.ldif")
        os.system("systemctl restart slapd")
    else:
        print("You have to be root")

def reconfigure():
    if whoami == "root":
        os.system("dpkg-reconfigure slapd ")
        os.system("dpkg-reconfigure libnss-ldap ") 
    else:
        print("You have to be root")

def add_group():
    groupname = input("Enter the name of the new group : ")
    ldif = [
            "dn: ou="+groupname+",dc="+dc[0]+",dc="+dc[1],
            "objectClass: organizationalUnit",
            "ou: "+groupname
            ]
    for i in range(len(ldif)):
        os.system("echo "+ldif[i]+ ">> /etc/ldap/add_group.ldif")
    os.system("ldapadd -D 'cn=admin,dc="+dc[0]+",dc="+dc[1]+"' -W -H ldapi:/// -f /etc/ldap/add_group.ldif")
    os.system("rm /etc/ldap/add_group.ldif")

def add_user():
    username =  input("     Name of the new user: ")
    groupname = input("     Name of the group: ")    
    uidnumber = input("     UID: ")
    while True:
        password = input("New user password: ")
        password2 = input("Again New user password: ")
        if password == password2:
            break

    ldif = ["dn: cn="+username+",ou="+groupname+",dc="+dc[0]+",dc="+dc[1],
            "objectClass: top",
            "objectClass: account",
            "objectClass: posixAccount",
            "objectClass: shadowAccount",
            "cn: "+username,
            "uid: "+username,
            "uidNumber: "+uidnumber,
            "gidNumber: "+uidnumber,
            "homeDirectory: /home/"+username,
            "userPassword: "+password,
            "loginShell: /bin/bash"
        ]
    for i in range(len(ldif)):
        os.system("echo "+ldif[i]+ ">> /etc/ldap/add_user.ldif")
    os.system("ldapadd -D 'cn=admin,dc="+dc[0]+",dc="+dc[1]+"' -W -H ldap:/// -f /etc/ldap/add_user.ldif")
    os.system("rm /etc/ldap/add_user.ldif")

def del_user():
    user_name = input("      Name of the user to remove: ")
    user_group = input("     Group of the user to remove: ")

    ldif=[
            "dn: cn="+user_name+",ou="+user_group+",dc="+dc[0]+",dc="+dc[1],
            "changeType: delete",
        ]

    for i in range(len(ldif)):
        os.system("echo "+ldif[i]+ ">> /etc/ldap/del_user.ldif")
    os.system("ldapmodify -D 'cn=admin,dc="+dc[0]+",dc="+dc[1]+"' -W -H ldap:/// -f /etc/ldap/del_user.ldif")
    os.system("rm /etc/ldap/del_user.ldif")

def del_group():
    groupname = input("     Group to remove: ")
    ldif=[
        "dn: cn="+groupname+",ou="+groupname+",dc="+dc[0]+",dc="+dc[1],
        "changetype: delete"
        ]
    for i in range(len(ldif)):
        os.system("echo "+ldif[i]+ ">> /etc/ldap/del_group.ldif")
    #os.system("ldapdelete -x -W -H ldap:/// -D 'cn=admin,dc="+dc[0]+",dc="+dc[1]+"' ou="+groupname+",dc="+dc[0]+",dc="+dc[1]+")
    os.system("rm /etc/ldap/del_group.ldif")

# MENU
def main_loop():
    while True:
        header()
        print("     [0] - Install")
        print("     [1] - Reconfigure")
        print("     [2] - Display conf")
        print("     [3] - Display Groups")
        print("     [4] - Display Users")
        print("     [5] - Add Group")
        print("     [6] - Add User")
        print("     [7] - Remove Group (not working)")
        print("     [8] - Remove User")
        choice = input("     Enter your choice : ")
        if choice == "0":
            print("Install")
            install()
            input("Press enter to continue ...")
        elif choice == "1":
            print("Reconfigure")
            reconfigure()
            input("Press enter to continue ...")
        elif choice == "2":
            os.system("slapcat")
            input("Press enter to continue ...")
        elif choice == "3":
            os.system("ldapsearch -x -b 'dc="+dc[0]+",dc="+dc[1]+"' ou")
            input("Press enter to continue ...")
        elif choice == "4":
            groupname = input("     Enter groupname : ")
            os.system("ldapsearch -x -b 'dc="+dc[0]+",dc="+dc[1]+"' users")
            input("Press enter to continue ...")
        elif choice == "5":
            print("Adding group")
            add_group()
            input("Press enter to continue ...")
        elif choice == "6":
            print("Adding user")
            add_user()
            input("Press enter to continue ...")
        elif choice == "7":
            print("Remove Group")
            del_group()
            input("Press enter to continue ...")
        elif choice == "8":
            print("Remove user")
            del_user()
            input("Press enter to continue ...")

main_loop()