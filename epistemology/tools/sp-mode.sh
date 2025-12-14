#!/bin/sh
#
# sp-mode.sh
#
# Mandatory mode selection for epistemically ambiguous tools.
#

###############################################################################
# Defaults
###############################################################################

SP_MODE="satire"

###############################################################################
# Parse --mode flag
###############################################################################

sp_parse_mode() {
	for arg in "$@"; do
		case "$arg" in
			--mode=satire)
				SP_MODE="satire"
				;;
			--mode=instrument)
				SP_MODE="instrument"
				;;
			--mode=*)
				echo "[sp-mode] error: invalid mode '$arg'" >&2
				exit 1
				;;
		esac
	done
}

###############################################################################
# Enforcement
###############################################################################

sp_require_mode() {
	case "$SP_MODE" in
		satire|instrument)
			;;
		*)
			echo "[sp-mode] error: mode not set" >&2
			exit 1
			;;
	esac
}

###############################################################################
# Mode guards
###############################################################################

sp_assert_satire_only() {
	[ "$SP_MODE" = "satire" ] || {
		echo "[sp-mode] error: this feature is satire-only" >&2
		exit 1
	}
}

sp_assert_instrument_only() {
	[ "$SP_MODE" = "instrument" ] || {
		echo "[sp-mode] error: this feature requires instrument mode" >&2
		exit 1
	}
}

