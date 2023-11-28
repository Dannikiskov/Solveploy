#!/bin/bash
start_time=$(date +%s)

eval $(minikube docker-env)

docker build -t frontend -f services/frontend/Dockerfile services/frontend/
docker build -t api-gateway -f services/api-gateway/Dockerfile services/api-gateway/
docker build -t solver-handler -f services/solver-handler/Dockerfile services/solver-handler/

kubectl rollout restart deployment frontend
kubectl rollout restart deployment api-gateway
kubectl rollout restart deployment solver-handler

end_time=$(date +%s)
execution_time=$((end_time - start_time))
echo "Script execution time: $execution_time seconds"


