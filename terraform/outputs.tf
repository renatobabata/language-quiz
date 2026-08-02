output "vm_public_ip" {
  description = "Public IP of the VM (use for SSH and DNS)"
  value       = google_compute_instance.app_vm.network_interface[0].access_config[0].nat_ip
}

output "vm_name" {
  value = google_compute_instance.app_vm.name
}
