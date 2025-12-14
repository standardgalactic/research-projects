# Note: There isn't an "official" NixOS Docker base in the same sense as Debian/Fedora.
# The standard pattern is: use a minimal Linux base + install Nix, then define your env via flake/nixpkgs.
# This gives you Nix-style reproducibility *inside* the container.

FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
  ca-certificates curl xz-utils bash git make \
  && rm -rf /var/lib/apt/lists/*

# Install Nix (single-user install inside container)
ENV USER=root
RUN curl -L https://nixos.org/nix/install -o /tmp/install-nix.sh && \
    bash /tmp/install-nix.sh --no-daemon && \
    rm -f /tmp/install-nix.sh

# Activate Nix profile for subsequent RUN layers
SHELL ["/bin/bash", "-lc"]

# Install packages via nixpkgs
RUN nix-channel --add https://nixos.org/channels/nixpkgs-unstable nixpkgs && \
    nix-channel --update && \
    nix-env -iA nixpkgs.bash nixpkgs.git nixpkgs.gnumake nixpkgs.tmux nixpkgs.byobu nixpkgs.vim \
             nixpkgs.texliveFull nixpkgs.latexmk nixpkgs.ghostscript \
             nixpkgs.go nixpkgs.gcc

WORKDIR /opt/project
COPY tools /opt/project/tools
RUN /opt/project/tools/install_utils.sh

CMD ["/bin/bash", "-lc"]

