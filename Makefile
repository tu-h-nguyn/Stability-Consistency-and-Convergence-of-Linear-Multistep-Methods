# Stability, Consistency and Convergence of Linear Multistep Methods
#
#   make report     build the PDF report
#   make slides     build the presentation
#   make figures    regenerate every figure from the Python code
#   make test       run the test suite
#   make matlab     run the MATLAB scripts through Octave and check them
#   make lint       run ruff over the Python sources
#   make all        everything above

PYTHON  ?= python3
LATEXMK ?= latexmk -pdf -interaction=nonstopmode -halt-on-error

.PHONY: all report slides figures test matlab lint clean help

all: figures test report slides

report: main.tex $(wildcard Sections/*.tex)
	$(LATEXMK) main.tex

slides:
	cd slides && $(LATEXMK) main.tex

figures:
	$(PYTHON) code/experiments/run_all.py

test:
	cd code && $(PYTHON) -m pytest tests -q

matlab:
	./matlab/verify.sh

lint:
	cd code && $(PYTHON) -m ruff check .

clean:
	latexmk -C main.tex || true
	cd slides && latexmk -C main.tex || true
	rm -rf code/**/__pycache__ code/.pytest_cache

help:
	@grep -E '^#   make' Makefile
