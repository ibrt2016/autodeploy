import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORK_DIR = os.path.join(BASE_DIR, "..", "jobs")
TERRAFORM_BIN = "terraform"

os.makedirs(WORK_DIR, exist_ok=True)
