sudo apt install pipx
pipx install --include-deps ansible
ansible-galaxy role install --roles-path ansible/playbooks/roles geerlingguy.docker
ansible-galaxy role install --roles-path ansible/playbooks/roles gantsign.minikube
ansible-galaxy role install --roles-path ansible/playbooks/roles robertdebock.kubectl
