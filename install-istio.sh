helm repo add istio https://istio-release.storage.googleapis.com/charts
helm repo update
helm install istio-base istio/base -n istio-system --set defaultRevision=default --create-namespace
helm install istiod istio/istiod -n istio-system --wait
kubectl create namespace istio-ingress
helm install istio-ingress istio/gateway -n istio-ingress --wait
kubectl label namespace default istio-injection=enabled
