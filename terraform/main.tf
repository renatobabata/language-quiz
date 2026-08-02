resource "google_compute_instance" "app_vm" {
  name         = "language-quiz-vm"
  # e2-micro is the shape eligible for the GCP Always Free tier
  machine_type = "e2-micro"
  zone         = var.gcp_zone

  # Always Free requires a non-preemptible instance — explicit for clarity
  scheduling {
    preemptible = false
  }

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2404-lts-amd64"
      # Standard (non-SSD) disk to stay within the Always Free 30GB limit
      type = "pd-standard"
      size = 30
    }
  }

  network_interface {
    network = "default"
    access_config {
      # empty block = ephemeral public IP (required for the app to be reachable,
      # and avoids the cost of a reserved static IP)
    }
  }

  metadata = {
    ssh-keys = "${var.ssh_user}:${file(var.ssh_public_key_path)}"
  }

  tags = ["http-server", "https-server"]
}

resource "google_compute_firewall" "allow_http_https" {
  name    = "language-quiz-allow-web"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["80", "443"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["http-server", "https-server"]
}

resource "google_compute_firewall" "allow_ssh" {
  name    = "language-quiz-allow-ssh"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = [var.allowed_ssh_source_range]
  target_tags   = ["http-server", "https-server"]
}
