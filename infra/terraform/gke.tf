resource "google_container_cluster" "nowhere_link_autopilot" {
  name             = "nowhere-link-autopilot"
  location         = "us-central1"
  enable_autopilot = true

  release_channel {
    channel = "REGULAR"
  }

  ip_allocation_policy {}

  depends_on = [
    google_project_service.compute,
    google_project_service.container
  ]
}