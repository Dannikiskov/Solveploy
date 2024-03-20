#!/bin/bash



# Deploy app locally
minikube start --cpus=4 --memory=6000

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
  docker build -q -t api-gateway -f services/api_gateway/Dockerfile services/api_gateway/
  echo "Finished Docker api-gateway build."
) &

(
  # Start Docker job-handler build
  echo "Starting Docker job-handler build.."
  docker build -q -t job-handler -f services/job_handler/Dockerfile services/job_handler/
  echo "Finished Docker job-handler build."
) &

(
  # Start Docker knowledge-base build
  echo "Starting Docker knowledge-bank build.."
  docker build -q -t knowledge-base -f services/knowledge_base/Dockerfile services/knowledge_base/
  echo "Finished Docker knowledge-bank build."
) &

(
  # Start Docker mzn-pod build
  echo "Starting Docker mzn-pod build.."
  docker build -q -t mzn-pod -f services/mzn_pod/Dockerfile services/mzn_pod/
  echo "Finished Docker mzn-pod build."
) &

(
  # Start Docker sat-pod build
  echo "Starting Docker sat-pod build.."
  docker build -q -t sat-pod -f services/sat_pod/Dockerfile services/sat_pod/
  echo "Finished Docker sat-pod build."
) &

(
  # Start Docker sat-pod build
  echo "Starting Docker maxsat-pod build.."
  docker build -q -t maxsat-pod -f services/maxsat_pod/Dockerfile services/maxsat_pod/
  echo "Finished Docker maxsat-pod build."
) &


# Wait for all background processes to finish
wait

# Apply Kubernetes deployments and services
kubectl apply -f kubernetes-deployments/api-gateway-deployment.yaml
kubectl apply -f kubernetes-deployments/api-gateway-service.yaml

kubectl apply -f kubernetes-deployments/frontend-deployment.yaml
kubectl apply -f kubernetes-deployments/frontend-service.yaml

kubectl apply -f kubernetes-deployments/job-handler-deployment.yaml
kubectl apply -f kubernetes-deployments/job-handler-service.yaml

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
