# Makefile (top-level)
# Repo goal: reproducible LaTeX builds in Docker + optional “scaffold” docs output

SHELL := /bin/bash
IMAGE := flyxion/latex-essays:latest
OUT   := out
ESSAYS_DIR := essays
SCAFFOLD_DIR := scaffold

.DEFAULT_GOAL := help

help:
	@echo "Targets:"
	@echo "  make docker-build        Build the Docker image"
	@echo "  make compile             Compile all LaTeX essays to PDF"
	@echo "  make compile-one NAME=x  Compile a single essay (basename, no .tex)"
	@echo "  make scaffold            Generate folders + README_RSVP.md"
	@echo "  make clean               Remove build artifacts"

docker-build:
	docker build -t $(IMAGE) .

compile: docker-build
	mkdir -p $(OUT)
	docker run --rm -u $$(id -u):$$(id -g) -v "$$PWD":/work -w /work $(IMAGE) \
		bash -lc 'scripts/compile_all.sh "$(ESSAYS_DIR)" "$(OUT)"'

compile-one: docker-build
	@if [[ -z "$(NAME)" ]]; then echo "Usage: make compile-one NAME=essay_basename"; exit 2; fi
	mkdir -p $(OUT)
	docker run --rm -u $$(id -u):$$(id -g) -v "$$PWD":/work -w /work $(IMAGE) \
		bash -lc 'scripts/compile_one.sh "$(ESSAYS_DIR)/$(NAME).tex" "$(OUT)"'

scaffold:
	bash scripts/scaffold.sh "$(SCAFFOLD_DIR)"

clean:
	rm -rf $(OUT) $(SCAFFOLD_DIR)
	find $(ESSAYS_DIR) -maxdepth 2 -type f \( -name "*.aux" -o -name "*.log" -o -name "*.bbl" -o -name "*.blg" -o -name "*.bcf" -o -name "*.run.xml" -o -name "*.toc" -o -name "*.out" \) -delete

