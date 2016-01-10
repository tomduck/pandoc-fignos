
all: out/demo.pdf out/demo.tex out/demo.html out/demo.epub out/demo.md

out/demo.pdf out/demo.tex: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	pandoc $< --filter pandoc-fignos --variable geometry:margin=1in -o $@

out/demo.html: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	pandoc $< -t html --standalone --filter pandoc-fignos -o $@
	cp -R img out

out/demo.epub: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	pandoc $< -t epub3 --filter pandoc-fignos -o $@

out/demo.md: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	pandoc $< -t markdown --filter pandoc-fignos -o $@

out/demo.json: demo.md
	@if [ ! -d $(dir $@) ]; then mkdir -p $(dir $@); fi
	pandoc $< -t json -o $@

restore: clean
	git checkout out/demo.epub
	git checkout out/demo.html
	git checkout out/demo.md
	git checkout out/demo.pdf
	git checkout out/demo.tex
	git checkout out/img/plot1.png
	git checkout out/img/plot2.png
	git checkout out/img/plot3.png


.PHONY: clean

clean:
	rm -rf out
