#!/bin/bash

eval $(minikube docker-env)

docker build -q -t frontend -f services/frontend/Dockerfile services/frontend/
kubectl rollout restart deployment frontend

watch kubectl get pods