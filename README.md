# 📘 **README.md — AutoDeploy CLI**
Automated Natural-Language-Driven Application Deployment  
Supports AWS + GCP VMs, Framework Detection, Git Clone on VM, Auto Port Detection, Auto Systemd Service

---

# 🚀 AutoDeploy — The No-DevOps Deployment Engine

AutoDeploy is a backend + CLI tool that **automatically deploys applications to cloud VMs** (AWS or GCP) using:

- Natural language instructions  
- A GitHub repository (public or private)  
- Automatic framework detection (Flask, Django, FastAPI, Node.js, etc.)  
- Automatic dependency installation  
- Automatic infrastructure provisioning via Terraform  
- Automatic service creation using systemd  
- Automatic replacement of `127.0.0.1` → `0.0.0.0` in `app.py`  
- Automatic replacement of `localhost` → VM Public IP inside HTML templates  

The goal: **Minimal user intervention. No DevOps knowledge required.**

---

# 🧠 Example Usage (CLI)

```
autodeploy deploy \
  --description "Deploy this Flask app to AWS" \
  --repo https://github.com/Arvo-AI/hello_world
```

This will:

1. Parse natural language to determine platform (AWS)  
2. Analyze the GitHub repo (framework, port, start command)  
3. Provision cloud VM through Terraform  
4. SSH into VM automatically  
5. Clone the GitHub repo directly on VM  
6. Fix host binding (`app.run(host='0.0.0.0')`)  
7. Update templates/index.html to use VM public IP  
8. Install dependencies  
9. Create and enable systemd service  
10. Provide the final public URL  

---

# ✨ Features

| Feature | Supported |
|--------|-----------|
| Natural language deployment | ✅ |
| AWS EC2 VM deployment | ✅ |
| GCP Compute Engine deployment | ✅ |
| Git clone on VM (no SFTP) | ✅ |
| Framework auto-detection | Flask, Django, FastAPI, Node.js |
| Port detection | Auto-extracted from repo |
| Auto-rewrite app.py to 0.0.0.0 | ✅ |
| Auto-replace localhost in index.html | ✅ |
| Auto systemd service creation | ✅ |
| Automatic Terraform key generation | ✅ |
| Minimal user intervention | 🚀 |

---

# 📦 Installation

## 1. Clone the Repo

```
git clone https://github.com/YOUR_USERNAME/autodeploy.git
cd autodeploy
```

## 2. Install Python Dependencies

```
pip install -r requirements.txt
```

## 3. Install Terraform

Download from:  
https://developer.hashicorp.com/terraform/downloads

Then verify:

```
terraform version
```

## 4. Install the CLI

```
pip install -e .
```

---

# 🔑 Cloud Credentials Setup

## AWS

You need:

- AWS_ACCESS_KEY_ID  
- AWS_SECRET_ACCESS_KEY  
- Default region  

Set them:

```
aws configure
```

Or export manually:

```
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_REGION=us-east-1
```

---

# 🧰 How the CLI Works

The CLI command:

```
autodeploy deploy \
  --description "Deploy this Flask app to AWS" \
  --repo https://github.com/Arvo-AI/hello_world
```

Triggers the following sequence:

## 1️⃣ NLP Processor  
Parses natural language:

- Identify cloud provider (AWS/GCP)
- Extract deployment type (VM)
- Detect framework hints (Flask, Django, Node, etc.)

## 2️⃣ Repo Analyzer  
Clones the repo locally and extracts:

- Framework (Flask, Django, FastAPI, Node)
- Start command
- Port to expose
- Entry file (app.py, main.py, server.js)

Stores results:

```
analysis["repo_url"]
analysis["framework"]
analysis["port"]
analysis["start_command"]
```

## 3️⃣ Terraform Generator  
Creates:

```
jobs/{job_id}/terraform/
    main.tf
    variables.tf
    terraform.tfvars
    ssh_key
    ssh_key.pub
```

VM is created automatically.

## 4️⃣ Deployer (SSH Automation)

On the VM:

- Installs git, python, pip, node, etc.  
- Clones the repo:
  ```
  git clone <repo_url> /home/ubuntu/app
  ```  
- Rewrites app.py:
  ```
  127.0.0.1 → 0.0.0.0
  ```  
- Rewrites templates/index.html:
  ```
  localhost → <public_ip>
  ```  
- Installs dependencies  
- Creates systemd service:
  ```
  /etc/systemd/system/autodeploy-<job>.service
  ```  
- Enables and starts service

## 5️⃣ Output Returned to User

```
Application deployed successfully!
URL: http://<public_ip>:<port>
```

---

# 🧪 CLI Usage Reference

## Deploy an app

```
autodeploy deploy \
  --description "Deploy this FastAPI app on GCP" \
  --repo https://github.com/example/my_api
```

## Get status of a deployment

```
autodeploy status --job-id <id>
```

## List previous deployments

```
autodeploy list
```

---

# 🌐 Supported Frameworks

| Framework | Detection Method |
|----------|------------------|
| Flask | app.py + flask imports |
| Django | manage.py + settings.py |
| FastAPI | fastapi import |
| Node.js | package.json + express/fastify detection |

---

# 📁 Project Structure

```
autodeploy/
│
├── backend/
│   ├── analyzer/
│   ├── nlp/
│   ├── terraform_generator/
│   ├── deploy_vm.py
│   └── utils/
│
├── cli/
│   └── autodeploy_cli.py
│
├── jobs/
│   └── <job_id>/
│       ├── terraform/
│       └── logs/
│
└── README.md
```

---

# 🛠 Troubleshooting

### ❗ App fails to start automatically

Check logs:

```
sudo journalctl -u autodeploy-<job_id> -f
```

---

### ❗ Port not open or reachable

Security group may block your port.  
Terraform automatically opens:

- 22 (SSH)
- Detected app port

---

### ❗ HTML still points to localhost

Search for remaining references:

```
sudo grep -R "localhost" /home/ubuntu/app
```

---

# 📜 License

MIT License

---

# 🤝 Contributing

PRs welcome!  
Planned features:

- Kubernetes support  
- Docker image builds  
- Serverless deployment  
- Buildpacks  
- Deploy keys for private repos  

---

# 🎥 Demo Video

Record a 1-minute Loom video demonstrating:

- Running the CLI  
- Seeing logs  
- Opening the deployed app  

