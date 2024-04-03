sudo apt install pip -y
python3 -m pip install --user ansible
export PATH=$PATH:/home/${USER}/.local/bin
pip3 install openshift
pip3 install pyyaml
pip3 install kubernetes
ansible-galaxy collection install kubernetes.core --force
ansible-galaxy role install --roles-path=ansible/playbooks/roles geerlingguy.docker
ansible-galaxy role install --roles-path=ansible/playbooks/roles gantsign.minikube
ansible-galaxy role install --roles-path=ansible/playbooks/roles robertdebock.kubectl
ansible-playbook ansible/playbooks/install_roles.yml -i ansible/inventory/hosts
sudo usermod -aG docker $USER && newgrp docker
sudo systemctl start docker
ansible-playbook ansible/playbooks/testbook.yml -i ansible/inventory/hosts
