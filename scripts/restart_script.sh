#!/bin/bash

eval $(minikube docker-env)

docker build -q -t frontend -f services/frontend/Dockerfile services/frontend/
docker build -q -t api-gateway -f services/api_gateway/Dockerfile services/api_gateway/
docker build -q -t job-handler -f services/job_handler/Dockerfile services/job_handler/
docker build -q -t mzn-pod -f services/mzn_pod/Dockerfile services/mzn_pod/
docker build -q -t sat-pod -f services/sat_pod/Dockerfile services/sat_pod/
docker build -q -t maxsat-pod -f services/maxsat_pod/Dockerfile services/maxsat_pod/
docker build -q -t knowledge-base -f services/knowledge_base/Dockerfile services/knowledge_base/

kubectl rollout restart deployment frontend
kubectl rollout restart deployment api-gateway
kubectl rollout restart deployment job-handler
kubectl rollout restart deployment knowledge-base

kubectl delete jobs --all

watch kubectl get podskgp