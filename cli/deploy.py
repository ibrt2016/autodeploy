import requests
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("description")
parser.add_argument("repo_url")
args = parser.parse_args()

resp = requests.post("http://localhost:8000/deploy", json={
    "description": args.description,
    "repo_url": args.repo_url
})

print(resp.json())
