
extensions = .pdf .html .epub .tex .docx

dest = $(addprefix out/demo,$(extensions)) \
       $(addprefix out/demo2,$(extensions)) \
       $(addprefix out/demo3,$(extensions)) \
       out/demo4.pdf

all: $(dest)

$(filter out/demo.%,$(dest)): demo.md
$(filter out/demo2.%,$(dest)): demo2.md
$(filter out/demo3.%,$(dest)): demo3.md
$(filter out/demo4.%,$(dest)): demo4.md

out/%.pdf: %.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	pandoc $< --filter pandoc-fignos --variable urlcolor=blue -o $@

out/%.html: %.md headers/header.html
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	pandoc $< --standalone --filter pandoc-fignos --include-in-header=headers/header.html -o $@
	cp -R img out

out/%.epub: %.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	pandoc $< -t epub3 --filter pandoc-fignos -o $@

out/%:
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	pandoc $^ --filter pandoc-fignos -o $@


restore: clean
	for num in "" 2 3 ; do \
      for ext in $(extensions) ; do \
        git checkout out/demo$$num$$ext ; \
      done ; \
    done

	git checkout out/img/fig-1.png
	git checkout out/img/fig-2.png
	git checkout out/img/fig-3.png


.PHONY: clean

clean:
	rm -rf out
