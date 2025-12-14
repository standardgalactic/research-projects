# Spherepop Tools Makefile
# Explicit, local, reversible installation
# No networking, no build steps, no privilege escalation beyond install paths

PREFIX      ?= /usr/local
BINDIR      := $(PREFIX)/bin
MANDIR      := $(PREFIX)/share/man
MAN1DIR     := $(MANDIR)/man1

TOOLS := \
	sp-lab \
	sp-probe-goodhart \
	sp-drift-metrics \
	sp-check-invariants \
	sp-sim-observer \
	sp-audit-legibility \
	sp-probe-refusal \
	sp-sim-apprenticeship

MANPAGES := $(TOOLS:%=%.1)

.PHONY: all install uninstall reinstall man install-man uninstall-man check

all:
	@echo "Spherepop tools are scripts; nothing to build."
	@echo "Use: make install"

check:
	@echo "Checking executability..."
	@for t in $(TOOLS); do \
		test -x usr/bin/$$t || { echo "ERROR: usr/bin/$$t not executable"; exit 1; }; \
	done
	@echo "OK"

install: check install-bin install-man
	@echo "Installed Spherepop tools into $(PREFIX)"

install-bin:
	@echo "Installing tools into $(BINDIR)"
	@install -d $(BINDIR)
	@for t in $(TOOLS); do \
		install -m 0755 usr/bin/$$t $(BINDIR)/$$t; \
	done

install-man:
	@echo "Installing manpages into $(MAN1DIR)"
	@install -d $(MAN1DIR)
	@for m in $(MANPAGES); do \
		install -m 0644 usr/share/man/man1/$$m $(MAN1DIR)/$$m; \
	done
	@command -v mandb >/dev/null 2>&1 && mandb >/dev/null 2>&1 || true

edge-init:
	@sp-edge-init nodes/lab.json

edge-status:
	@sp-edge-list

edge-run:
	@sp-edge-run uptime

edge-demo:
	@sp-edge-lab demo

: uninstall-bin uninstall-man
	@echo "Uninstalled Spherepop tools from $(PREFIX)"

uninstall-bin:
	@echo "Removing tools from $(BINDIR)"
	@for t in $(TOOLS); do \
		rm -f $(BINDIR)/$$t; \
	done

uninstall-man:
	@echo "Removing manpages from $(MAN1DIR)"
	@for m in $(MANPAGES); do \
		rm -f $(MAN1DIR)/$$m; \
	done
	@command -v mandb >/dev/null 2>&1 && mandb >/dev/null 2>&1 || true

reinstall: uninstall install

