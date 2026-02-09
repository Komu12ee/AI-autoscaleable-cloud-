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

## 📊 Verification
To verify the core logic without a full cluster deployment, you can run the unit tests:

```bash
python3 firm/verify_aware.py
```
This tests the:
-   Meta-Learner embedding generation.
-   Bootstrapper logic switching.
-   MPA Controller scaling wrapper.

## 📂 Project Structure
-   `firm/ddpg/`: Contains the Reinforcement Learning agent code (`main.py`, `ddpg.py`, `actorcritic.py`).
-   `firm/aware/`: Contains AWARE-specific modules (`meta_learner.py`, `bootstrapper.py`, `mpa.py`).
-   `firm/k8s/`: Kubernetes manifest files.
-   `firm/metrics/`: Code for the metric collector.
-   `firm/server.py`: The gRPC server running in the cluster.

## ⚠️ Troubleshooting

-   **`ModuleNotFoundError`**: Ensure you are running python from the same environment where you installed `pip` packages. On some systems, use `/usr/bin/python3`.
-   **Connection Refused**: Check if `kubectl port-forward` is running and active.
-   **ImagePullBackOff**: Ensure `firm-server:latest` was built locally and is available to your Kubernetes cluster (easy with Docker Desktop; for Minikube use `eval $(minikube docker-env)` before building).

---
*Based on the paper: "AWARE: Automate Workload Autoscaling with Reinforcement Learning in Production Cloud Systems", USENIX ATC '23.*
