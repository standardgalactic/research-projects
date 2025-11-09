.PHONY: build test paper zip

build:
\tpython -m pip install -e src

test:
\tpytest -q

paper:
\t# build LaTeX (requires pdflatex, biber)
\tcd paper && pdflatex main.tex || true

zip:
\tpython -c "import shutil; shutil.make_archive('plenumhub_stage3','zip','.')"
