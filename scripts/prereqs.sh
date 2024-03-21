sudo apt install pipx -y
pipx install --include-deps ansible
ansible-galaxy collection install community.docker -p /ansible/collections
ansible-galaxy collection install community.kubernetes -p /ansible/collections
ansible-galaxy role install --roles-path ansible/playbooks/roles geerlingguy.docker
ansible-galaxy role install --roles-path ansible/playbooks/roles gantsign.minikube
ansible-galaxy role install --roles-path ansible/playbooks/roles robertdebock.kubectl
