SHELL := /bin/bash

TEX_FILES := $(shell find year-* -path '*/notes/*.tex' -not -path '*/.git/*' -not -path '*/node_modules/*')
PDF_FILES := $(TEX_FILES:.tex=.pdf)

LATEXMK := latexmk
LATEXMK_FLAGS := -pdf -interaction=nonstopmode -halt-on-error -file-line-error

.PHONY: all notes clean list help $(TEX_FILES)

all: notes

notes: $(PDF_FILES)

%.pdf: %.tex
	@echo ">> Building $<"
	@cd $(dir $<) && $(LATEXMK) $(LATEXMK_FLAGS) $(notdir $<)

clean:
	@for f in $(TEX_FILES); do \
		(cd $$(dirname $$f) && $(LATEXMK) -c $$(basename $$f)) || true; \
	done

distclean:
	@for f in $(TEX_FILES); do \
		(cd $$(dirname $$f) && $(LATEXMK) -C $$(basename $$f)) || true; \
	done

list:
	@for f in $(TEX_FILES); do echo $$f; done

help:
	@echo "Targets:"
	@echo "  make / make notes  Build all notes PDFs"
	@echo "  make <path>.pdf    Build a single PDF"
	@echo "  make clean         Remove LaTeX aux files"
	@echo "  make distclean     Remove aux files and PDFs"
	@echo "  make list          List discovered .tex files"
