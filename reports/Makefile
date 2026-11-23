# Makefile for CO5177 LaTeX Reports
# Usage:
#   make init NAME=tabular      # Scaffold reports/tabular/ from starter/
#   make build TARGET=tabular   # Compile reports/tabular/report.tex -> report.pdf
#   make check TARGET=tabular   # Build and check for undefined references / warnings
#   make clean TARGET=tabular   # Remove LaTeX auxiliary files in reports/tabular/
#   make template               # Compile the upstream reference in reports/template/

TARGET ?= template
NAME ?=
LATEXMK = latexmk -pdf -shell-escape -interaction=nonstopmode -halt-on-error

.PHONY: help init build watch check clean distclean template

help:
	@echo "Targets:"
	@echo "  make init NAME=<name>       Create reports/<name>/ from reports/starter/"
	@echo "  make build TARGET=<name>    Compile reports/<name>/report.tex"
	@echo "  make watch TARGET=<name>    Auto-recompile reports/<name>/report.tex on changes"
	@echo "  make check TARGET=<name>    Compile, show PDF summary, and check log for errors/refs"
	@echo "  make clean TARGET=<name>    Clean LaTeX aux & _minted files in reports/<name>/"
	@echo "  make distclean TARGET=<name> Clean aux files and remove report.pdf"
	@echo "  make template               Compile reports/template/report.tex"

init:
	@test -n "$(NAME)" || (echo "Error: specify NAME=<report_name>, e.g. make init NAME=tabular" && exit 1)
	@test ! -d "$(NAME)" || (echo "Error: reports/$(NAME) already exists" && exit 1)
	cp -r starter "$(NAME)"
	@echo "Created reports/$(NAME)/ from starter/. Edit reports/$(NAME)/report.tex and chapters/*.tex."

build:
	@test -f "$(TARGET)/report.tex" || (echo "Error: $(TARGET)/report.tex not found" && exit 1)
	cd "$(TARGET)" && $(LATEXMK) report.tex

watch:
	@test -f "$(TARGET)/report.tex" || (echo "Error: $(TARGET)/report.tex not found" && exit 1)
	cd "$(TARGET)" && latexmk -pdf -pvc -shell-escape -interaction=nonstopmode report.tex

check: build
	@if command -v pdfinfo >/dev/null 2>&1; then \
		echo "=== PDF Summary ==="; \
		pdfinfo "$(TARGET)/report.pdf" | grep -E "Pages|Page size"; \
	fi
	@echo "=== Reference & Citation Errors ==="
	@if grep -qE "LaTeX Warning: (Reference|Citation).*undefined|There were undefined references|Citation .* undefined" "$(TARGET)/report.log"; then \
		grep -nE "LaTeX Warning: (Reference|Citation).*undefined|There were undefined references|Citation .* undefined" "$(TARGET)/report.log"; \
		exit 1; \
	else \
		echo "None"; \
	fi
	@echo "=== Layout Overflow Warnings (Overfull hbox/vbox) ==="
	@grep -nE "Overfull \\\\(hbox|vbox)" "$(TARGET)/report.log" || echo "None"
	@echo "OK: $(TARGET)/report.pdf built cleanly with no undefined references."

clean:
	@test -d "$(TARGET)" || (echo "Error: $(TARGET) not found" && exit 1)
	cd "$(TARGET)" && latexmk -c && rm -rf _minted-*

distclean: clean
	rm -f "$(TARGET)/report.pdf"

template:
	$(MAKE) build TARGET=template
