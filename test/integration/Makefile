
PANDOC = pandoc
#PANDOC = pandoc-2.2.3.2
#PANDOC = pandoc-1.19
#PANDOC = pandoc-1.18
#PANDOC = pandoc-1.17.2
#PANDOC = pandoc-1.16.0.2
#PANDOC = pandoc-1.15.2

FLAGS = --standalone --top-level-division=section --number-sections --filter pandoc-fignos --filter pandoc-eqnos --filter pandoc-tablenos
#--filter ./savejson.py

all: out/demo.pdf out/demo.html out/demo.docx out/demo.json out/demo.tex

out/%: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC) $< $(FLAGS) -o $@
	if [ ! -f out/fig.png ]; then cp fig.png out; fi

.PHONY: clean

clean:
	rm -rf out
