# DevOps SteamScraper

A tiny **Python + FastAPI** service I use to demonstrate DevOps practices for the *Modern Practices in DevOps* course at FMI.  
The code is intentionally lightweight – the interesting parts are the **pipeline**, **containers**, **Kubernetes deployment**, and **security checks**.

---

## Why this repo exists

The project is mostly about the delivery process, not complex business logic. It shows how to:

* **Build & test** a FastAPI service  
* **Package** it with a multi-stage **Dockerfile**  
* **Publish** images to **GitHub Container Registry (GHCR)**  
* Run **CI** on every push / PR:
  * lint + format (`flake8`, `black --check`)  
  * unit tests (`pytest`)  
  * build and **Trivy-scan** the Docker image  
* Run **CD** on `main`:
  * rebuild & push to GHCR  
  * deploy to a Kubernetes cluster (kind or pre-created self-hosted runner)  
  * hit `/health` and `/games` as smoke tests  
* Apply some core DevOps ideas:
  * protected `main`, `feature` → `dev` → `main` workflow  
  * SAST with **GitHub CodeQL**  
  * manifests & pipelines kept as code in the repo  

---

## Branching in one sentence

`feature/*` → PR into **`dev`** (CI only) → PR into **`main`** (CI + CD) → automatic deploy.  
`main` is protected; merges require green CI.

---

## API in 15 seconds

| Method | Path             | Purpose                           |
| ------ | ---------------- | --------------------------------- |
| GET    | `/health`        | Used by probes & smoke tests      |
| GET    | `/games?rows=N`  | Returns **N** Steam games as JSON |

That’s enough logic to feel realistic and to test deployments without building a full Steam client.

---

## Stack

* **Python 3.12**, **FastAPI**, **Uvicorn**  
* Tests → `pytest`  
* Lint → `flake8`, format → `black` (check mode)  
* **Docker** multi-stage build → slim runtime image  
* Registry → **GHCR**  
* **Kubernetes** → `kind` (in CI) or pre-created cluster on a self-hosted Ubuntu runner  
* **GitHub Actions** → `.github/workflows/ci.yml` & `cd.yml`  
* Security → **CodeQL** (Python SAST) + **Trivy** (image scan)

---

## Repo tour

```text
.
├─ backend/
│  ├─ api.py               # FastAPI app (/health, /games)
│  ├─ scraper.py           # Minimal Steam scraping / parsing logic
│  └─ models.py            # Pydantic types (optional)
├─ tests/                  # pytest suites
├─ k8s/                    # Kubernetes YAML
│  ├─ namespace.yaml
│  ├─ deployment.yaml
│  └─ service.yaml
├─ .github/workflows/      # CI / CD pipelines
│  ├─ ci.yml
│  └─ cd.yml
├─ requirements.txt
├─ requirements-dev.txt
├─ Dockerfile              # multi-stage
└─ README.md
````

---

## Quick local run (no Docker)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

pytest -q                 # run tests
uvicorn backend.api:app --host 0.0.0.0 --port 8000

curl http://localhost:8000/health
curl "http://localhost:8000/games?rows=3"
```

---

## Docker (multi-stage)

Build the slim runtime image and try it:

```bash
docker build --target runtime -t steamscraper-backend:local .
docker run --rm -p 8000:8000 steamscraper-backend:local
curl http://localhost:8000/health
```

Multi-stage layout:

1. **base** → `python:3.12-slim`
2. **builder** → installs deps + (optionally) runs tests
3. **runtime** → copies only the venv + app code → smallest surface

---

## Kubernetes in a minute

```bash
kind create cluster --name steamscraper

kubectl apply -f k8s/
kubectl rollout status deploy/steamscraper-backend -n steamscraper

kubectl port-forward svc/steamscraper-backend -n steamscraper 8000:80
curl http://localhost:8000/health
```

The manifests use `/health` for liveness/readiness and default to two replicas.

---

## CI overview (`ci.yml`)

On pushes and PRs to `dev` / `main`, CI does:

1. Checkout
2. Set up Python 3.12
3. Install dependencies (+ dev dependencies)
4. **Lint** with `flake8` & **format check** with `black --check`
5. **Run tests** with `pytest`
6. Build the runtime Docker image
7. **Trivy scan** the image → fail on `HIGH` / `CRITICAL` vulnerabilities

---

## CD overview (`cd.yml`)

Runs only on `main` (and `workflow_dispatch` for demos):

1. Build runtime image → tag
   `ghcr.io/tem3lkov/steamscraper-backend:<sha>`
2. Log in & push the image to GHCR
3. Patch `deployment.yaml` to use that tag
4. `kubectl apply` manifests (cluster already running on self-hosted runner)
5. Wait for rollout, port-forward, call `/health` + `/games` → fail if not 200

---

## Security bits

* **CodeQL** – Python SAST, results under **Security → Code scanning**
* **Trivy** – scans the Docker image in CI; the pipeline fails if serious vulnerabilities appear
* Branch protection on `main` – PR + successful CI required, no force-push

---

## Roadmap ideas

Some things that could be added on top:

* Real Steam API calls & caching
* DB + migrations (PostgreSQL + Alembic)
* Front-end client with its own pipeline
