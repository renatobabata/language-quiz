variable "gcp_project_id" {
  description = "GCP project ID"
  type        = string
}

variable "gcp_region" {
  description = "GCP region. Must be one of the Always Free eligible regions for e2-micro."
  type        = string
  default     = "us-central1"
}

variable "gcp_zone" {
  description = "GCP zone"
  type        = string
  default     = "us-central1-a"
}

variable "ssh_user" {
  description = "SSH username for the VM"
  type        = string
  default     = "languagequiz"
}

variable "ssh_public_key_path" {
  description = "Local path to the SSH public key used to access the VM"
  type        = string
  default     = "~/.ssh/id_ed25519.pub"
}

variable "allowed_ssh_source_range" {
  description = "CIDR range allowed to SSH into the VM. Restrict this to your own IP (e.g. 1.2.3.4/32) instead of 0.0.0.0/0."
  type        = string
  default     = "0.0.0.0/0"
}
