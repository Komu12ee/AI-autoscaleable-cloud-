# AWARE: Automate Workload Autoscaling with Reinforcement Learning

This repository contains a replication of the **AWARE** framework (USENIX ATC '23) built on top of the **FIRM** framework. It implements an intelligent autoscaling agent for Kubernetes that leverages:
1.  **Reinforcement Learning (RL)**: To learn optimal scaling policies.
2.  **Meta-Learning**: To adapt quickly to new workloads using latent embeddings.
3.  **Bootstrapping**: To safely transition from heuristic-based (HPA/VPA) control to RL-based control.

## 🏗 Architecture

The system consists of the following components:
-   **Firm Server**: A central controller deployed in the Kubernetes cluster that interfaces with the RL agent and manages scaling actions.
-   **Metric Collector**: A DaemonSet that gathers real-time resource usage metrics (CPU, Memory) from nodes and pods, storing them in Redis.
-   **RL Agent (DDPG)**: An actor-critic agent running externally (or in-cluster) that decides scaling actions based on state observations.
-   **Meta-Learner**: An RNN module that processes workload trajectories to generate embeddings for the RL agent.
-   **MPA Wrapper**: A custom environment wrapper that translating RL actions into Kubernetes scaling operations.

## 🚀 Prerequisites

Before running the project, ensure you have the following installed:

-   **Kubernetes Cluster**: A running cluster (e.g., Docker Desktop, Minikube, Kind, or bare-metal).
    -   *Verified on Docker Desktop Kubernetes v1.30+*
-   **Python 3.10+**: For running the RL agent.
-   **Docker**: To build the `firm-server` image.
-   **kubectl**: Configured to access your cluster.

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd cloud-computing-research
```

### 2. Install Python Dependencies
Install the required packages for the RL agent. Note: We use the CPU version of PyTorch for lighter installation.

```bash
# Install PyTorch (CPU)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Install other requirements
pip install kubernetes redis grpcio protobuf matplotlib ipython
```

### 3. Kubernetes Setup

1.  **Build the Docker Image**:
    The `firm-server` image contains the controller logic. Build it locally so your cluster can access it (if using Docker Desktop/Minikube).
    ```bash
    docker build -t firm-server:latest -f Dockerfile .
    ```

2.  **Deploy Infrastructure**:

    Apply the Kubernetes manifests to set up Redis, Permissions, and the FIRM components.
    ```bash
    # Permissions and Database
    kubectl apply -f firm/k8s/rbac.yaml
    kubectl apply -f firm/k8s/redis.yaml

    # AWARE Components
    kubectl apply -f firm/k8s/collector.yaml
    kubectl apply -f firm/k8s/firm-server.yaml
    ```

3.  **Verify Deployment**:
    Ensure all pods are running:
    ```bash
    kubectl get pods
    ```
    *Note: It may take a minute for `firm-server` and `collector` to start.*

## 🏃‍♂️ Running the Agent

### 1. Port Forwarding
Since the RL agent runs locally on your machine, it needs to communicate with the `firm-server` service inside the cluster. Open a separate terminal and run:

```bash
kubectl port-forward svc/firm-server 50051:50051
```
*Keep this terminal open.*

### 2. Start the RL Training
In your main terminal, execute the training script:

```bash
python3 firm/ddpg/main.py
```

### Training Phases
The agent will proceed through two main phases:
1.  **Bootstrapping (Offline Mode)**:
    -   The agent uses a Heuristic Controller (mimicking Kubernetes HPA/VPA).
    -   It collects "safe" trajectories to populate its replay buffer.
    -   *Duration: Default 50 episodes.*
2.  **RL Adaptation (Online Mode)**:
    -   The agent switches to the DDPG policy.
    -   The Meta-Learner generates embeddings based on observed workload patterns.
    -   The agent continuously learns and optimizes scaling actions.

## 🚀 Process to Run on Existing Infrastructure

Since you already have a **Kubernetes Cluster** and **Docker** running, follow these steps to deploy and run the AWARE agent.

### 1. Verify Your Cluster
First, ensure your cluster is active and you can access it.

```bash
# Check if nodes are ready
kubectl get nodes

# Check existing pods (should show kube-system pods at minimum)
kubectl get pods -A
```

### 2. Deploy AWARE Components
Apply the configuration files to deploy the Redis database, Metric Collector, and Firm Server to your cluster.

```bash
# 1. Setup Permissions and Database
kubectl apply -f firm/k8s/rbac.yaml
kubectl apply -f firm/k8s/redis.yaml

# 2. Deploy AWARE logic
kubectl apply -f firm/k8s/collector.yaml
kubectl apply -f firm/k8s/firm-server.yaml
```
*Note: These commands are idempotent. If you have already run them, running them again is safe and helpful to ensure everything is up to date.*

### 3. Verify Deployment
Check that the AWARE pods are running. You should see `firm-server` and `resource-collector` in the output.

```bash
kubectl get pods
```
-   **Pending**: The cluster is downloading images or waiting for resources. Wait a moment.
-   **Running**: The pod is ready.
-   **Error/CrashLoop**: Check logs with `kubectl logs <pod-name>`.

### 4. Connect to the Server
The RL agent runs on your local machine (Python) and needs to talk to the `firm-server` in the cluster. usage **Port Forwarding**:

```bash
# Open a NEW terminal window and run:
kubectl port-forward svc/firm-server 50051:50051
```
> **Keep this terminal open!** If you close it, the connection breaks.
> Expected output: `Forwarding from 127.0.0.1:50051 -> 50051`

### 5. Run the RL Agent
Now, in your **main terminal**, start the training script:

```bash
# Navigate to the correct directory if needed
# cd cloud-computing-research

python3 firm/ddpg/main.py
```

### 6. Verify Execution
If successful, you will see output like this in your main terminal:
```text
Training started...
Episode: 0 | Reward: -150
...
```
This confirms the agent is receiving state from Kubernetes and sending actions back.

## 📊 Verification & Analysis

1.  **Unit Tests** (Logic only):
    ```bash
    python3 firm/verify_aware.py
    ```

2.  **Training Progress Analysis** (Requires Checkpoints):
    If you have started training, you can analyze the rewards to check for learning improvements:
    ```bash
    /usr/bin/python3 firm/ddpg/analyze_training.py
    ```
    -   **Expected**: Rewards should increase over time.
    -   **Bad Sign**: Constant rewards (e.g., flat 1500) indicate the agent is not learning or inputs are broken.

## 📂 Project Structure
-   `firm/ddpg/`: Contains the Reinforcement Learning agent code (`main.py`, `ddpg.py`, `actorcritic.py`).
-   `firm/aware/`: Contains AWARE-specific modules (`meta_learner.py`, `bootstrapper.py`, `mpa.py`).
-   `firm/k8s/`: Kubernetes manifest files.
-   `firm/metrics/`: Code for the metric collector.
-   `firm/server.py`: The gRPC server running in the cluster.

## ⚠️ Troubleshooting

-   **`ModuleNotFoundError`**:
    -   Cause: Python environment mismatch.
    -   Fix: Use the system Python.
    ```bash
    /usr/bin/python3 firm/ddpg/main.py
    ```

-   **`kubectl: command not found`**:
    -   Cause: `kubectl` is not installed or not in PATH.
    -   Fix: Install via snap.
    ```bash
    sudo snap install kubectl --classic
    ```

-   **`Error from server (NotFound): services "firm-server" not found`**:
    -   Cause: The AWARE components are not deployed in the cluster.
    -   Fix: Deploy the manifests.
    ```bash
    kubectl apply -f firm/k8s/rbac.yaml
    kubectl apply -f firm/k8s/redis.yaml
    kubectl apply -f firm/k8s/collector.yaml
    kubectl apply -f firm/k8s/firm-server.yaml
    ```

-   **`Connection Refused`** or **`grpc._channel._InactiveRpcError`**:
    -   Cause: The local agent cannot reach the cluster.
    -   Fix: Ensure port forwarding is running in a separate terminal.
    ```bash
    kubectl port-forward svc/firm-server 50051:50051
    ```

-   **`ImagePullBackOff`**:
    -   Cause: The `firm-server` image is missing or cannot be pulled.
    -   Fix: Build the image locally (if using Docker Desktop/Minikube).
    ```bash
    docker build -t firm-server:latest -f Dockerfile .
    # For Minikube, run `eval $(minikube docker-env)` first.
    ```

---
*Based on the paper: "AWARE: Automate Workload Autoscaling with Reinforcement Learning in Production Cloud Systems", USENIX ATC '23.*
