# ============================================================
# Unified Makefile for RSVP Monograph (3 volumes + master PDF)
# Assumes:
#   - latexmk + lualatex + biber
#   - .latexmkrc in project root
#   - pdfunite installed (poppler-utils)
# ============================================================

# Volume main files
VOL1 = Volume-I-Foundations/main-vol1.tex
VOL2 = Volume-II-Applications/main-vol2.tex
VOL3 = Volume-III-Extensions/main-vol3.tex

# Output PDFs (latexmk will generate)
OUT1 = Volume-I-Foundations/main-vol1.pdf
OUT2 = Volume-II-Applications/main-vol2.pdf
OUT3 = Volume-III-Extensions/main-vol3.pdf

# Final joined PDF
MASTER = RSVP-Monograph.pdf

.PHONY: all vol1 vol2 vol3 clean distclean master

# ------------------------------------------------------------
# Build everything
# ------------------------------------------------------------
all: vol1 vol2 vol3 master

# ------------------------------------------------------------
# Individual builds
# ------------------------------------------------------------
vol1:
	cd Volume-I-Foundations && latexmk

vol2:
	cd Volume-II-Applications && latexmk

vol3:
	cd Volume-III-Extensions && latexmk

# ------------------------------------------------------------
# Master document
# ------------------------------------------------------------
master: $(OUT1) $(OUT2) $(OUT3)
	pdfunite $(OUT1) $(OUT2) $(OUT3) $(MASTER)
	@echo ""
	@echo "======================================================"
	@echo "  MASTER PDF created successfully: $(MASTER)"
	@echo "======================================================"
	@echo ""

# ------------------------------------------------------------
# Clean up auxiliary files but keep PDFs
# ------------------------------------------------------------
clean:
	cd Volume-I-Foundations       && latexmk -c
	cd Volume-II-Applications     && latexmk -c
	cd Volume-III-Extensions      && latexmk -c

# ------------------------------------------------------------
# Remove everything including PDFs
# ------------------------------------------------------------
distclean:
	cd Volume-I-Foundations       && latexmk -C
	cd Volume-II-Applications     && latexmk -C
	cd Volume-III-Extensions      && latexmk -C
	rm -f $(MASTER)

