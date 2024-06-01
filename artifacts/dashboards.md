# Accessing Dashboards
First, to interact with the cluster on the target VM execute the command: 

`mkdir -p $HOME/.kube && sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config && sudo chown $(id -u):$(id -g) $HOME/.kube/config`


## Prometheus with Grafana Dashboard
### Target VM
To access the Prometheus with Grafana dashboard, run the following command in the terminal of the target VM:

`kubectl port-forward svc/prometheus-operator-grafana -n monitoring 8080:80`

### Host Machine
Then, run the following command in the terminal of the local machine:

`ssh -L 3000:localhost:8080 USERNAME@TARGET_VM_IP`

to access Prometheus with Grafana Dashboard localhost:3000 in browser with:

username: admin

password: prom-operator


## Chaos Mesh Dashboard
### Target VM
To access the Chaos Mesh Dashboard and to execute chaos in the cluster run the following commands on the target VM:

`helm repo add chaos-mesh https://charts.chaos-mesh.org`

`kubectl create ns chaos-mesh`

`helm install chaos-mesh chaos-mesh/chaos-mesh -n=chaos-mesh --version 2.6.3`

`kubectl port-forward svc/chaos-dashboard -n chaos-mesh 8080:2333`

If you want to start chaos:

`kubectl apply -f k8s-manifests/chaos.yaml`


### Host Machine
Then, run the following command in the terminal of the local machine:

`ssh -L 3000:localhost:8080 USERNAME@TARGET_VM_IP`

Then, follow the instructions from the instructions at localhost:3000 in browser.