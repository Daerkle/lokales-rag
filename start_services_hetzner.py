#!/usr/bin/env python3
"""
start_services.py

This script starts the Supabase stack first, waits for it to initialize,
and then starts the local AI stack. Both stacks use the same Docker Compose
project name ("localai") so they appear together in Docker Desktop.
"""

import os
import subprocess
import shutil
import time
import argparse
import platform
import sys

def run_command(cmd, cwd=None):
    """Run a shell command and print it."""
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, cwd=cwd, check=True)

def clone_supabase_repo():
    """Clone the Supabase repository using sparse checkout if not already present."""
    if not os.path.exists("supabase"):
        print("Cloning the Supabase repository...")
        run_command(["git", "clone", "--filter=blob:none", "--no-checkout", "https://github.com/supabase/supabase.git"])
        os.chdir("supabase")
        run_command(["git", "sparse-checkout", "init", "--cone"])
        run_command(["git", "sparse-checkout", "set", "docker"])
        run_command(["git", "checkout", "master"])
        os.chdir("..")
    else:
        print("Supabase repository already exists, updating...")
        os.chdir("supabase")
        run_command(["git", "pull"])
        os.chdir("..")

def prepare_supabase_env():
    """Copy .env to .env in supabase/docker."""
    env_path = os.path.join("supabase", "docker", ".env")
    shutil.copyfile(".env", env_path)
    print("Copied .env to supabase/docker/.env")

def stop_existing_containers():
    """Stop and remove existing containers for our unified project ('localai')."""
    print("Stopping and removing existing containers for project 'localai'...")
    run_command([
        "docker-compose", "-p", "localai",
        "-f", "docker-compose.yml",
        "-f", "supabase/docker/docker-compose.yml",
        "down"
    ])

def start_supabase():
    """Start the Supabase services."""
    print("Starting Supabase services...")
    run_command([
        "docker-compose", "-p", "localai",
        "-f", "supabase/docker/docker-compose.yml",
        "up", "-d"
    ])

def start_local_ai(profile=None):
    """Start the local AI services."""
    print("Starting local AI services...")
    cmd = ["docker-compose", "-p", "localai"]
    if profile and profile != "none":
        cmd.extend(["--profile", profile])
    cmd.extend(["-f", "docker-compose.yml", "up", "-d"])
    run_command(cmd)

def generate_searxng_secret_key():
    """Generate a secret key for SearXNG."""
    settings_path = os.path.join("searxng", "settings.yml")
    base_path = os.path.join("searxng", "settings-base.yml")

    if not os.path.exists(base_path):
        print(f"Missing {base_path}, skipping secret generation.")
        return

    if not os.path.exists(settings_path):
        shutil.copyfile(base_path, settings_path)
        print(f"Created settings.yml from base")
    else:
        print(f"settings.yml already exists")

    try:
        system = platform.system()
        random_key = subprocess.check_output(["openssl", "rand", "-hex", "32"]).decode('utf-8').strip()
        sed_cmd = []

        if system == "Darwin":
            sed_cmd = ["sed", "-i", "", f"s|ultrasecretkey|{random_key}|g", settings_path]
        elif system == "Windows":
            print("Manual key generation required on Windows.")
            return
        else:
            sed_cmd = ["sed", "-i", f"s|ultrasecretkey|{random_key}|g", settings_path]

        subprocess.run(sed_cmd, check=True)
        print("Secret key updated in settings.yml")
    except Exception as e:
        print(f"Failed to update secret: {e}")

def check_and_fix_docker_compose_for_searxng():
    """Check and fix docker-compose.yml for SearXNG's first run."""
    path = "docker-compose.yml"
    if not os.path.exists(path):
        print("docker-compose.yml not found")
        return

    try:
        with open(path, 'r') as f:
            content = f.read()

        is_first_run = True
        result = subprocess.run(["docker", "ps", "--filter", "name=searxng", "--format", "{{.Names}}"],
                                capture_output=True, text=True)
        container_name = result.stdout.strip()

        if container_name:
            check = subprocess.run(["docker", "exec", container_name, "sh", "-c",
                                    "[ -f /etc/searxng/uwsgi.ini ] && echo found || echo not_found"],
                                   capture_output=True, text=True)
            is_first_run = "found" not in check.stdout

        marker = "cap_drop: - ALL"
        if is_first_run and marker in content:
            with open(path, 'w') as f:
                f.write(content.replace(marker, f"# {marker}  # Temporarily commented out"))
            print("Temporarily commented out cap_drop for first run")
        elif not is_first_run and f"# {marker}" in content:
            with open(path, 'w') as f:
                f.write(content.replace(f"# {marker}  # Temporarily commented out", marker))
            print("Re-enabled cap_drop after initialization")
    except Exception as e:
        print(f"Error while patching docker-compose.yml: {e}")

def main():
    parser = argparse.ArgumentParser(description='Start local AI and Supabase services.')
    parser.add_argument('--profile', choices=['cpu', 'gpu-nvidia', 'gpu-amd', 'none'], default='cpu')
    args = parser.parse_args()

    clone_supabase_repo()
    prepare_supabase_env()
    generate_searxng_secret_key()
    check_and_fix_docker_compose_for_searxng()
    stop_existing_containers()
    start_supabase()

    print("Waiting for Supabase to initialize...")
    time.sleep(10)

    start_local_ai(args.profile)

if __name__ == "__main__":
    main()
