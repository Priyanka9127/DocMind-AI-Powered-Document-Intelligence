# VPC Network
resource "google_compute_network" "docmind_vpc" {
  name                    = "docmind-vpc"
  auto_create_subnetworks = false
}

# Subnet
resource "google_compute_subnetwork" "docmind_subnet" {
  name          = "docmind-subnet"
  region        = var.region
  network       = google_compute_network.docmind_vpc.name
  ip_cidr_range = "10.0.0.0/16"
}

# Service Account for GKE Nodes
resource "google_service_account" "default" {
  account_id   = "docmind-gke-nodes"
  display_name = "DocMind GKE Service Account"
}

# GKE Cluster
resource "google_container_cluster" "primary" {
  name     = var.cluster_name
  location = var.zone

  remove_default_node_pool = true
  initial_node_count       = 1

  network    = google_compute_network.docmind_vpc.name
  subnetwork = google_compute_subnetwork.docmind_subnet.name

  deletion_protection = false # for dev purposes
}

# Node Pool
resource "google_container_node_pool" "primary_nodes" {
  name       = "docmind-node-pool"
  location   = var.zone
  cluster    = google_container_cluster.primary.name
  node_count = 2

  node_config {
    preemptible  = true # Saves cost for personal projects
    machine_type = "e2-standard-4" # Requires slightly higher CPU/RAM for Ollama & Chroma

    # Google recommends custom service accounts that have cloud-platform scope and permissions granted via IAM Roles.
    service_account = google_service_account.default.email
    oauth_scopes    = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}

# Cloud SQL/PostgreSQL (Optional Metadata Database placeholder)
# Interviewer prep: Useful to show you know how to provision databases via Terraform
# Uncomment the below if you want to deploy a DB
/*
resource "google_sql_database_instance" "instance" {
  name             = "docmind-db-instance"
  region           = var.region
  database_version = "POSTGRES_14"
  settings {
    tier = "db-f1-micro"
  }
  deletion_protection = false
}
*/
