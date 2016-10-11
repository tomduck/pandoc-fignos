
v1.17 = 1.17.2
v1.16 = 1.16.0.2
v1.15 = 1.15.2

PANDOC-1.17 = pandoc-$(v1.17)
PANDOC-1.16 = pandoc-$(v1.16)
PANDOC-1.15 = pandoc-$(v1.15)

PYTHON-2.7 = python2.7
PYTHON-3.4 = python3.4

PDFFLAGS = --variable geometry:margin=1in --standalone --variable urlcolor=blue
HTMLFLAGS = --standalone --variable urlcolor=blue

all: pdf html img tex md

pdf: out/test-1.17.pdf \
     out/test-1.17-py2.7.pdf \
     out/test-1.17-py3.4.pdf \
     out/test-1.17-autolink.pdf \
     out/test-1.17-cleveref.pdf \
     out/test-1.17-autolink-cleveref.pdf \
     out/test-1.16.pdf \
     out/test-1.16-py2.7.pdf \
     out/test-1.16-py3.4.pdf \
     out/test-1.16-autolink.pdf \
     out/test-1.16-cleveref.pdf \
     out/test-1.16-autolink-cleveref.pdf \
     out/test-1.15.pdf \
     out/test-1.15-py2.7.pdf \
     out/test-1.15-py3.4.pdf \
     out/test-1.15-autolink.pdf \
     out/test-1.15-cleveref.pdf \
     out/test-1.15-autolink-cleveref.pdf


html: out/test-1.17.html \
      out/test-1.16.html \
      out/test-1.15.html \
      img

img: out/img/plot1.png out/img/plot2.png out/img/plot3.png 

tex: out/test-1.17.tex \
     out/test-1.16.tex \
     out/test-1.15.tex

md: out/test-1.17.md

out/test-1.17.html: test.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.17) $< --filter pandoc-fignos $(HTMLFLAGS) -o $@

out/test-1.17.pdf: test.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.17) $< --filter pandoc-fignos $(PDFFLAGS) -o $@

out/test-1.17.tex: test.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.17) $< --filter pandoc-fignos -o $@

out/test-1.17.md: test.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.17) $< --filter pandoc-fignos -o $@

out/test-1.17-py2.7.pdf: test.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.17) $< -t json | $(PYTHON-2.7) ../pandoc_fignos.py latex --pandocversion=$(v1.17) | $(PANDOC-1.17) -f json $(PDFFLAGS) -o $@

out/test-1.17-py3.4.pdf: test.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.17) $< -t json | $(PYTHON-3.4) ../pandoc_fignos.py latex --pandocversion=$(v1.17) | $(PANDOC-1.17) -f json $(PDFFLAGS) -o $@

out/test-1.17-autolink.pdf: test.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.17) $< --from markdown+autolink_bare_uris --filter pandoc-fignos $(PDFFLAGS) -o $@

out/test-1.17-cleveref.pdf: test.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.17) $< --filter pandoc-fignos $(PDFFLAGS) --include-in-header=cleveref.tex -o $@

out/test-1.17-autolink-cleveref.pdf: test.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.17) $< --from markdown+autolink_bare_uris --filter pandoc-fignos $(PDFFLAGS) --include-in-header=cleveref.tex -o $@


out/test-1.16.html: test.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.16) $< --filter pandoc-fignos $(HTMLFLAGS) -o $@

out/test-1.16.pdf: test.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.16) $< --filter pandoc-fignos $(PDFFLAGS) -o $@

out/test-1.16.tex: test.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.16) $< --filter pandoc-fignos -o $@

out/test-1.16-py2.7.pdf: test.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.16) $< -t json | $(PYTHON-2.7) ../pandoc_fignos.py latex --pandocversion=$(v1.16) | $(PANDOC-1.16) -f json $(PDFFLAGS) -o $@

out/test-1.16-py3.4.pdf: test.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.16) $< -t json | $(PYTHON-3.4) ../pandoc_fignos.py latex --pandocversion=$(v1.16) | $(PANDOC-1.16) -f json $(PDFFLAGS) -o $@

out/test-1.16-autolink.pdf: test.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.16) $< --from markdown+autolink_bare_uris --filter pandoc-fignos $(PDFFLAGS) -o $@

out/test-1.16-cleveref.pdf: test.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.16) $< --filter pandoc-fignos $(PDFFLAGS) --include-in-header=cleveref.tex -o $@

out/test-1.16-autolink-cleveref.pdf: test.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.16) $< --from markdown+autolink_bare_uris --filter pandoc-fignos $(PDFFLAGS) --include-in-header=cleveref.tex -o $@


out/test-1.15.html: test.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.15) $< --filter pandoc-fignos $(HTMLFLAGS) -o $@

out/test-1.15.pdf: test.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.15) $< --filter pandoc-fignos $(PDFFLAGS) -o $@

out/test-1.15.tex: test.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.15) $< --filter pandoc-fignos -o $@

out/test-1.15-py2.7.pdf: test.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.15) $< -t json | $(PYTHON-2.7) ../pandoc_fignos.py latex --pandocversion=$(v1.15) | $(PANDOC-1.15) -f json $(PDFFLAGS) -o $@

out/test-1.15-py3.4.pdf: test.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.15) $< -t json | $(PYTHON-3.4) ../pandoc_fignos.py latex --pandocversion=$(v1.15) | $(PANDOC-1.15) -f json $(PDFFLAGS) -o $@

out/test-1.15-autolink.pdf: test.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.15) $< --from markdown+autolink_bare_uris --filter pandoc-fignos $(PDFFLAGS) -o $@

out/test-1.15-cleveref.pdf: test.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.15) $< --filter pandoc-fignos $(PDFFLAGS) --include-in-header=cleveref.tex -o $@

out/test-1.15-autolink-cleveref.pdf: test.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.15) $< --from markdown+autolink_bare_uris --filter pandoc-fignos $(PDFFLAGS) --include-in-header=cleveref.tex -o $@


out/img/plot%.png: img/plot%.png
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	cp $< $@



.PHONY: clean

clean:
	rm -rf out
