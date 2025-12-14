package main

import (
	"bufio"
	"fmt"
	"os"
	"strings"
)

/*
  rsvp-validate
  Lightweight manuscript lint:
  - flags discouraged hype-terms in *public* theory summaries (you can extend list)
  - checks for duplicate section headers (common in stitched TeX)
  - warns if bibliography missing
*/

var discouraged = []string{
	"quaternion", "octonion", // your preference: avoid these terms due to woo co-option
	"get rich quick", "quantum woo",
}

func main() {
	in := bufio.NewScanner(os.Stdin)
	sections := map[string]int{}
	lineNo := 0
	hasBib := false

	for in.Scan() {
		lineNo++
		line := in.Text()
		lower := strings.ToLower(line)

		if strings.Contains(lower, "thebibliography") || strings.Contains(lower, "\\bibliography") {
			hasBib = true
		}

		if strings.HasPrefix(strings.TrimSpace(line), "\\section{") ||
			strings.HasPrefix(strings.TrimSpace(line), "\\subsection{") ||
			strings.HasPrefix(strings.TrimSpace(line), "\\subsubsection{") {

			key := strings.TrimSpace(line)
			sections[key]++
		}

		for _, t := range discouraged {
			if strings.Contains(lower, t) {
				fmt.Printf("warn:%d discouraged_term=%q\n", lineNo, t)
			}
		}
	}

	for k, n := range sections {
		if n > 1 {
			fmt.Printf("warn duplicate_header count=%d header=%s\n", n, k)
		}
	}
	if !hasBib {
		fmt.Println("warn missing_bibliography (no \\bibliography or thebibliography detected)")
	}

	if err := in.Err(); err != nil {
		fmt.Fprintf(os.Stderr, "error reading stdin: %v\n", err)
		os.Exit(1)
	}
}

