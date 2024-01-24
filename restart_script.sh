#!/bin/bash

eval $(minikube docker-env)

docker build -q -t frontend -f services/frontend/Dockerfile services/frontend/
docker build -q -t api-gateway -f services/api-gateway/Dockerfile services/api-gateway/
docker build -q -t solver-handler -f services/solver-handler/Dockerfile services/solver-handler/
docker build -q -t solver-pod -f services/solver-pod/Dockerfile services/solver-pod/
docker build -q -t knowledge-base -f services/knowledge-base/Dockerfile services/knowledge-base/

kubectl rollout restart deployment frontend
kubectl rollout restart deployment api-gateway
kubectl rollout restart deployment solver-handler
kubectl rollout restart deployment knowledge-base


watch kubectl get pods



