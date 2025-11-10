FROM haskell:9.4.5-bullseye
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl git build-essential libgmp-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /usr/src/app
COPY stack.yaml package.yaml ebssc.cabal ./
COPY src/ src/
COPY app/ app/
COPY README.md README.md
RUN stack setup --upgrade-cabal
RUN stack build --copy-bins
ENTRYPOINT ["/bin/bash"]
