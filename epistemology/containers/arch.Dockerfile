FROM archlinux:latest

# Arch caveat: rolling release. Good for "fresh", bad for reproducibility.
RUN pacman -Syu --noconfirm && pacman -S --noconfirm \
  bash coreutils findutils grep sed gawk \
  git make \
  byobu tmux vim \
  perl python \
  gcc \
  go \
  texlive texlive-latexextra texlive-fontsextra texlive-bibtexextra \
  ghostscript \
  ttf-dejavu \
  && pacman -Scc --noconfirm

WORKDIR /opt/project
COPY tools /opt/project/tools
RUN /opt/project/tools/install_utils.sh

CMD ["/bin/bash"]

