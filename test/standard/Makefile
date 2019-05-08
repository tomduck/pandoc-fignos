
# Note: pandoc-2.4 broke citation parsing, and so is not supported.

v2.7 = 2.7
v2.6 = 2.6
v2.5 = 2.5
v2.3 = 2.3.1
v2.2 = 2.2.3.2
v2.1 = 2.1.3
v2.0 = 2.0.6
v1.19 = 1.19.2
v1.18 = 1.18
v1.17 = 1.17.2
v1.16 = 1.16.0.2
v1.15 = 1.15.2

PANDOC-2.7 = pandoc-$(v2.7)
PANDOC-2.6 = pandoc-$(v2.6)
PANDOC-2.5 = pandoc-$(v2.5)
PANDOC-2.3 = pandoc-$(v2.3)
PANDOC-2.2 = pandoc-$(v2.2)
PANDOC-2.1 = pandoc-$(v2.1)
PANDOC-2.0 = pandoc-$(v2.0)
PANDOC-1.19 = pandoc-$(v1.19)
PANDOC-1.18 = pandoc-$(v1.18)
PANDOC-1.17 = pandoc-$(v1.17)
PANDOC-1.16 = pandoc-$(v1.16)
PANDOC-1.15 = pandoc-$(v1.15)

PYTHON-2.7 = python2.7
PYTHON-3.6 = python3.6

PDFFLAGS = --variable geometry:margin=1in --standalone --variable urlcolor=blue
HTMLFLAGS = --standalone --variable urlcolor=blue

IMAGES = img/fig-1.png img/fig-2.png img/fig-3.png


all: pdf html docx img

pdf: out/test-2.7.pdf \
     out/test-2.7-py2.7.pdf \
     out/test-2.7-py3.6.pdf \
     out/test-2.7-cleveref.pdf \
     out/test-2.6.pdf \
     out/test-2.5.pdf \
     out/test-2.3.pdf \
     out/test-2.2.pdf \
     out/test-2.1.pdf \
     out/test-2.0.pdf \
     out/test-1.19.pdf \
     out/test-1.19-cleveref.pdf \
     out/test-1.18.pdf \
     out/test-1.18-cleveref.pdf \
     out/test-1.17.pdf \
     out/test-1.16.pdf \
     out/test-1.15.pdf

html: out/test-2.7.html

docx: out/test-2.7.docx


out/test-%.html: test.md $(IMAGES)
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-$*) $< --filter pandoc-fignos $(HTMLFLAGS) -o $@
	@if [ ! -d out/img ]; then mkdir -p out/img; fi
	cp img/fig-?.png out/img

out/test-%-py2.7.pdf: test.md $(IMAGES)
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-$*) $< -t json $(PDFFLAGS) | $(PYTHON-2.7) ../../pandoc_fignos.py latex --pandocversion=$(v$*) | $(PANDOC-$*) -f json $(PDFFLAGS) -o $@

out/test-%-py3.6.pdf: test.md $(IMAGES)
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-$*) $< -t json $(PDFFLAGS) | $(PYTHON-3.6) ../../pandoc_fignos.py latex --pandocversion=$(v$*) | $(PANDOC-$*) -f json $(PDFFLAGS) -o $@

out/test-%-cleveref.pdf: test.md $(IMAGES)
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-$*) $< --filter pandoc-fignos $(PDFFLAGS) --include-in-header=cleveref.tex -o $@

out/test-%.pdf: test.md $(IMAGES)
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-$*) $< --filter pandoc-fignos $(PDFFLAGS) -o $@

out/test-%.docx: test.md $(IMAGES)
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-$*) $< --filter pandoc-fignos -o $@

out/test-%.json: test.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-$*) $< --filter pandoc-fignos -o $@


.PHONY: clean

clean:
	rm -rf out
