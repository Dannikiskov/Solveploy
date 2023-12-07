#!/bin/bash
start_time=$(date +%s)
minikube start --cpus=4 --memory=8000

eval $(minikube docker-env)

kubectl apply -f kubernetes-deployments/rabbitmq-operator.yaml
kubectl apply -f kubernetes-deployments/rabbitmq-definition.yaml

docker build -t frontend -f services/frontend/Dockerfile services/frontend/
docker build -t api-gateway -f services/api-gateway/Dockerfile services/api-gateway/
docker build -t solver-handler -f services/solver-handler/Dockerfile services/solver-handler/
docker build -t solver-pod -f services/solver-pod/Dockerfile services/solver-pod/
docker build -t solver-db-comms -f services/solver-db-comms/Dockerfile services/solver-db-comms/

kubectl apply -f kubernetes-deployments/api-gateway-deployment.yaml
kubectl apply -f kubernetes-deployments/api-gateway-service.yaml

kubectl apply -f kubernetes-deployments/frontend-deployment.yaml
kubectl apply -f kubernetes-deployments/frontend-service.yaml

kubectl apply -f kubernetes-deployments/solver-handler-deployment.yaml
kubectl apply -f kubernetes-deployments/solver-handler-service.yaml

kubectl apply -f kubernetes-deployments/solver-db-comms-deployment.yaml
kubectl apply -f kubernetes-deployments/solver-db-comms-service.yaml

kubectl apply -f kubernetes-deployments/role-job-creator.yaml
kubectl apply -f kubernetes-deployments/cluster-role-job-creator.yaml
kubectl apply -f kubernetes-deployments/clusterrolebinding-job-creator.yaml

end_time=$(date +%s)
execution_time=$((end_time - start_time))
echo "Script execution time: $execution_time seconds"

watch kubectl get pods