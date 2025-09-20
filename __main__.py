import pulumi
import pulumi_gcp as gcp
import os

# Note to the user: The instance type is set to 'e2-standard-2' instead of 'e2-micro'
# because the application's README recommends at least 8GB of RAM for the ML models.
# 'e2-micro' only provides 1GB of RAM, which would likely cause performance issues or failures.
pulumi.log.info("Using 'e2-standard-2' instance type for adequate performance based on project requirements.")

# Get the GCP project and region from Pulumi config.
# Ensure you have run `pulumi config set gcp:project YOUR_PROJECT_ID` and `pulumi config set gcp:region YOUR_REGION`
config = pulumi.Config()
gcp_project = gcp.config.project
gcp_region = gcp.config.region

if not gcp_project or not gcp_region:
    raise pulumi.RunError("GCP project and region must be set in Pulumi config. \n"
                           "Run `pulumi config set gcp:project YOUR_PROJECT_ID` and "
                           "`pulumi config set gcp:region YOUR_REGION`.")

# Create a dedicated service account for the VM to follow principle of least privilege
instance_service_account = gcp.serviceaccount.Account("k3s-server-sa",
    account_id="k3s-server-sa",
    display_name="Service Account for K3s Server VM",
    project=gcp_project)

# Grant the service account the necessary roles for operation
project_iam_bindings = [
    gcp.projects.IAMMember(f"log-writer-binding",
        project=gcp_project,
        role="roles/logging.logWriter",
        member=pulumi.Output.concat("serviceAccount:", instance_service_account.email)),
    gcp.projects.IAMMember(f"metric-writer-binding",
        project=gcp_project,
        role="roles/monitoring.metricWriter",
        member=pulumi.Output.concat("serviceAccount:", instance_service_account.email)),
    gcp.projects.IAMMember(f"gcr-puller-binding",
        project=gcp_project,
        role="roles/storage.objectViewer", # Required to pull images from GCR
        member=pulumi.Output.concat("serviceAccount:", instance_service_account.email)),
]

# Define the startup script to install Docker and k3s
startup_script = """#!/bin/bash
set -e
# Log everything to a file
exec > >(tee /var/log/startup-script.log|logger -t startup-script -s 2>/dev/console) 2>&1

echo "Starting startup script..."

# Wait for network to be ready
until ping -c1 google.com &>/dev/null; do
  echo "Waiting for network..."
  sleep 1
done

# Install Docker
echo "Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
usermod -aG docker ubuntu

# Install k3s
echo "Installing k3s..."
curl -sfL https://get.k3s.io | sh -s - --docker

# Create a kubeconfig file that's accessible by the ubuntu user
echo "Creating kubeconfig..."
mkdir -p /home/ubuntu/.kube
cp /etc/rancher/k3s/k3s.yaml /home/ubuntu/.kube/config
chown -R ubuntu:ubuntu /home/ubuntu/.kube
chmod 600 /home/ubuntu/.kube/config

echo "Startup script finished."
"""

# Read the public SSH key from the user's home directory
ssh_key_path = os.path.expanduser("~/.ssh/id_rsa.pub")
ssh_key = ""
try:
    with open(ssh_key_path, 'r') as f:
        ssh_key = f.read()
except FileNotFoundError:
    pulumi.log.warn(f"SSH public key not found at {ssh_key_path}. The VM will be created without a pre-configured SSH key. You may need to add one manually.")

# Create a GCP compute instance
instance = gcp.compute.Instance(
    "k3s-server",
    machine_type="e2-standard-2",
    boot_disk=gcp.compute.InstanceBootDiskArgs(
        initialize_params=gcp.compute.InstanceBootDiskInitializeParamsArgs(
            image="ubuntu-os-cloud/ubuntu-2404-lts",
            size=50, # Increase disk size for containers and images
        )
    ),
    network_interfaces=[gcp.compute.InstanceNetworkInterfaceArgs(
        network="default",
        access_configs=[gcp.compute.InstanceNetworkInterfaceAccessConfigArgs()],
    )],
    metadata={
        "startup-script": startup_script,
    } if not ssh_key else {
        "startup-script": startup_script,
        "ssh-keys": f"ubuntu:{ssh_key}",
    },
    tags=["web", "k3s-server"],
    project=gcp_project,
    # Select a zone within the configured region
    zone=pulumi.Output.from_input(gcp_region).apply(lambda r: r + "-a"),
    service_account=gcp.compute.InstanceServiceAccountArgs(
        email=instance_service_account.email,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    ),
    allow_stopping_for_update=True,
)

# Create a firewall rule to allow HTTP, HTTPS, and Kubernetes API traffic from anywhere
firewall_public = gcp.compute.Firewall(
    "allow-k3s-public-traffic",
    network="default",
    allows=[
        gcp.compute.FirewallAllowArgs(protocol="tcp", ports=["80"]),  # HTTP
        gcp.compute.FirewallAllowArgs(protocol="tcp", ports=["443"]), # HTTPS
        gcp.compute.FirewallAllowArgs(protocol="tcp", ports=["6443"]),# Kubernetes API Server (consider restricting if not needed)
    ],
    source_ranges=["0.0.0.0/0"],
    target_tags=["k3s-server"], # Apply rule only to our instance
    project=gcp_project,
)

# Create a firewall rule to allow SSH only from a trusted IP range (replace with your actual IP/CIDR)
firewall_ssh = gcp.compute.Firewall(
    "allow-k3s-ssh",
    network="default",
    allows=[
        gcp.compute.FirewallAllowArgs(protocol="tcp", ports=["22"]),  # SSH
    ],
    source_ranges=["203.0.113.0/24"],  # <-- Replace with your trusted IP range
    target_tags=["k3s-server"],
    project=gcp_project,
)
# Export the instance's external IP address and name
pulumi.export("instance_name", instance.name)
pulumi.export("instance_ip", instance.network_interfaces[0].access_configs[0].nat_ip)
