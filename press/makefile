# PRESS
# publish simple markdown documentation to different formats

# prelim: eval "$(luarocks path --bin)"

SHELL:=/bin/bash
HAS_LROCKS := $(shell echo "$${LUA_PATH}" 2> /dev/null)

# commands
.PHONY:

# targets
SOURCES:=$(shell find raw/ -name '*.md' -print)
TARGETS_md:=$(patsubst raw/%.md, pub/%.md, ${SOURCES})
TARGETS_html:=$(patsubst raw/%.md, pub/%.html, ${SOURCES})
TARGETS_pdf:=$(patsubst raw/%.md, pub/%.pdf, ${SOURCES})
TARGETS_docx:=$(patsubst raw/%.md, pub/%.docx, ${SOURCES})

# publish in all formats
all: \
	pub pub/pics pub/render \
	${TARGETS_html} ${TARGETS_md} ${TARGETS_pdf} ${TARGETS_docx}
ifndef HAS_LROCKS
	@echo "error: cannot find lua path"
	@echo 'usage: eval "$$(luarocks path --bin)"'
endif

# settings
SOURCE_FORMAT="markdown+pipe_tables+backtick_code_blocks+auto_identifiers+strikeout+yaml_metadata_block+implicit_figures+all_symbols_escapable+link_attributes+smart+fenced_divs"

# prepare links
pub:
	mkdir -p ./pub
pub/render:
	cd pub && ln -s ../render
pub/pics:
	if [ -d raw/pics ]; then cd pub && ln -s ../raw/pics; fi

clean:
	rm -rf pub/

# dev: for logging or debugging of lua pandoc filters, see 
#   https://pandoc.org/lua-filters.html#debugging-lua-filters

# note we have to send shell echo commands to stdout or makefile gets confused
# note that we use a sed kludge below to strip custom comments

pub/%.html: raw/%.md
	$(shell if [ $$(pandoc \
		--template=render/metadata.pandoc-tpl --metadata title=" " $< | \
		jq "if .press.html then 1 else 0 end") -ne 0 ]; then \
			echo "status: converting $< to $@" >&2; \
			sed '/^[[:blank:]]*-- .*$$/d;s/-- .*$$//' $< | cat -s | \
			pandoc --standalone \
				--lua-filter render/custom-imager.lua \
				-c render/github-markdown.css \
				-f gfm -t html \
				--output=$@; \
			if [ ! "$$(pandoc \
				--template=render/metadata.pandoc-tpl $< | \
				jq '.copy_html')" = "null" ]; then \
				CMD_COPY="cp -av $@ $$(pandoc \
					--template=render/metadata.pandoc-tpl $< | \
					jq ".copy_html" | \
					sed -e "s/[[:space:]]/\\\ /g" | sed -e 's/\"//g')" ; \
				eval $${CMD_COPY} >&2 ; \
				fi; fi)

pub/%.md: raw/%.md
	$(shell if [ $$(pandoc \
		--template=render/metadata.pandoc-tpl --metadata title=" " $< | \
		jq "if .press.markdown then 1 else 0 end") -ne 0 ]; then \
			echo 'status: converting $< to $@' >&2; \
			sed '/^[[:blank:]]*-- .*$$/d;s/-- .*$$//' $< | cat -s | \
			pandoc --standalone \
				--lua-filter render/custom-imager.lua \
				-f markdown -t markdown \
				--output=$@; \
			if [ ! "$$(pandoc \
				--template=render/metadata.pandoc-tpl $< | \
				jq '.copy_md')" = "null" ]; then \
				CMD_COPY="cp -av $@ $$(pandoc \
					--template=render/metadata.pandoc-tpl $< | \
					jq ".copy_md" | \
					sed -e "s/[[:space:]]/\\\ /g" | sed -e 's/\"//g')" ; \
				eval $${CMD_COPY} >&2 ; \
				fi; fi)

# note when monitoring this file, use url option #pagemode=none

pub/%.pdf: raw/%.md
	$(shell if [ $$(pandoc \
		--template=render/metadata.pandoc-tpl --metadata title=" " $< | \
		jq "if .press.beamer then 1 else 0 end") -ne 0 ]; then \
			echo "status: converting $< to $@" >&2; \
			sed '/^[[:blank:]]*-- .*$$/d;s/-- .*$$//' $< | cat -s | \
			pandoc --standalone \
				--to=beamer \
				--pdf-engine=xelatex \
				--lua-filter render/custom-imager.lua \
				--highlight-style tango \
				-f ${SOURCE_FORMAT} \
				--include-in-header render/style.tex \
				--output=$@; \
			if [ ! "$$(pandoc \
				--template=render/metadata.pandoc-tpl $< | \
				jq '.copy_pdf')" = "null" ]; then \
				CMD_COPY="cp -av $@ $$(pandoc \
					--template=render/metadata.pandoc-tpl $< | \
					jq ".copy_pdf" | \
					sed -e "s/[[:space:]]/\\\ /g" | sed -e 's/\"//g')" ; \
				eval $${CMD_COPY} >&2 ; \
				fi; fi)

# note using eval below to deal with nightmarish spaces escape problem

pub/%.docx: raw/%.md
	$(shell if [ $$(pandoc \
		--template=render/metadata.pandoc-tpl --metadata title=" " $< | \
		jq "if .press.docx then 1 else 0 end") -ne 0 ]; then \
			echo "status: converting $< to $@" >&2; \
			sed '/^[[:blank:]]*-- .*$$/d;s/-- .*$$//' $< | cat -s | \
			pandoc --standalone \
				--lua-filter render/custom-imager.lua \
				-f markdown -t docx \
				--output=$@; \
			if [ ! "$$(pandoc \
				--template=render/metadata.pandoc-tpl $< | \
				jq '.copy_docx')" = "null" ]; then \
				CMD_COPY="cp -av $@ $$(pandoc \
					--template=render/metadata.pandoc-tpl $< | \
					jq ".copy_docx" | \
					sed -e "s/[[:space:]]/\\\ /g" | sed -e 's/\"//g')" ; \
				eval $${CMD_COPY} >&2 ; \
				fi; fi)