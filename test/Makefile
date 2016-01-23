

PANDOCVERSION = $(shell pandoc -v | head -n 1)

all: out/demo-1.16.pdf \
     out/demo-1.16-autolink.pdf \
     out/demo-1.15.pdf \
     out/demo-1.15-autolink.pdf

out/demo-1.16.pdf: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	pandoc-1.16.0.2 $< --filter pandoc-eqnos -o $@

out/demo-1.16-autolink.pdf: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	pandoc-1.16.0.2 $< --from markdown+autolink_bare_uris --filter pandoc-eqnos -o $@

out/demo-1.15.pdf: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	pandoc-1.15.2 $< --from markdown+autolink_bare_uris --filter pandoc-eqnos -o $@

out/demo-1.15-autolink.pdf: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	pandoc-1.15.2 $< --from markdown+autolink_bare_uris --filter pandoc-eqnos -o $@


.PHONY: clean

clean:
	rm -rf out
