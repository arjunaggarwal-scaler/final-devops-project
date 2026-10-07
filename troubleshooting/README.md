# Troubleshooting Challenge

**Name:** Arjun Aggarwal  **Roll No:** 24BCS10109

This document records five issues that were **intentionally introduced** into the
running TaskBoard deployment on the Kubernetes cluster, and for each one: how it
was identified, investigated, the root cause, the fix, and the verification. Every
screenshot below is from a real `kubectl` session against the live cluster.

> Argo CD auto-sync was temporarily disabled during this exercise so the broken
> state would persist long enough to diagnose (otherwise self-heal reverts it).

| # | Fault injected | Symptom | Root cause |
|---|----------------|---------|------------|
| 1 | Wrong image tag | Pod `ImagePullBackOff` | Image tag does not exist in GHCR |
| 2 | Service selector mismatch | `/api` unreachable, empty Endpoints | Selector no longer matches pod labels |
| 3 | Bad Secret (DB password) | Backend `CrashLoopBackOff` | `DATABASE_URL` has the wrong password |
| 4 | Failing readiness path | Pod stuck `0/1`, rollout stalls | `readinessProbe` points at a 404 path |
| 5 | Oversized resource request | Pod stuck `Pending` | `requests.cpu` exceeds node allocatable |

---

## Issue 1 — Wrong image tag → `ImagePullBackOff`

**Identify & Investigate.** After a deploy, a new backend pod never becomes ready.
`kubectl get pods` shows `ImagePullBackOff`; `kubectl describe pod` Events show the
kubelet failing to pull the image.

**Root cause.** The Deployment references
`…/final-devops-project-backend:v9.9.9-does-not-exist`, a tag that was never pushed.

**Fix.** Point the container back at the real tag:
```bash
kubectl set image deploy/taskboard-taskboard-backend \
  backend=ghcr.io/arjunaggarwal-scaler/final-devops-project-backend:local -n taskboard
```

**Verify.** The rollout completes and all backend pods are `Running`.

![diagnosis](../screenshots/s21-21-ts1-image-before.png)
![fix](../screenshots/s21-22-ts1-image-after.png)

---

## Issue 2 — Service selector mismatch → no Endpoints

**Identify & Investigate.** The app returns errors through the Ingress for `/api`.
`kubectl get endpoints taskboard-backend` shows **no endpoints**, even though the
backend pods are healthy.

**Root cause.** The Service selector was changed to `app: taskboard-backend-WRONG`,
which matches no pods, so the Service has no endpoints to route to.

**Fix.**
```bash
kubectl patch svc taskboard-backend -n taskboard --type merge \
  -p '{"spec":{"selector":{"app":"taskboard-backend"}}}'
```

**Verify.** Endpoints repopulate and `/api/tasks` returns `200` again.

![diagnosis](../screenshots/s21-23-ts2-service-before.png)
![fix](../screenshots/s21-24-ts2-service-after.png)

---

## Issue 3 — Bad Secret → database authentication failure

**Identify & Investigate.** The backend goes into `CrashLoopBackOff`. `kubectl logs`
shows a `psycopg.OperationalError` — password authentication failed for the Postgres user.

**Root cause.** The `DATABASE_URL` key in the `taskboard-taskboard-secret` Secret was
set to the wrong password (`WRONGPASS`), so the backend cannot open a DB connection.

**Fix.**
```bash
kubectl patch secret taskboard-taskboard-secret -n taskboard --type merge \
  -p '{"stringData":{"DATABASE_URL":"postgresql+psycopg://taskboard:taskboard@taskboard-postgres:5432/taskboard"}}'
kubectl rollout restart deploy/taskboard-taskboard-backend -n taskboard
```

**Verify.** Pods become `Running` and `/api/tasks/stats` returns data from Postgres.

![diagnosis](../screenshots/s21-25-ts3-secret-before.png)
![fix](../screenshots/s21-26-ts3-secret-after.png)

---

## Issue 4 — Failing readiness probe path → pods never Ready

**Identify & Investigate.** A new backend pod stays `0/1 READY` and the rollout never
completes. `kubectl describe pod` shows repeated `Readiness probe failed: HTTP 404`.

**Root cause.** The `readinessProbe.httpGet.path` was changed to `/not-a-real-path`,
which the backend answers with 404, so Kubernetes never marks the pod Ready.

**Fix.**
```bash
kubectl patch deploy taskboard-taskboard-backend -n taskboard --type json \
  -p '[{"op":"replace","path":"/spec/template/spec/containers/0/readinessProbe/httpGet/path","value":"/ready"}]'
```

**Verify.** Pods become `1/1 READY` and the rollout finishes.

![diagnosis](../screenshots/s21-27-ts4-readiness-before.png)
![fix](../screenshots/s21-28-ts4-readiness-after.png)

---

## Issue 5 — Oversized resource request → pod stuck `Pending`

**Identify & Investigate.** A new backend pod is stuck `Pending`. `kubectl describe pod`
shows `FailedScheduling … 0/1 nodes are available: 1 Insufficient cpu`.

**Root cause.** `requests.cpu` (and `limits.cpu`) were set to `100` cores, far more than
the single kind node's allocatable CPU (15), so the scheduler cannot place the pod.

**Fix.**
```bash
kubectl patch deploy taskboard-taskboard-backend -n taskboard --type json \
  -p '[{"op":"replace","path":"/spec/template/spec/containers/0/resources/requests/cpu","value":"100m"},
       {"op":"replace","path":"/spec/template/spec/containers/0/resources/limits/cpu","value":"500m"}]'
```

**Verify.** The pod schedules and the whole app returns to a healthy state.

![diagnosis](../screenshots/s21-29-ts5-pending-before.png)
![fix](../screenshots/s21-30-ts5-pending-after.png)

---

## Lessons learned

- **`kubectl describe` Events** are the fastest way to diagnose `ImagePullBackOff`,
  `FailedScheduling`, and probe failures — the reason is right there.
- **Empty Endpoints** almost always mean a Service selector / pod label mismatch.
- **CrashLoopBackOff** → read the container **logs**; config/secret problems surface there.
- Probe failures keep a pod out of Service rotation without killing it, which is exactly
  what readiness probes are for — but a wrong path makes the rollout hang silently.
- Resource requests are a scheduling contract: ask for more than a node has and the pod
  waits forever in `Pending`.
