#!/bin/bash

eval $(minikube docker-env)

docker build -t solver-handler -f services/solver-handler/Dockerfile services/solver-handler/
kubectl rollout restart deployment solver-handler

watch kubectl get pods