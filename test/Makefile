
v1.17 = 1.17.0.2
v1.16 = 1.16.0.2
v1.15 = 1.15.2

PANDOC-1.17 = pandoc-$(v1.17)
PANDOC-1.16 = pandoc-$(v1.16)
PANDOC-1.15 = pandoc-$(v1.15)

PYTHON-2.7 = python2.7
PYTHON-3.4 = python3.4

FLAGS = --variable geometry:margin=1in --standalone

PDF = out/demo-1.17.pdf \
      out/demo-1.17-py2.7.pdf \
      out/demo-1.17-py3.4.pdf \
      out/demo-1.17-autolink.pdf \
      out/demo-1.16.pdf \
      out/demo-1.16-py2.7.pdf \
      out/demo-1.16-py3.4.pdf \
      out/demo-1.16-autolink.pdf \
      out/demo-1.15.pdf \
      out/demo-1.15-py2.7.pdf \
      out/demo-1.15-py3.4.pdf \
      out/demo-1.15-autolink.pdf

HTML = out/demo-1.17.html \
       out/demo-1.16.html \
       out/demo-1.15.html

IMG = out/img/plot1.png out/img/plot2.png out/img/plot3.png 

all: $(PDF) $(HTML) $(IMG)

out/demo-1.17.%: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.17) $< --filter pandoc-fignos $(FLAGS) -o $@

out/demo-1.17-py2.7.pdf: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.17) $< -t json | $(PYTHON-2.7) ../pandoc_fignos.py --pandocversion=$(v1.17) | $(PANDOC-1.17) -f json $(FLAGS) -H emptycaption.tex -o $@

out/demo-1.17-py3.4.pdf: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.17) $< -t json | $(PYTHON-3.4) ../pandoc_fignos.py --pandocversion=$(v1.17) | $(PANDOC-1.17) -f json $(FLAGS) -H emptycaption.tex -o $@

out/demo-1.17-autolink.pdf: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.17) $< --from markdown+autolink_bare_uris --filter pandoc-fignos $(FLAGS) -o $@



out/demo-1.16.%: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.16) $< --filter pandoc-fignos $(FLAGS) -o $@

out/demo-1.16-py2.7.pdf: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.16) $< -t json | $(PYTHON-2.7) ../pandoc_fignos.py --pandocversion=$(v1.16) | $(PANDOC-1.16) -f json $(FLAGS) -H emptycaption.tex -o $@

out/demo-1.16-py3.4.pdf: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.16) $< -t json | $(PYTHON-3.4) ../pandoc_fignos.py --pandocversion=$(v1.16) | $(PANDOC-1.16) -f json $(FLAGS) -H emptycaption.tex -o $@

out/demo-1.16-autolink.pdf: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.16) $< --from markdown+autolink_bare_uris --filter pandoc-fignos $(FLAGS) -o $@



out/demo-1.15.%: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.15) $< --filter pandoc-fignos $(FLAGS) -o $@

out/demo-1.15-py2.7.pdf: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.15) $< -t json | $(PYTHON-2.7) ../pandoc_fignos.py --pandocversion=$(v1.15) | $(PANDOC-1.15) -f json $(FLAGS) -H emptycaption.tex -o $@

out/demo-1.15-py3.4.pdf: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.15) $< -t json | $(PYTHON-3.4) ../pandoc_fignos.py --pandocversion=$(v1.15) | $(PANDOC-1.15) -f json $(FLAGS) -H emptycaption.tex -o $@

out/demo-1.15-autolink.pdf: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.15) $< --from markdown+autolink_bare_uris --filter pandoc-fignos $(FLAGS) -o $@


out/img/plot%.png: img/plot%.png
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	cp $< $@



.PHONY: clean

clean:
	rm -rf out
