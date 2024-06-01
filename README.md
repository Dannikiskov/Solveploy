# Solveploy
Easy cloud deployment of Minizinc, SAT and MAXSAT solvers

## Prerequisites

* Ansible installed and added to PATH with role darkwizard242.helm installed and collection kubernetes.core installed.
* Python3 install with packages openshift, pyyaml, and kubernetes installed.
* To deploy locally, docker must be installed.
* SSH access to target (debian) virtual machine.
* ngrok free account claimed domain, authtoken and api-key.

## To deploy on Target virtual machine:

* Change value of private_key_file in ansible/ansible.cfg to filepath to private key.
* Add ngrok authtoken, api-key and domain values to .environmentals.json
* To deploy on debian virtual machine, execute command `solveploy VIRTUAL_MACHINE_IP --target-username USERNAME`
  
     username is 'ucloud' unless specified by flag.

When deployment has concluded, Solveploy is accesible on ngork domain.

## To deploy locally
execute command `solveploy --dev` and enter password when prompted.
