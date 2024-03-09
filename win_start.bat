@echo off

REM Start Minikube
minikube start --cpus=4 --memory=6000

REM Set Minikube Docker environment
@FOR /f "tokens=*" %%i IN ('minikube docker-env') DO @%%i

REM Apply Kubernetes resources
kubectl apply -f kubernetes-deployments\rabbitmq-operator.yaml
kubectl apply -f kubernetes-deployments\rabbitmq-definition.yaml

REM Build Docker base image
echo Starting Docker base image..
docker build -q -t solveploy-backend-base-image -f base-image\DockerfileBackendBase base-image\
echo Finished Docker base image..

REM Start Docker builds in parallel
start /B "" cmd /c "docker build -q -t frontend -f services\frontend\Dockerfile services\frontend\ & echo %errorlevel% > frontend.err"
start /B "" cmd /c "docker build -q -t api-gateway -f services\api_gateway\Dockerfile services\api_gateway\ & echo %errorlevel% > api-gateway.err"
start /B "" cmd /c "docker build -q -t job-handler -f services\job_handler\Dockerfile services\job_handler\ & echo %errorlevel% > job-handler.err"
start /B "" cmd /c "docker build -q -t knowledge-base -f services\knowledge_base\Dockerfile services\knowledge_base\ & echo %errorlevel% > knowledge-base.err"
start /B "" cmd /c "docker build -q -t mzn-pod -f services\mzn_pod\Dockerfile services\mzn_pod\ & echo %errorlevel% > mzn-pod.err"
start /B "" cmd /c "docker build -q -t sat-pod -f services\sat_pod\Dockerfile services\sat_pod\ & echo %errorlevel% > sat-pod.err"

:wait
ping localhost -n 2 >nul
for %%A in (frontend api-gateway job-handler knowledge-base mzn-pod sat-pod) do (
    if not exist %%A.err goto wait
)

REM Delete %%A.err files
for %%A in (frontend api-gateway job-handler knowledge-base mzn-pod sat-pod) do (
    if exist %%A.err del %%A.err
)

REM Apply Kubernetes deployments and services
kubectl apply -f kubernetes-deployments\api-gateway-deployment.yaml
kubectl apply -f kubernetes-deployments\api-gateway-service.yaml
kubectl apply -f kubernetes-deployments\frontend-deployment.yaml
kubectl apply -f kubernetes-deployments\frontend-service.yaml
kubectl apply -f kubernetes-deployments\job-handler-deployment.yaml
kubectl apply -f kubernetes-deployments\job-handler-service.yaml
kubectl apply -f kubernetes-deployments\role-job-creator.yaml
kubectl apply -f kubernetes-deployments\cluster-role-job-creator.yaml
kubectl apply -f kubernetes-deployments\clusterrolebinding-job-creator.yaml
kubectl apply -f kubernetes-deployments\knowledge-base-database-deployment.yaml
kubectl apply -f kubernetes-deployments\knowledge-base-database-service.yaml
kubectl apply -f kubernetes-deployments\knowledge-base-deployment.yaml
kubectl apply -f kubernetes-deployments\knowledge-base-service.yaml

REM End of script
exit
