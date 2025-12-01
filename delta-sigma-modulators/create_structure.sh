#!/bin/bash

echo "Creating directory structure..."

mkdir -p chapters
mkdir -p appendices

# Create chapters ch1.tex ... ch40.tex
for i in $(seq 1 40); do
    filename="chapters/ch$i.tex"
    if [ ! -f "$filename" ]; then
        echo "% Chapter $i" > "$filename"
        echo "\\chapter{Chapter $i Title}" >> "$filename"
        echo "" >> "$filename"
        echo "% Your content here" >> "$filename"
        echo "Created $filename"
    fi
done

# Create appendices appA.tex ... appE.tex
for app in A B C D E; do
    filename="appendices/app${app}.tex"
    if [ ! -f "$filename" ]; then
        echo "% Appendix $app" > "$filename"
        echo "\\chapter{Appendix $app}" >> "$filename"
        echo "" >> "$filename"
        echo "% Your content here" >> "$filename"
        echo "Created $filename"
    fi
done

echo "Done."

