sudo apt install pipx -y
pipx install --include-deps ansible
ansible-galaxy collection install community.docker
ansible-galaxy collection install community.kubernetes
ansible-galaxy role install geerlingguy.docker
ansible-galaxy role install gantsign.minikube
ansible-galaxy role install robertdebock.kubectl
