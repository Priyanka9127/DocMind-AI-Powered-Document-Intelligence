#!/usr/bin/env python3
import os
import argparse
import sys
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

def get_llm():
    """Initialize the connection to Ollama DeepSeek."""
    return Ollama(
        model="deepseek-r1:1.5b",
        base_url=OLLAMA_BASE_URL,
        temperature=0.2 # Lower temperature for analytical/coding tasks
    )

def clean_response(response):
    """Clean <think> tags from model response."""
    if "<think>" in response:
        return response.split("</think>")[-1].strip()
    return response.strip()

def analyze_logs(log_text):
    """Use GenAI to analyze Kubernetes or application logs."""
    llm = get_llm()
    
    template = """You are an expert DevOps and Site Reliability Engineer (SRE).
Please analyze the following application/Kubernetes logs, identify the root cause of the error or crash, and suggest actionable remediation steps.

LOGS:
{log_text}

ROOT CAUSE ANALYSIS AND SUGGESTED FIX:"""
    
    prompt = PromptTemplate(template=template, input_variables=["log_text"])
    chain = prompt | llm
    
    print("🤖 Agent is analyzing logs...")
    response = chain.invoke({"log_text": log_text})
    
    print("\n" + "="*50)
    print("📊 INCIDENT ANALYSIS REPORT")
    print("="*50)
    print(clean_response(response))
    print("="*50 + "\n")

def generate_manifest(description):
    """Use GenAI to generate K8s manifests from natural language."""
    llm = get_llm()
    
    template = """You are an expert Kubernetes Administrator.
Please generate standard Kubernetes YAML manifests for the following request. Do not include any explanation outside the YAML block. Use best practices (resource limits, labels, health checks).

IMPORTANT: You MUST output valid Kubernetes YAML with `apiVersion`, `kind`, `metadata`, and `spec`. 

Example Format:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: example-app
spec:
  replicas: 1
  # ... rest of spec
```

REQUEST: {description}

KUBERNETES YAML MANIFEST:"""
    
    prompt = PromptTemplate(template=template, input_variables=["description"])
    chain = prompt | llm
    
    print(f"🤖 Agent is generating YAML for: '{description}'...")
    response = chain.invoke({"description": description})
    
    print("\n" + "="*50)
    print("📦 GENERATED KUBERNETES MANIFEST")
    print("="*50)
    print(clean_response(response))
    print("="*50 + "\n")

def main():
    parser = argparse.ArgumentParser(description="GenAI DevOps Auto-Remediation Agent for DocMind")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Analyze logs sub-command
    log_parser = subparsers.add_parser("analyze-logs", help="Analyze logs from a file or stdin")
    log_parser.add_file_or_group = log_parser.add_mutually_exclusive_group(required=True)
    log_parser.add_file_or_group.add_argument("-f", "--file", type=str, help="Path to log file")
    log_parser.add_file_or_group.add_argument("-t", "--text", type=str, help="Raw log text to analyze")
    
    # Generate manifest sub-command
    gen_parser = subparsers.add_parser("generate", help="Generate K8s manifests or Terraform code")
    gen_parser.add_argument("description", type=str, help="Natural language description of what to generate")
    
    args = parser.parse_args()
    
    if args.command == "analyze-logs":
        log_content = ""
        if args.file:
            try:
                with open(args.file, 'r') as f:
                    log_content = f.read()
            except Exception as e:
                print(f"Error reading file: {e}")
                sys.exit(1)
        elif args.text:
            log_content = args.text
            
        analyze_logs(log_content)
        
    elif args.command == "generate":
        generate_manifest(args.description)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
