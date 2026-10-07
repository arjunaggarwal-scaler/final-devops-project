# Docker

The Dockerfiles live next to their build contexts under
[`application/backend/Dockerfile`](../application/backend/Dockerfile) and
[`application/frontend/Dockerfile`](../application/frontend/Dockerfile); the
local stack is wired together by [`../docker-compose.yml`](../docker-compose.yml).

## Images

| Service | Base | Build | Runs as |
|---------|------|-------|---------|
| backend | `python:3.12-slim` | multi-stage (venv builder → slim runtime) | non-root `appuser` (uid 10001) |
| frontend | `node:22-alpine` → `nginxinc/nginx-unprivileged:1.29-alpine` | multi-stage (Vite build → nginx) | non-root `nginx` (uid 101) |

Both images are **multi-stage** (build tooling stays out of the runtime image) and
**run as non-root**. Image CVEs are kept clean for the CI security gate:

- backend: pip/setuptools/wheel are removed from the final image (their vendored
  packages carried HIGH CVEs), and FastAPI/Starlette are pinned to patched versions.
- frontend: the base is `nginx-unprivileged:1.29-alpine` with `apk upgrade` to patch
  OpenSSL/libssl3/c-ares.

## Run the full stack locally

```bash
docker compose up --build        # frontend :22130, backend :22108, postgres :22132
docker compose ps                # all three services, containers prefixed s21-
docker compose down -v           # tear down + remove the postgres volume
```

The frontend container's nginx proxies `/api` to the backend using the `BACKEND_HOST`
environment variable (`backend` in Compose, `taskboard-backend` in Kubernetes), so the
same image works in both environments.
