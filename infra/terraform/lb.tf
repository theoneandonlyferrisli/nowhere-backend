resource "google_compute_global_address" "links_ip" {
  name = "links-nowhereapp-ip"

  depends_on = [
    google_project_service.compute
  ]
}

resource "google_dns_record_set" "links_a" {
  name         = "links.nowhereapp.ai."
  type         = "A"
  ttl          = 300
  managed_zone = google_dns_managed_zone.nowhereapp_primary.name
  rrdatas      = [google_compute_global_address.links_ip.address]
}

# Root domain (nowhereapp.ai) pointing to same IP as links subdomain
resource "google_dns_record_set" "root_a" {
  name         = "nowhereapp.ai."
  type         = "A"
  ttl          = 300
  managed_zone = google_dns_managed_zone.nowhereapp_primary.name
  rrdatas      = [google_compute_global_address.links_ip.address]
}