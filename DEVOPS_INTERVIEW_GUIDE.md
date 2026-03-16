# DevOps Interview Guide: DocMind Tools & Process

This document is your cheat sheet for answering common DevOps interview questions about your platform's architecture and operational lifecycle.

## Section 1: The Tools

### Docker & Docker Compose (Containerization)
*   **Why you used it:** To solve the "it works on my machine" problem and create isolated, reproducible development environments.
*   **How you used it:** 
    *   Wrote a `Dockerfile` to package the Python code, PyPDF2, and Streamlit dependencies into a lightweight image (`python:3.9-slim`).
    *   Used `docker-compose.yml` to define network mapping so the containerized application could easily communicate with the host machine's Ollama AI server.

### Kubernetes (Container Orchestration)
*   **Why you used it:** To manage the application at scale in a production-like environment. Docker alone can't handle load balancing or self-healing if a container crashes under load.
*   **How you used it:**
    *   Wrote `.yaml` manifests to define the desired state of the infrastructure.
    *   Used a `Deployment` manifest to spin up replicas of the application to handle high traffic robustly.
    *   Used `Service` and `Ingress` manifests to expose those internal pods securely to external users.
    *   Used a `HorizontalPodAutoscaler` (HPA) to automatically scale the number of application pods up or down based on CPU utilization metrics.

### Prometheus (Monitoring & Observability)
*   **Why you used it:** To get real-time visibility into the health and performance of the application.
*   **How you used it:** 
    *   Imported the `prometheus_client` Python package directly into the application code (`app.py`).
    *   Created custom application metrics: a `Counter` to track total user requests, and a `Histogram` to measure the latency (speed) of the Large Language Model responses.
    *   Exposed an `/metrics` HTTP endpoint that the Prometheus server automatically scrapes.

### Grafana (Visualization)
*   **Why you used it:** Because raw Prometheus metric text is hard to read. Grafana turns metric text into visual dashboards for Site Reliability and DevOps teams.
*   **How you used it:** Deployed Grafana into the Kubernetes cluster alongside Prometheus. It connects to the Prometheus database and runs PromQL queries to display graphs of API latencies and request volumes.

### LangChain & ChromaDB (AI Engineering)
*   **Why you used it:** LangChain provides the framework to connect user input to AI models. ChromaDB provides specialized vector storage needed for AI search.
*   **How you used it:** LangChain splits uploaded PDFs into smaller text chunks, converts them to vector embeddings using DeepSeek, and stores them locally on disk using ChromaDB to enable rapid Similarity Searching.

### Ollama & DeepSeek (Local AI)
*   **Why you used it:** To run a powerful Large Language Model (`deepseek-r1:1.5b`) entirely locally, avoiding cloud API costs (like OpenAI) and ensuring Data Privacy when analyzing internal documents.
*   **How you used it:** Ran the Ollama server as the backend brain. The main application uses it to answer questions, and the `devops_agent.py` script uses it as an SRE tool to automate DevOps tasks like writing Kubernetes YAML and debugging crash logs.

---

## Section 2: The End-to-End Flow (CI/CD Narrative)

If the interviewer asks, *"Walk me through the lifecycle of how a change makes it to production"* or *"Describe your deployment pipeline"*, you can narrate this exact flow:

1.  **Code & Commit:** I write application updates in Python or modify my Terraform/Kubernetes configuration files locally and commit them to Git.
2.  **Local Testing (Docker):** Before deploying anywhere, I run `docker-compose up --build` to spin up the container locally and verify that my changes didn't break the application functionality.
3.  **The CI Pipeline (Theory):** _(Note: Explain this as design intent if you aren't currently using GitHub Actions)_ "In this enterprise setting, pushing code to version control triggers a CI pipeline. The pipeline automatically runs `docker build`, executes unit tests, and pushes the new image tag to an AWS ECR or Docker Hub container registry."
4.  **Configuration Update:** I update my Kubernetes `docmind-deployment.yaml` file to point to the newly published image tag.
5.  **Deployment (Kubernetes):** I use the `kubectl apply -f k8s/` command to apply the updated configurations to my cluster. Kubernetes performs a rolling update, gracefully shutting down old pods and spinning up new ones, achieving zero-downtime deployment.
6.  **Monitoring (SRE):** Once deployed, I monitor the new release using my Grafana dashboards. Specifically, I watch my custom Prometheus metric for `docmind_llm_response_seconds` to ensure the new application code hasn't introduced latency regressions for the end-user.
