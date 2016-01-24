
PANDOC-1.16 = pandoc-1.16.0.2
PANDOC-1.15 = pandoc-1.15.2
PYTHON-2.7 = python2.7
PYTHON-3.4 = python3.4

FLAGS = --variable geometry:margin=1in

all: out/demo-1.16.pdf \
     out/demo-1.16-py2.7.pdf \
     out/demo-1.16-py3.4.pdf \
     out/demo-1.16-autolink.pdf \
     out/demo-1.15.pdf \
     out/demo-1.15-py2.7.pdf \
     out/demo-1.15-py3.4.pdf \
     out/demo-1.15-autolink.pdf

out/demo-1.16.pdf: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.16) $< --filter pandoc-fignos $(FLAGS) -o $@

out/demo-1.16-py2.7.pdf: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.16) $< -t json | $(PYTHON-2.7) ../pandoc_fignos.py | $(PANDOC-1.16) -f json $(FLAGS) -H emptycaption.tex -o $@

out/demo-1.16-py3.4.pdf: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.16) $< -t json | $(PYTHON-3.4) ../pandoc_fignos.py | $(PANDOC-1.16) -f json $(FLAGS) -H emptycaption.tex -o $@

out/demo-1.16-autolink.pdf: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.16) $< --from markdown+autolink_bare_uris --filter pandoc-fignos $(FLAGS) -o $@

out/demo-1.15.pdf: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.15) $< --filter pandoc-fignos $(FLAGS) -o $@

out/demo-1.15-autolink.pdf: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.15) $< --from markdown+autolink_bare_uris --filter pandoc-fignos $(FLAGS) -o $@

out/demo-1.15-py2.7.pdf: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.15) $< -t json | $(PYTHON-2.7) ../pandoc_fignos.py | $(PANDOC-1.15) -f json $(FLAGS) -H emptycaption.tex -o $@

out/demo-1.15-py3.4.pdf: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC-1.15) $< -t json | $(PYTHON-3.4) ../pandoc_fignos.py | $(PANDOC-1.15) -f json $(FLAGS) -H emptycaption.tex -o $@

.PHONY: clean

clean:
	rm -rf out
