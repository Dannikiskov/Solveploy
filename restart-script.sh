#!/bin/bash

eval $(minikube docker-env)

docker build -t frontend -f services/frontend/Dockerfile services/frontend/
docker build -t api-gateway -f services/api-gateway/Dockerfile services/api-gateway/
docker build -t solver-handler -f services/solver-handler/Dockerfile services/solver-handler/
docker build -t solver-pod -f services/solver-pod/Dockerfile services/solver-pod/
docker build -t solver-db-comms -f services/solver-db-comms/Dockerfile services/solver-db-comms/

kubectl rollout restart deployment frontend
kubectl rollout restart deployment api-gateway
kubectl rollout restart deployment solver-handler
kubectl rollout restart deployment solver-db-comms

watch kubectl get pods



