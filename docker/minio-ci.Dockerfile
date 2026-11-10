FROM debian:bookworm-slim

ARG MINIO_VERSION=RELEASE.2025-04-22T22-12-26Z
ARG MC_VERSION=RELEASE.2025-08-13T08-35-41Z

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

# Download the pinned ARM64 MinIO server and mc releases from official GitHub
# release assets, then verify each binary against its published SHA-256 file.
RUN set -eux; \
    minio_asset="minio.linux-arm64.${MINIO_VERSION}"; \
    minio_url="https://github.com/minio/minio/releases/download/${MINIO_VERSION}/${minio_asset}"; \
    curl -fL "${minio_url}" -o /usr/local/bin/minio; \
    curl -fL "${minio_url}.sha256sum" -o /tmp/minio.sha256sum; \
    minio_sha="$(awk '{print $1}' /tmp/minio.sha256sum)"; \
    printf '%s  %s\n' "${minio_sha}" /usr/local/bin/minio | sha256sum -c -; \
    mc_asset="mc.linux-arm64.${MC_VERSION}"; \
    mc_url="https://github.com/minio/mc/releases/download/${MC_VERSION}/${mc_asset}"; \
    curl -fL "${mc_url}" -o /usr/local/bin/mc; \
    curl -fL "${mc_url}.sha256sum" -o /tmp/mc.sha256sum; \
    mc_sha="$(awk '{print $1}' /tmp/mc.sha256sum)"; \
    printf '%s  %s\n' "${mc_sha}" /usr/local/bin/mc | sha256sum -c -; \
    chmod 0755 /usr/local/bin/minio /usr/local/bin/mc; \
    minio --version; \
    mc --version

EXPOSE 9000 9001

ENTRYPOINT ["minio"]
