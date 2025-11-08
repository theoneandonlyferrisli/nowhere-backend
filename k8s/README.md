# Kubernetes Manifests

Kubernetes resources for deploying the link server to GKE Autopilot with dual-domain support.

## Resources

- **deployment.yaml** - Link server deployment (2 replicas, currently version 2025.11.1)
- **service.yaml** - NodePort service exposing pods
- **managed-cert.yaml** - Google-managed TLS certificate for both domains:
  - `links.nowhereapp.ai`
  - `nowhereapp.ai`
- **ingress.yaml** - GCE Ingress with HTTPS load balancer routing both domains to link-server service

## Prerequisites

1. GKE cluster must be running (created via Terraform)
2. Docker image must be pushed to Artifact Registry
3. kubectl must be configured with cluster credentials

### Get Cluster Credentials

```bash
gcloud container clusters get-credentials nowhere-link-autopilot \
  --region us-central1 \
  --project nowhere-link-prod
```

## Initial Deployment

Deploy all resources in order:

```bash
cd k8s
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f managed-cert.yaml
kubectl apply -f ingress.yaml
```

**Note:** The ManagedCertificate can take up to 24 hours to provision after deployment. `links.nowhereapp.ai` will provision faster than `nowhereapp.ai` since it's been active longer.

## Common Operations

### Check Deployment Status

```bash
# View pods
kubectl get pods

# Check pod logs
kubectl logs -l app=link-server --tail=50

# View all resources
kubectl get all
```

### Check Ingress & Certificate

```bash
# Get ingress details (IP address)
kubectl get ingress link-server-ingress

# Check certificate status (should show "Active" for both domains)
kubectl get managedcertificate
kubectl get managedcertificate links-nowhereapp-cert -o jsonpath='{.status.domainStatus}' | python3 -m json.tool
```

### Update Deployment After Code Changes

After building and pushing a new Docker image:

```bash
# Edit deployment.yaml to use new version tag (e.g., 2025.11.2)
# Then apply:
kubectl apply -f deployment.yaml

# Watch rollout progress
kubectl rollout status deployment/link-server
```

### Scale Deployment

```bash
# Scale to 3 replicas
kubectl scale deployment/link-server --replicas=3

# Or edit deployment.yaml and reapply
kubectl apply -f deployment.yaml
```

### Rollback Deployment

```bash
# View rollout history
kubectl rollout history deployment/link-server

# Rollback to previous version
kubectl rollout undo deployment/link-server

# Rollback to specific revision
kubectl rollout undo deployment/link-server --to-revision=2
```

### Update Ingress Configuration

After modifying `ingress.yaml`:

```bash
kubectl apply -f ingress.yaml
```

**Note:** Changes to the Ingress can take several minutes to propagate to the load balancer.

### Update Certificate Domains

After modifying `managed-cert.yaml`:

```bash
kubectl apply -f managed-cert.yaml
```

**Note:** Certificate reprovisioning takes 10-30 minutes.

## Troubleshooting

### Pods Not Starting

```bash
# Check pod details
kubectl describe pod <pod-name>

# View pod logs
kubectl logs <pod-name>
```

### Certificate Stuck in "Provisioning"

```bash
# Check certificate details
kubectl describe managedcertificate links-nowhereapp-cert

# Common issues:
# - DNS not pointing to correct IP
# - Domain not yet propagated
# - Certificate quota exceeded
```

### Ingress Not Routing Traffic

```bash
# Check ingress details
kubectl describe ingress link-server-ingress

# Verify backend service
kubectl get service link-server-svc

# Check backend health
kubectl describe ingress link-server-ingress | grep -A 10 "Backend"
```

## Clean Up

Remove all resources:

```bash
kubectl delete -f ingress.yaml
kubectl delete -f managed-cert.yaml
kubectl delete -f service.yaml
kubectl delete -f deployment.yaml
```
