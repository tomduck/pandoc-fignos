
PANDOC-1.16 = pandoc-1.16.0.2
PANDOC-1.15 = pandoc-1.15.2

all: out/demo-1.16.pdf \
     out/demo-1.16-autolink.pdf \
     out/demo-1.15.pdf

out/demo-1.16.pdf: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.16) $< --filter pandoc-fignos -o $@

out/demo-1.16-autolink.pdf: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.16) $< --from markdown+autolink_bare_uris --filter pandoc-fignos -o $@

out/demo-1.15.pdf: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.15) $< --filter pandoc-fignos -o $@

out/demo-1.15-autolink.pdf: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.15) $< --from markdown+autolink_bare_uris --filter pandoc-fignos -o $@


.PHONY: clean

clean:
	rm -rf out
