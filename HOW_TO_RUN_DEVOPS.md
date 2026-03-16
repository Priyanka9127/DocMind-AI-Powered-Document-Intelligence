# How to Run the GenAI-Enhanced DevOps Platform

This guide outlines exactly how to run your newly enhanced platform. There are multiple ways to run it depending on what part of your DevOps skills you want to demonstrate.

## 1. The Containerized Way (Docker Compose)
*Best for: Showing you know how to package and run isolated environments.*

**Prerequisites:** 
- Docker Desktop must be installed and running.
- Ollama must be running locally (`ollama serve`).

**Steps:**
1. Open a terminal in this directory.
2. Build and start the container:
   ```bash
   docker-compose up --build
   ```
3. Access the application at: **http://localhost:8501**
4. To stop the application:
   ```bash
   docker-compose down
   ```

## 2. The GenAI Automation Layer (SRE Agent)
*Best for: Impressing interviewers with your ability to use AI for Operations.*

**Prerequisites:**
- Python must be installed.
- Required python packages must be installed (`pip install langchain-community langchain-core`).
- Ollama must be running locally.

**Demo 1: Auto-generate Kubernetes YAML**
```bash
python devops_agent.py generate "Create a Kubernetes deployment for a Redis cache with 2 replicas and 512Mi memory limits"
```

**Demo 2: Analyze a Crash Log**
1. Ensure you have a log file (e.g., `crash.txt` containing an error).
2. Run the analyzer:
```bash
python devops_agent.py analyze-logs -f crash.txt
```

## 3. The Enterprise Way (Kubernetes)
*Best for: Explaining your production deployment strategy.*

If you have a Kubernetes cluster running (like Minikube, Docker Desktop K8s, or GKE), run these commands in order:

```bash
# 1. Create the namespace
kubectl apply -f k8s/namespace.yaml

# 2. Setup Configuration
kubectl apply -f k8s/configmap-secret.yaml

# 3. Deploy Ollama
kubectl apply -f k8s/ollama-deployment.yaml

# 4. Deploy the DocMind Application
kubectl apply -f k8s/docmind-deployment.yaml

# 5. Expose via Service & Ingress
kubectl apply -f k8s/docmind-service-ingress.yaml

# 6. Apply Autoscaling rules
kubectl apply -f k8s/hpa.yaml

# 7. Deploy Observability (Monitoring)
kubectl apply -f k8s/prometheus.yaml
kubectl apply -f k8s/grafana.yaml
```

Once deployed, you can monitor the pods using `kubectl get pods -n docmind`.
