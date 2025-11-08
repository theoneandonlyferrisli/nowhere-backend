resource "google_dns_managed_zone" "nowhereapp_primary" {
  name        = "nowhereapp-ai-zone"
  dns_name    = "nowhereapp.ai."
  description = "Primary DNS zone for nowhereapp.ai"

  depends_on = [
    google_project_service.dns
  ]
}