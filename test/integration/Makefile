
PANDOC = pandoc

FLAGS = --standalone --top-level-division=section --number-sections --filter pandoc-xnos

all: out/demo.pdf out/demo.html out/demo.docx out/demo.json out/demo.tex

out/%: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	$(PANDOC) $< $(FLAGS) -o $@
	if [ ! -f out/fig.png ]; then cp fig.png out; fi

.PHONY: clean

clean:
	rm -rf out
