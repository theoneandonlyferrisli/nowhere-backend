resource "google_project_service" "container" {
  project = "nowhere-link-prod"
  service = "container.googleapis.com"
}

resource "google_project_service" "compute" {
  project = "nowhere-link-prod"
  service = "compute.googleapis.com"
}

resource "google_project_service" "dns" {
  project = "nowhere-link-prod"
  service = "dns.googleapis.com"
}
