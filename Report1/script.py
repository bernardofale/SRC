import paramiko
import sys

try:
    # Connect to the device using SSH
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect("192.1.1.1", username="vyos", password="vyos")
    
    with open("ip_list.txt", "r") as f:
        ips = [line.strip() for line in f]

    for ip in ips:
        ssh.exec_command("configure")
        ssh.exec_command("set policy access-list 100 rule 11 action deny")
        ssh.exec_command("set policy access-list 100 rule 11 destionation any")
        ssh.exec_command("set policy access-list 100 rule 11  source host 200.32.43.4")
        ssh.exec_command("commit")
        ssh.exec_command("save")
        ssh.exec_command("exit")
    # Close the SSH connection
    ssh.close()
	
    # Empty the file
    with open("ip_list.txt", "w") as f:
        f.write("")

except paramiko.AuthenticationException:
	print(f"Failed to connect to {ip}: authentication failed")
except paramiko.SSHException as e:
	print(f"Failed to connect to {ip}: {e}")

