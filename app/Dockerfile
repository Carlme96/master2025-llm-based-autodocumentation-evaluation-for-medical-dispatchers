FROM python:3.13.2-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:0.6.1 /uv /uvx /bin/

WORKDIR /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

# Copy the project into the image
ADD . /app
RUN apt update && apt install -y libsm6 libxext6 ffmpeg libfontconfig1 libxrender1 libgl1-mesa-glx
# Sync the project into a new environment, using the frozen lockfile

EXPOSE 8000

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen