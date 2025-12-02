# Makefile for RSVP monograph

TEX=monograph.tex
PDF=monograph.pdf

all: $(PDF)

$(PDF): $(TEX) references.bib
	latexmk -pdf -interaction=nonstopmode monograph.tex

clean:
	latexmk -C
	rm -f monograph.run.xml monograph.bbl monograph.bcf monograph-blx.bib

reset:
	latexmk -C
	rm -f *.aux *.log *.out *.toc *.bbl *.bcf *.run.xml *.blg *.fdb_latexmk *.fls

