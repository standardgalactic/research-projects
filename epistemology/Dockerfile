# Dockerfile
# Minimal LaTeX toolchain for deterministic builds.

FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    make \
    bash \
    git \
    texlive-latex-recommended \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-science \
    texlive-bibtex-extra \
    biber \
    latexmk \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /work

