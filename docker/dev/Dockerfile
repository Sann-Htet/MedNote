FROM nvidia/cuda:11.8.0-devel-ubuntu22.04 as python-base

ENV PYTHONUNBUFFERED=1

# SYSTEM
RUN apt-get update --yes --quiet && DEBIAN_FRONTEND=noninteractive apt-get install --yes --quiet --no-install-recommends \
    software-properties-common \
    build-essential apt-utils \
    wget curl vim git ca-certificates kmod \
 && rm -rf /var/lib/apt/lists/*

# PYTHON 3.10
RUN add-apt-repository --yes ppa:deadsnakes/ppa && apt-get update --yes --quiet
RUN DEBIAN_FRONTEND=noninteractive apt-get install --yes --quiet --no-install-recommends \
    python3.11 \
    python3.11-dev \
    python3.11-distutils \
    python3.11-lib2to3 \
    python3.11-gdbm \
    python3.11-venv \
    python3.11-tk \
    pip
## ---------------------------------------------------------------------------------- ##
## ------------------------- Python base -------------------------------------------- ##
## ---------------------------------------------------------------------------------- ##
ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_ROOT_USER_ACTION=ignore \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 999 \
    && update-alternatives --config python3 && ln -s /usr/bin/python3 /usr/bin/python

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends git tini \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /root/.cache \
    && rm -rf /var/apt/lists/* \
    && rm -rf /var/cache/apt/* \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false\
    && mkdir -p /workspace/app \
    && pip install --quiet -U pip wheel setuptools virtualenv

## ---------------------------------------------------------------------------------- ##
## ------------------------- Python build base -------------------------------------- ##
## ---------------------------------------------------------------------------------- ##
FROM python-base AS build-base
ARG PDM_INSTALL_ARGS="-G:all"
ENV PDM_INSTALL_ARGS="${PDM_INSTALL_ARGS}" \
    GRPC_PYTHON_BUILD_WITH_CYTHON=1 \
    PATH="/workspace/app/.venv/bin:/usr/local/bin:$PATH"
## -------------------------- add build packages ----------------------------------- ##
RUN apt-get install -y --no-install-recommends build-essential curl \
    && apt-get install -y ffmpeg\
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /root/.cache \
    && rm -rf /var/apt/lists/* \
    && rm -rf /var/cache/apt/* \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false

## -------------------------- install application ----------------------------------- ##
WORKDIR /workspace/app
COPY pyproject.toml pdm.lock README.md .pre-commit-config.yaml Makefile \
    ./
RUN python -m venv --copies /workspace/app/.venv \
    && /workspace/app/.venv/bin/pip install pdm  \
    && pdm install ${PDM_INSTALL_ARGS} --no-self
COPY backend/ ./backend/

## ---------------------------------------------------------------------------------- ##
## -------------------------------- development build ------------------------------- ##
## ---------------------------------------------------------------------------------- ##
## ------------------------- use builder base --------------------------------------- ##
FROM build-base as dev-image
ARG ENV_SECRETS="runtime-secrets"
## --------------------------- standardize execution env ----------------------------- ##
ENV PATH="/workspace/app/.venv/bin:$PATH" \
    VIRTUAL_ENV="/workspace/app/.venv" \
    ENV_SECRETS="${ENV_SECRETS}"  \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8
WORKDIR /workspace/app
COPY backend ./backend/
RUN pdm install $PDM_INSTALL_ARGS
STOPSIGNAL SIGINT
EXPOSE 8000
ARG ENV_SECRETS="runtime-secrets"
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_SUBMISSION_ID
ARG AWS_SUBMISSION_KEY
ENV ENV_SECRETS="${ENV_SECRETS}"
ENTRYPOINT ["tini","--" ]
RUN aws configure set aws_access_key_id ${AWS_ACCESS_KEY_ID}
RUN aws configure set aws_secret_access_key ${AWS_SECRET_ACCESS_KEY}
RUN aws configure set aws_access_key_id ${AWS_SUBMISSION_ID} --profile "submission_vaai"
RUN aws configure set aws_secret_access_key ${AWS_SUBMISSION_KEY} --profile "submission_vaai"

CMD [ "litestar","run","--host","0.0.0.0"]
VOLUME /workspace/app
