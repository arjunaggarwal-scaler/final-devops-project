# GitOps with Argo CD

This directory contains the Argo CD `Application` that manages the TaskBoard
deployment using the **GitOps** model: Git is the single source of truth, and
Argo CD continuously reconciles the cluster to match what is committed.

## How it works

```
GitHub repo (helm/taskboard)  ─►  Argo CD Application  ─►  Kubernetes cluster
        (desired state)              (reconcile loop)          (actual state)
```

- `application.yaml` points Argo CD at `helm/taskboard` in this public repo.
- `syncPolicy.automated` with `prune` + `selfHeal` means:
  - a new commit to `main` is pulled and applied automatically (auto-sync),
  - resources deleted from Git are pruned from the cluster,
  - manual drift in the cluster is reverted back to the Git state (self-heal).

## Install Argo CD and apply the Application

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl apply -f gitops/application.yaml
```

Argo CD then reports the Application as **Synced** and **Healthy** once the
TaskBoard pods are running. Committing a change to the Helm chart (for example,
bumping `backend.replicaCount`) and pushing to `main` triggers an automatic
re-sync, with no `kubectl` or `helm` command needed.
