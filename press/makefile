# PRESS
# publish simple markdown documentation to different formats

# prelim: eval "$(luarocks path --bin)"

SHELL:=/bin/bash

# commands
.PHONY: install grip check

# targets
SOURCES:=$(shell find raw -name '*.md' -print)
TARGETS_md:=$(patsubst raw/%.md, pub/%.md, ${SOURCES})
TARGETS_html:=$(patsubst raw/%.md, pub/%.html, ${SOURCES})
TARGETS_pdf:=$(patsubst raw/%.md, pub/%.pdf, ${SOURCES})

# publish in all formats
all: ${TARGETS_html} ${TARGETS_md} ${TARGETS_pdf}

# settings
SOURCE_FORMAT="markdown+pipe_tables+backtick_code_blocks+auto_identifiers+strikeout+yaml_metadata_block+implicit_figures+all_symbols_escapable+link_attributes+smart+fenced_divs"

# use grip to demo github-flavored markdown
install: venv venv/bin/grip
venv:
	python3 -m venv venv
venv/bin/grip:
	source venv/bin/activate && pip install grip
grip:
	venv/bin/grip

# dev: for logging or debugging of lua pandoc filters, see 
#   https://pandoc.org/lua-filters.html#debugging-lua-filters

# note we have to send shell echo commands to stdout or makefile gets confused
# note that we use a sed kludge below to strip custom comments

pub/%.html: raw/%.md
	$(shell if [ $$(pandoc \
		--template=render/metadata.pandoc-tpl \
		$< | jq "if .press.html then 1 else 0 end") -ne 0 ]; then \
			echo "status: converting $< to $@" >&2; \
			sed '/^[[:blank:]]*-- .*$$/d;s/-- .*$$//' $< | cat -s | \
			pandoc --standalone \
				--lua-filter render/custom-imager.lua \
				-c ../render/github-markdown.css \
				-f gfm -t html \
				--output=$@ ; \
				fi)

pub/%.md: raw/%.md
	$(shell if [ $$(pandoc \
		--template=render/metadata.pandoc-tpl \
		$< | jq "if .press.markdown then 1 else 0 end") -ne 0 ]; then \
			echo 'status: converting $< to $@' >&2; \
			sed '/^[[:blank:]]*-- .*$$/d;s/-- .*$$//' $< | cat -s | \
			pandoc --standalone \
				--lua-filter render/custom-imager.lua \
				-f markdown -t markdown \
				--output=$@ ; \
				fi)

# note when monitoring this file, use url option #pagemode=none

pub/%.pdf: raw/%.md
	$(shell if [ $$(pandoc \
		--template=render/metadata.pandoc-tpl \
		$< | jq "if .press.beamer then 1 else 0 end") -ne 0 ]; then \
			echo "status: converting $< to $@" >&2; \
			sed '/^[[:blank:]]*-- .*$$/d;s/-- .*$$//' $< | cat -s | \
			pandoc --standalone \
				--to=beamer \
				--pdf-engine=xelatex \
				--lua-filter render/custom-imager.lua \
				--highlight-style tango \
				-f ${SOURCE_FORMAT} \
				--include-in-header render/style.tex \
				--output=$@ ; \
				fi)