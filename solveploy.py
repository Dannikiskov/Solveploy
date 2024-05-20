import subprocess
import sys

file_path = "./ansible/inventory/hosts"

if sys.argv[1] == "--help":
    print("Usage:\n \t python3 solveploy.py target_ip target_username\n")
    exit()

host = sys.argv[1] if len(sys.argv) > 1 else input("Host: ").strip()
user = sys.argv[2] if len(sys.argv) > 2 else "ucloud"



content = f'''[kubernetes_hosts]
target_vm ansible_host={host} ansible_user={user}
'''
with open(file_path, "w") as file:
    file.write(content)
    file.close()

command = "ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook ansible/playbooks/dep_prod.yml -i ansible/inventory/hosts"
subprocess.run(command, shell=True)