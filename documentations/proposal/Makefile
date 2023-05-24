name=proposal

all: $(name).pdf

force:
	rm -f $(name).pdf
	make all

$(name).pdf: *.tex *.cls
	pdflatex $(name)
	bibtex $(name)
	pdflatex $(name)
	pdflatex $(name)

clean:
	rm -f *.aux *.toc *.log *.bbl *.blg *.out $(name).pdf
