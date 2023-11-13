#!/bin/bash
start_time=$(date +%s)

minikube start --cpus=4 --memory=4000
eval $(minikube docker-env)


# Build the backend Docker image
docker build -t my-frontend -f services/frontend/Dockerfile services/frontend/

# Build the frontend Docker image
docker build -t my-backend -f "services/solver"/Dockerfile services/solver/

kubectl apply -f services/kubernetes-deployments

end_time=$(date +%s)
execution_time=$((end_time - start_time))
echo "Script execution time: $execution_time seconds"


