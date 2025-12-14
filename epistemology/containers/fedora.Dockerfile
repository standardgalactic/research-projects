FROM fedora:41

RUN dnf -y update && dnf -y install \
  bash coreutils findutils grep sed gawk \
  git make \
  byobu tmux vim-enhanced \
  perl python3 \
  gcc \
  golang \
  # TeX
  texlive-scheme-full latexmk \
  ghostscript \
  dejavu-sans-fonts dejavu-serif-fonts \
  && dnf clean all

WORKDIR /opt/project
COPY tools /opt/project/tools
RUN /opt/project/tools/install_utils.sh

CMD ["/bin/bash"]

