# Use LuaLaTeX instead of PDFLaTeX
$pdflatex = 'lualatex -interaction=nonstopmode -shell-escape';

# Use Biber for biblatex
$biber = 'biber';

# Always run biber after latex if needed
$pdf_mode = 1;

# Clean up extra files when running latexmk -c
$clean_ext .= ' %R.run.xml %R.bcf';

# Make latexmk detect biber runs
$bibtex_use = 2;

