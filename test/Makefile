
v1.18 = 1.18
v1.17 = 1.17.2
v1.16 = 1.16.0.2
v1.15 = 1.15.2

PANDOC-1.18 = pandoc-$(v1.18)
PANDOC-1.17 = pandoc-$(v1.17)
PANDOC-1.16 = pandoc-$(v1.16)
PANDOC-1.15 = pandoc-$(v1.15)

PYTHON-2.7 = python2.7
PYTHON-3.4 = python3.4

PDFFLAGS = --variable geometry:margin=1in --standalone --variable urlcolor=blue
HTMLFLAGS = --standalone --variable urlcolor=blue
DOCXFLAGS =

all: pdf html docx img


pdf: out/test-1.18.pdf \
     out/test-1.18-py2.7.pdf \
     out/test-1.18-py3.4.pdf \
     out/test-1.18-cleveref.pdf \
     out/test-1.17.pdf \
     out/test-1.17-py2.7.pdf \
     out/test-1.17-py3.4.pdf \
     out/test-1.17-cleveref.pdf \
     out/test-1.16.pdf \
     out/test-1.16-py2.7.pdf \
     out/test-1.16-py3.4.pdf \
     out/test-1.16-cleveref.pdf \
     out/test-1.15.pdf \
     out/test-1.15-py2.7.pdf \
     out/test-1.15-py3.4.pdf \
     out/test-1.15-cleveref.pdf \
     img


html: out/test-1.18.html \
      out/test-1.17.html \
      out/test-1.16.html \
      out/test-1.15.html \
      img


docx: out/test-1.18.docx img


img: out/img/fig-1.png out/img/fig-2.png out/img/fig-3.png


out/test-%.html: test.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-$*) $< --filter pandoc-fignos $(HTMLFLAGS) -o $@

out/test-%-py2.7.pdf: test.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-$*) $< -t json $(PDFFLAGS) | $(PYTHON-2.7) ../pandoc_fignos.py latex --pandocversion=$(v$*) | $(PANDOC-$*) -f json $(PDFFLAGS) -o $@

out/test-%-py3.4.pdf: test.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-$*) $< -t json $(PDFFLAGS) | $(PYTHON-3.4) ../pandoc_fignos.py latex --pandocversion=$(v$*) | $(PANDOC-$*) -f json $(PDFFLAGS) -o $@

out/test-%-cleveref.pdf: test.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-$*) $< --filter pandoc-fignos $(PDFFLAGS) --include-in-header=cleveref.tex -o $@

out/test-%.pdf: test.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-$*) $< --filter pandoc-fignos $(PDFFLAGS) -o $@

out/test-%.docx: test.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-$*) $< --filter pandoc-fignos $(DOCXFLAGS) -o $@


out/img/fig-%.png: img/fig-%.png
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	cp $< $@


.PHONY: clean

clean:
	rm -rf out
