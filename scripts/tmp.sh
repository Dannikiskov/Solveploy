# Get the secret from the rabbitmq-system namespace
secret=$(kubectl get secret message-broker-default-user -n rabbitmq-system -o json)

# Remove the namespace field from the secret's metadata
secret=$(echo "$secret" | jq 'del(.metadata.namespace)')

# Apply the secret to the default namespace
echo "$secret" | kubectl apply -n default -f -