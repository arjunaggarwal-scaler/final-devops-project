# syntax=docker/dockerfile:1
# ---- Stage 1: build the React/Vite static bundle ----
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# ---- Stage 2: serve with the unprivileged Nginx image (runs as non-root) ----
# nginxinc/nginx-unprivileged runs as uid 101 and listens on 8080 (no root needed).
FROM nginxinc/nginx-unprivileged:1.29-alpine
# Patch OS packages (OpenSSL/libssl, c-ares, etc.) to clear HIGH/CRITICAL CVEs
# flagged by the image scanner. apk needs root, so upgrade before dropping to 101.
USER root
RUN apk upgrade --no-cache
# The image runs envsubst over /etc/nginx/templates/*.template at startup.
# These defaults suit Docker Compose; Kubernetes overrides BACKEND_HOST/DNS_RESOLVER.
ENV BACKEND_HOST=backend \
    DNS_RESOLVER=127.0.0.11
COPY --from=build /app/dist /usr/share/nginx/html
COPY default.conf.template /etc/nginx/templates/default.conf.template
EXPOSE 8080
USER 101
