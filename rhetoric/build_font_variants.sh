#!/usr/bin/env bash
#
# build_font_variants.sh
#
# Compiles a .tex file (default: vocabulary-of-acceleration.tex) once with
# its original fonts, then once more per local font family found in the
# current directory or a ./fonts subdirectory. Each variant swaps only
# \setmainfont; math, sans, and mono fonts are left untouched, since
# amsmath's math glyphs don't come from \setmainfont anyway.
#
# Font family detection: files are grouped by the part of the filename
# before -Regular / -Bold / -Italic / -BoldItalic. A bare "Name.ttf" with
# no such suffix is treated as that family's Regular weight. Missing
# Bold/Italic/BoldItalic files are synthesized by fontspec's FakeBold/
# FakeSlant rather than erroring.
#
# One font's failure (missing glyphs, corrupt file, whatever) is logged
# and skipped - it never aborts the rest of the batch.
#
# Usage:
#   ./build_font_variants.sh [source.tex]
#
set -uo pipefail   # deliberately NOT -e: a single xelatex failure must not
                    # kill the loop over the remaining fonts

SRC="${1:-vocabulary-of-acceleration.tex}"
BASE="$(basename "${SRC%.tex}")"
FONT_SEARCH_DIRS=(. fonts)
OUT_DIR="variants"
LOG="build_font_variants.log"

if [ ! -f "$SRC" ]; then
    echo "Source file not found: $SRC" >&2
    exit 1
fi

mkdir -p "$OUT_DIR"
: > "$LOG"

log() { echo "$1" | tee -a "$LOG"; }

############################################
# 1. Baseline build (original fonts, untouched)
############################################

log "==== Baseline build ($SRC) ===="
cp "$SRC" "$OUT_DIR/"
(
    cd "$OUT_DIR" || exit 1
    xelatex -interaction=nonstopmode "$(basename "$SRC")" >>"../$LOG" 2>&1
    xelatex -interaction=nonstopmode "$(basename "$SRC")" >>"../$LOG" 2>&1
)
if [ -s "$OUT_DIR/$BASE.pdf" ]; then
    log "  OK: baseline -> $OUT_DIR/$BASE.pdf"
else
    log "  FAILED: baseline (see $LOG)"
fi

############################################
# 2. Discover local font families
############################################
#
# Pass 1: anything matching a -Bold / -Italic / -BoldItalic / -Regular
# suffix is filed under that family name.
# Pass 2: any remaining bare "Name.ttf" becomes its own family's Regular,
# unless that family name was already claimed by a -Regular file (in
# which case the bare file is skipped and noted, rather than silently
# overwriting a more explicit match).

declare -A REGULAR BOLD ITALIC BOLDITALIC
declare -a BARE_CANDIDATES

for dir in "${FONT_SEARCH_DIRS[@]}"; do
    [ -d "$dir" ] || continue
    while IFS= read -r -d '' f; do
        base="$(basename "$f")"
        name="${base%.ttf}"
        case "$name" in
            *-BoldItalic) fam="${name%-BoldItalic}"; BOLDITALIC["$fam"]="$f" ;;
            *-Bold)       fam="${name%-Bold}";       BOLD["$fam"]="$f" ;;
            *-Italic)     fam="${name%-Italic}";     ITALIC["$fam"]="$f" ;;
            *-Regular)    fam="${name%-Regular}";    REGULAR["$fam"]="$f" ;;
            *)            BARE_CANDIDATES+=("$f") ;;
        esac
    done < <(find "$dir" -maxdepth 1 -type f -iname "*.ttf" -print0 2>/dev/null)
done

for f in "${BARE_CANDIDATES[@]:-}"; do
    [ -z "$f" ] && continue
    base="$(basename "$f")"
    name="${base%.ttf}"
    if [ -n "${REGULAR[$name]:-}" ]; then
        log "  note: skipping $f (family '$name' already has an explicit -Regular file)"
    else
        REGULAR["$name"]="$f"
    fi
done

log ""
log "Discovered families: ${!REGULAR[*]}"
log ""

############################################
# 3. Build one variant per family
############################################

for fam in "${!REGULAR[@]}"; do
    reg="${REGULAR[$fam]}"
    variant_base="${BASE}-${fam}"
    variant_tex="$OUT_DIR/${variant_base}.tex"

    # Stage the font files where Path=./ will find them at compile time.
    cp "$reg" "$OUT_DIR/" 2>/dev/null
    [ -n "${BOLD[$fam]:-}" ]       && cp "${BOLD[$fam]}" "$OUT_DIR/" 2>/dev/null
    [ -n "${ITALIC[$fam]:-}" ]     && cp "${ITALIC[$fam]}" "$OUT_DIR/" 2>/dev/null
    [ -n "${BOLDITALIC[$fam]:-}" ] && cp "${BOLDITALIC[$fam]}" "$OUT_DIR/" 2>/dev/null

    # Build the replacement \setmainfont line and patch the .tex with it.
    # Done in Python rather than sed: the replacement text contains
    # brackets and commas, which is exactly the kind of thing that turns
    # into a sed-escaping headache for no real benefit.
    python3 - "$SRC" "$variant_tex" "$reg" "${BOLD[$fam]:-}" "${ITALIC[$fam]:-}" "${BOLDITALIC[$fam]:-}" <<'PY'
import re, sys, os

src, dst, reg, bold, italic, bolditalic = sys.argv[1:7]

def base(p):
    return os.path.basename(p) if p else None

# FakeBold/FakeSlant must be scoped to the specific shape being synthesized
# (via BoldFeatures=/ItalicFeatures=/BoldItalicFeatures=), never passed as
# bare top-level options - a bare FakeSlant applies to every shape fontspec
# loads for this family, including plain upright body text, which is not
# what "fake the italic we don't have" is supposed to mean.
opts = ["Path=./"]

if bold:
    opts.append(f"BoldFont={base(bold)}")
else:
    opts.append("BoldFeatures={FakeBold=2.5}")

if italic:
    opts.append(f"ItalicFont={base(italic)}")
else:
    opts.append("ItalicFeatures={FakeSlant=0.2}")

if bolditalic:
    opts.append(f"BoldItalicFont={base(bolditalic)}")
elif bold and not italic:
    # We have a real bold face but no italic/bold-italic: fake the slant
    # on top of the real bold for the bold-italic shape.
    opts.append("BoldItalicFeatures={FakeSlant=0.2}")
elif italic and not bold:
    # We have a real italic face but no bold/bold-italic: fake the weight
    # on top of the real italic for the bold-italic shape.
    opts.append("BoldItalicFeatures={FakeBold=2.5}")
elif not bold and not italic:
    opts.append("BoldItalicFeatures={FakeBold=2.5,FakeSlant=0.2}")
# (if both bold and italic are real files, fontspec will look for a real
# BoldItalicFont; if none is given it falls back to the bold face as-is,
# which is a reasonable default we don't need to override.)

replacement = r"\setmainfont{%s}[%s]" % (base(reg), ",".join(opts))

with open(src, "r", encoding="utf-8") as f:
    content = f.read()

# Pass a function (not a string) as the repl argument: re.subn treats a
# string repl's backslash sequences as backreferences (\s, \1, etc.), which
# corrupts a literal replacement like "\setmainfont{...}". A function's
# return value is inserted verbatim, with no re-parsing.
new_content, n = re.subn(
    r"\\setmainfont\{[^}]*\}(\[[^\]]*\])?",
    lambda m: replacement,
    content,
    count=1,
)
if n == 0:
    sys.stderr.write("WARNING: no \\setmainfont line found to replace\n")

with open(dst, "w", encoding="utf-8") as f:
    f.write(new_content)
PY

    log "==== Building variant: $fam ===="
    (
        cd "$OUT_DIR" || exit 1
        xelatex -interaction=nonstopmode "${variant_base}.tex" >>"../$LOG" 2>&1
        xelatex -interaction=nonstopmode "${variant_base}.tex" >>"../$LOG" 2>&1
    )

    # A PDF existing is NOT sufficient evidence of success: xelatex in
    # nonstopmode survives a "font cannot be found" error by silently
    # falling back to a substitute font and still emitting a PDF. Grep
    # xelatex's own per-job log (not our combined transcript) for the
    # specific failure classes we care about.
    job_log="$OUT_DIR/${variant_base}.log"
    pdf="$OUT_DIR/${variant_base}.pdf"

    if [ -f "$job_log" ] && grep -q "Fatal error occurred\|Emergency stop" "$job_log"; then
        log "  FAILED: $fam (fatal error - see $job_log)"
    elif [ -f "$job_log" ] && grep -q "Package fontspec Error" "$job_log"; then
        log "  WARNING: $fam compiled but font was not found - PDF uses a FALLBACK font, not $(basename "$reg") (see $job_log)"
    elif [ -s "$pdf" ]; then
        log "  OK: $fam -> $pdf"
    else
        log "  FAILED: $fam (no PDF produced - see $LOG)"
    fi
done

############################################
# 4. Summary
############################################

log ""
log "==== Summary ===="
ok=$(grep -c "^  OK:" "$LOG")
warned=$(grep -c "^  WARNING:" "$LOG")
failed=$(grep -c "^  FAILED:" "$LOG")
total=$(( ${#REGULAR[@]} + 1 ))  # +1 for baseline
log "Total attempted     : $total"
log "OK (font used)      : $ok"
log "OK but fell back    : $warned   (compiled, but the requested font was not found - check filenames/paths)"
log "Failed              : $failed"
log "Output dir          : $OUT_DIR/"
log "Full log            : $LOG"
