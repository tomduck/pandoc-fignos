
all: out/demo.pdf out/demo.tex out/demo.html out/demo.epub out/demo.docx \
     out/demo2.pdf out/demo2.tex out/demo2.html out/demo2.epub out/demo2.docx \
     out/demo3.pdf out/demo3.tex out/demo3.html out/demo3.epub out/demo3.docx

out/%.pdf: %.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	pandoc $< --filter pandoc-fignos --variable geometry:margin=1in \
              --variable urlcolor=blue -o $@

out/%.tex: %.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	pandoc $< --filter pandoc-fignos --variable urlcolor=blue -o $@

out/%.html: %.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	pandoc $< -t html --standalone --filter pandoc-fignos \
                      --variable urlcolor=blue -o $@
	cp -R img out

out/%.epub: %.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	pandoc $< -t epub3 --filter pandoc-fignos --variable urlcolor=blue -o $@

out/%.docx: %.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	pandoc $< -t docx --filter pandoc-fignos --variable urlcolor=blue -o $@

out/%.md: %.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	pandoc $< -t markdown --filter pandoc-fignos --variable urlcolor=blue -o $@

out/%.json: %.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	pandoc $< -t json --variable urlcolor=blue -o $@

restore: clean
	git checkout out/demo.epub
	git checkout out/demo.html
	git checkout out/demo.md
	git checkout out/demo.pdf
	git checkout out/demo.tex

	git checkout out/demo2.epub
	git checkout out/demo2.html
	git checkout out/demo2.md
	git checkout out/demo2.pdf
	git checkout out/demo2.tex

	git checkout out/demo3.epub
	git checkout out/demo3.html
	git checkout out/demo3.md
	git checkout out/demo3.pdf
	git checkout out/demo3.tex

	git checkout out/img/fig-1.png
	git checkout out/img/fig-2.png
	git checkout out/img/fig-3.png


.PHONY: clean

clean:
	rm -rf out
