#!/bin/bash

eval $(minikube docker-env)

docker build -t frontend -f services/frontend/Dockerfile services/frontend/

kubectl rollout restart deployment frontend

kubectl get pods