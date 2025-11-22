#!/bin/sh

# ============================================================
#  init_monograph.sh
#  Creates directory structure + stubs + main.tex + references
# ============================================================

set -e

echo "=== Initializing RSVP–Polyxan Monograph Structure ==="

# --------------------------
# Directories
# --------------------------
mkdir -p chapters
mkdir -p parts
mkdir -p appendices
mkdir -p macros

echo "Directories ensured."

# --------------------------
# Create Part intro files
# --------------------------
for p in 1 2 3 4 5 6; do
    file="parts/part${p}.tex"
    if [ ! -f "$file" ]; then
        cat > "$file" <<EOF
% Part ${p} introduction

\\part{Part ${p} Title Placeholder}

\\label{part:${p}}

% Replace this text with the real Part introduction.
EOF
        echo "Created: $file"
    else
        echo "Exists:  $file"
    fi
done

# --------------------------
# Create Chapter stubs
# --------------------------
for n in $(seq -w 1 100); do
    file="chapters/chapter_${n}.tex"
    if [ ! -f "$file" ]; then
        cat > "$file" <<EOF
\\chapter{Chapter ${n} Placeholder Title}
\\label{ch:${n}}

% Replace this with the real content for Chapter ${n}.
EOF
        echo "Created: $file"
    else
        echo "Exists:  $file"
    fi
done

# --------------------------
# Appendices A–Z
# --------------------------
for letter in A B C D E F G H I J K L M N O P Q R S T U V W X Y Z; do
    file="appendices/appendix_${letter}.tex"
    if [ ! -f "$file" ]; then
        cat > "$file" <<EOF
\\chapter*{Appendix ${letter}}
\\addcontentsline{toc}{chapter}{Appendix ${letter}}

% Replace this with Appendix ${letter} content.
EOF
        echo "Created: $file"
    else
        echo "Exists:  $file"
    fi
done

# --------------------------
# Create references.bib
# --------------------------
if [ ! -f references.bib ]; then
    cat > references.bib <<EOF
% references.bib
% Add your BibTeX entries here.
% Compatible with biber.

@article{placeholder,
  author = {Author, A.},
  title = {Placeholder Title},
  journal = {Placeholder Journal},
  year = {2025}
}
EOF
    echo "Created: references.bib"
else
    echo "Exists:  references.bib"
fi

# --------------------------
# Create macros file
# --------------------------
if [ ! -f macros/macros.tex ]; then
    cat > macros/macros.tex <<EOF
% Global macros for the monograph.

% Example:
% \\newcommand{\\RSVP}{\\textsc{RSVP}}
EOF
    echo "Created: macros/macros.tex"
else
    echo "Exists:  macros/macros.tex"
fi

# --------------------------
# Create main.tex
# --------------------------
if [ ! -f main.tex ]; then
    cat > main.tex <<EOF
% ============================================================
%  main.tex — RSVP–Polyxan Monograph
%  LuaLaTeX + biber compatible
% ============================================================

\\documentclass[12pt,oneside]{book}

% ------------------------------------------------------------
% Packages
% ------------------------------------------------------------
\\usepackage{fontspec}        % LuaLaTeX font support
\\usepackage{microtype}
\\usepackage{setspace}
\\usepackage{amsmath,amssymb,amsthm}
\\usepackage{bm}
\\usepackage{physics}
\\usepackage{csquotes}
\\usepackage{hyperref}
\\usepackage{enumitem}
\\usepackage{titlesec}
\\usepackage{tocloft}

% ------------------------------------------------------------
% Bibliography
% ------------------------------------------------------------
\\usepackage[
  backend=biber,
  style=authoryear,
  maxbibnames=99
]{biblatex}
\\addbibresource{references.bib}

% ------------------------------------------------------------
% Macros
% ------------------------------------------------------------
\\input{macros/macros.tex}

% ------------------------------------------------------------
% Document
% ------------------------------------------------------------
\\begin{document}

\\frontmatter

\\title{\\bfseries The RSVP--Polyxan Universe:\\\\A Unified Theory of Meaning, Curvature, and Verification}
\\author{Flyxion}
\\date{2025}
\\maketitle

\\tableofcontents

\\mainmatter

% ------------------------------------------------------------
% Parts and Chapters
% ------------------------------------------------------------

% PART 1
\\input{parts/part1.tex}
EOF

    # Append all chapters and parts to main.tex
    for p in 1 2 3 4 5 6; do
        echo "% Part $p Chapters" >> main.tex
        for c in $(seq -w $(( (p-1)*20+1 )) $(( p*20 )) ); do
            echo "\\input{chapters/chapter_${c}.tex}" >> main.tex
        done
        if [ $p -lt 6 ]; then
            echo "\\input{parts/part$((p+1)).tex}" >> main.tex
        fi
    done

    # Finalize main.tex
    cat >> main.tex <<EOF

% ------------------------------------------------------------
% Appendices
% ------------------------------------------------------------

\\appendix

EOF

    for letter in A B C D E F G H I J K L M N O P Q R S T U V W X Y Z; do
        echo "\\input{appendices/appendix_${letter}.tex}" >> main.tex
    done

    cat >> main.tex <<EOF

% ------------------------------------------------------------
% Bibliography
% ------------------------------------------------------------
\\printbibliography

\\end{document}
EOF

    echo "Created: main.tex"
else
    echo "Exists:  main.tex"
fi

echo "=== Initialization complete ==="
