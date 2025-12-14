FROM alpine:3.20

# Alpine caveats:
# - musl libc
# - TeX can be heavier; texlive-full is huge.
# We'll install a workable TeX + latexmk + fonts.

RUN apk add --no-cache \
  bash coreutils findutils grep sed gawk \
  git make \
  tzdata \
  byobu tmux vim \
  perl \
  python3 \
  ca-certificates \
  gcc musl-dev \
  go \
  # TeX (Alpine splits into many packages; this is a reasonable baseline)
  texlive texlive-latex texlive-latexextra texlive-fontsextra texlive-bibtexextra \
  texmf-dist \
  ghostscript \
  fontconfig ttf-dejavu \
  && update-ca-certificates

# Copy utilities and install into /usr/bin
WORKDIR /opt/project
COPY tools /opt/project/tools
RUN /opt/project/tools/install_utils.sh

ENV SHELL=/bin/bash
CMD ["/bin/bash"]

