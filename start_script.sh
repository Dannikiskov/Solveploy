#!/bin/bash

start_time=$(date +%s)
minikube start 

eval $(minikube docker-env)

kubectl apply -f kubernetes-deployments/rabbitmq-operator.yaml
kubectl apply -f kubernetes-deployments/rabbitmq-definition.yaml
echo "Starting Docker base image.."
docker build -q -t solveploy-backend-base-image -f base-image/DockerfileBackendBase base-image/
echo "Finished Docker base image.."

(
  # Start Docker frontend build
  echo "Starting Docker frontend build.."
  docker build -q -t frontend -f services/frontend/Dockerfile services/frontend/
  echo "Finished Docker frontend build."
) &

(
  # Start Docker api-gateway build
  echo "Starting Docker api-gateway build.."
  docker build -q -t api-gateway -f services/api-gateway/Dockerfile services/api-gateway/
  echo "Finished Docker api-gateway build."
) &

(
  # Start Docker solver-handler build
  echo "Starting Docker solver-handler build.."
  docker build -q -t solver-handler -f services/solver-handler/Dockerfile services/solver-handler/
  echo "Finished Docker solver-handler build."
) &

(
  # Start Docker knowledge-base build
  echo "Starting Docker knowledge-bank build.."
  docker build -q -t knowledge-base -f services/knowledge-base/Dockerfile services/knowledge-base/
  echo "Finished Docker knowledge-bank build."
) &

(
  # Start Docker solver-pod build
  echo "Starting Docker solver-pod build.."
  docker build -q -t solver-pod -f services/solver-pod/Dockerfile services/solver-pod/
  echo "Finished Docker solver-pod build."
) &


# Wait for all background processes to finish
wait

# Apply Kubernetes deployments and services
kubectl apply -f kubernetes-deployments/api-gateway-deployment.yaml
kubectl apply -f kubernetes-deployments/api-gateway-service.yaml

kubectl apply -f kubernetes-deployments/frontend-deployment.yaml
kubectl apply -f kubernetes-deployments/frontend-service.yaml

kubectl apply -f kubernetes-deployments/solver-handler-deployment.yaml
kubectl apply -f kubernetes-deployments/solver-handler-service.yaml

kubectl apply -f kubernetes-deployments/role-job-creator.yaml
kubectl apply -f kubernetes-deployments/cluster-role-job-creator.yaml
kubectl apply -f kubernetes-deployments/clusterrolebinding-job-creator.yaml

kubectl apply -f kubernetes-deployments/knowledge-base-database-deployment.yaml
kubectl apply -f kubernetes-deployments/knowledge-base-database-service.yaml

kubectl apply -f kubernetes-deployments/knowledge-base-deployment.yaml
kubectl apply -f kubernetes-deployments/knowledge-base-service.yaml

end_time=$(date +%s)
execution_time=$((end_time - start_time))
echo "Script execution time: $execution_time seconds"

watch kubectl get pods
