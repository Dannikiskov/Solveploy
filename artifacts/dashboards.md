# Prometheus with Grafana Dashboard
## Target VM
To access the Prometheus with Grafana dashboard, run the following command in the terminal of the target VM:
`kubectl port-forward svc/prometheus-operator-grafana -n monitoring 8080:80`

# Host Machine
Then, run the following command in the terminal of the local machine:
`ssh -L 3000:localhost:8080 USERNAME@TARGET_VM_IP`
to access Prometheus with Grafana Dashboard localhost:3000 with:
username: admin
password: prom-operator