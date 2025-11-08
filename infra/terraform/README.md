# Terraform Infrastructure

This directory contains Terraform configuration for the Nowhere link server infrastructure on GCP.

## What Gets Created

- **GKE Autopilot Cluster** (`nowhere-link-autopilot`) - Managed Kubernetes cluster in `us-central1`
- **Cloud DNS Zone** (`nowhereapp-ai-zone`) - Managed DNS for `nowhereapp.ai`
- **Global Static IP** (`links-nowhereapp-ip`) - Static IP for the load balancer
- **DNS A Record** - `links.nowhereapp.ai` → static IP
- **Enabled APIs** - Container, Compute, DNS APIs

## Initial Setup

```bash
cd infra/terraform
terraform init
terraform apply
```

After applying, note the nameserver (NS) records output and update your domain registrar (GoDaddy) to use Cloud DNS nameservers.

## Get Cloud DNS Nameservers

```bash
gcloud dns managed-zones describe nowhereapp-ai-zone \
  --project=nowhere-link-prod \
  --format="value(nameServers)"
```

Update these NS records in GoDaddy for `nowhereapp.ai`.

## Common Operations

### View Current Infrastructure
```bash
terraform plan
```

### Apply Configuration Changes
After modifying any `.tf` files:
```bash
terraform apply
```

### Get Static IP Address
```bash
gcloud compute addresses describe links-nowhereapp-ip \
  --global \
  --project=nowhere-link-prod \
  --format="get(address)"
```

### Destroy Infrastructure
**Warning: This will delete everything**
```bash
terraform destroy
```

## Files

- `providers.tf` - GCP provider and Terraform version requirements
- `services.tf` - Enables required GCP APIs
- `dns.tf` - Cloud DNS zone for nowhereapp.ai
- `lb.tf` - Global static IP and DNS A record
- `gke.tf` - GKE Autopilot cluster configuration
