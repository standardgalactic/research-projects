# ===========================
# Makefile for Book Project
# ===========================

MAIN = main
OUTDIR = output

.PHONY: all clean watch bib

all:
	latexmk -pdf $(MAIN).tex

clean:
	latexmk -c
	rm -rf $(OUTDIR)/*.synctex.gz

watch:
	latexmk -pvc -pdf $(MAIN).tex

bib:
	biber $(MAIN)

# For rebuilding from scratch
full:
	rm -rf $(OUTDIR)/*
	latexmk -pdf $(MAIN).tex

