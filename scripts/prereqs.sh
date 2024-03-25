sudo apt install pip -y
python3 -m pip install --user ansible
pip3 install openshift pyyaml kubernetes
export PATH=$PATH:/home/${USER}/.local/bin
sudo usermod -aG docker $USER && newgrp docker
ansible-galaxy collection install kubernetes.core
ansible-galaxy role install --roles-path=ansible/playbooks/roles geerlingguy.docker
ansible-galaxy role install --roles-path=ansible/playbooks/roles gantsign.minikube
ansible-galaxy role install --roles-path=ansible/playbooks/roles robertdebock.kubectl

ansible-playbook ansible/playbooks/install_roles.yml -i ansible/inventory/hosts
ansible-playbook ansible/playbooks/testbook.yml -i ansible/inventory/hosts
