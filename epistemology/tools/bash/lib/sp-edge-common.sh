#!/bin/sh
#
# sp-edge-common.sh
#
# Shared epistemic safeguards and utilities for sp-edge tools.
#
# This file MUST be sourced by all sp-edge-* commands.
# It is intentionally minimal, explicit, and non-configurable.
#

###############################################################################
# Epistemic Runtime Banner
###############################################################################

sp_edge_banner() {
	cat <<'EOF'
[sp-edge] Cooperative edge execution on explicitly declared nodes only.
[sp-edge] No discovery, probing, inference, or diagnosis is performed.
[sp-edge] Output reflects direct command execution only.
EOF
}

###############################################################################
# Mandatory Banner Enforcement
###############################################################################

# Emit banner unless explicitly suppressed for non-interactive contexts
# (e.g., scripting). Suppression must be intentional.
if [ "${SP_EDGE_NO_BANNER:-0}" -ne 1 ]; then
	sp_edge_banner >&2
fi

###############################################################################
# Utility Guards
###############################################################################

sp_edge_die() {
	echo "[sp-edge] error: $*" >&2
	exit 1
}

sp_edge_require_file() {
	[ -f "$1" ] || sp_edge_die "required file not found: $1"
}

sp_edge_require_dir() {
	[ -d "$1" ] || sp_edge_die "required directory not found: $1"
}

###############################################################################
# SSH Defaults (Non-Escalating, Non-Persistent)
###############################################################################

SP_EDGE_SSH_OPTS="
-o BatchMode=yes
-o ConnectTimeout=5
-o StrictHostKeyChecking=accept-new
"

###############################################################################
# Safety Assertions
###############################################################################

sp_edge_assert_declared_host() {
	host="$1"
	config="$2"

	grep -q "\"host\"[[:space:]]*:[[:space:]]*\"$host\"" "$config" || \
		sp_edge_die "host '$host' not declared in $config"
}

