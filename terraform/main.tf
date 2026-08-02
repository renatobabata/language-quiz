resource "google_compute_instance" "app_vm" {
  name         = "language-quiz-vm"
  machine_type = "e2-micro"
  zone         = var.gcp_zone

  scheduling {
    preemptible = false
  }

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2404-lts-amd64"
      type  = "pd-standard"
      size  = 30
    }
  }

  network_interface {
    network = "default"
    access_config {
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
