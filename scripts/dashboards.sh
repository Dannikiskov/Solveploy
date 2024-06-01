# Prometheus with Grafana Dashboard acces on localhost:3000
# Target VM
kubectl port-forward svc/prometheus-operator-grafana -n monitoring 8080:80

# Host Machine
ssh -L 3000:localhost:8080 USERNAME@TARGET_VM_IP
username: admin, password: prom-operator


# Chaos Mesh Dashboard acces on localhost:3000
# Target VM
kubectl port-forward svc/chaos-dashboard -n chaos-mesh 8080:2333

# Host Machine
ssh -L 3000:localhost:8080 USERNAME@TARGET_VM_IP

# To start chaos
kubectl apply -f k8s-manifests/chaos.yaml