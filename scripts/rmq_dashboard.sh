password="$(kubectl get secret rabbitmq -o jsonpath='{.data.rabbitmq-password}' | base64 --decode)"
echo "password: $password"

kubectl port-forward svc/rabbitmq -n  8080:4369