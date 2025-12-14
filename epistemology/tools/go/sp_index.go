package main

import (
	"encoding/json"
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"strings"
)

type Counts struct {
	Tex     int `json:"tex"`
	Bib     int `json:"bib"`
	Lean    int `json:"lean"`
	Python  int `json:"python"`
	Haskell int `json:"haskell"`
	Racket  int `json:"racket"`
	Other   int `json:"other"`
}

type Index struct {
	Root   string `json:"root"`
	Counts Counts `json:"counts"`
	Files  []string `json:"files"`
}

func classify(path string) string {
	switch {
	case strings.HasSuffix(path, ".tex"):
		return "tex"
	case strings.HasSuffix(path, ".bib"):
		return "bib"
	case strings.HasSuffix(path, ".lean"):
		return "lean"
	case strings.HasSuffix(path, ".py"):
		return "python"
	case strings.HasSuffix(path, ".hs"):
		return "haskell"
	case strings.HasSuffix(path, ".rkt"):
		return "racket"
	default:
		return "other"
	}
}

func main() {
	root := "."
	if len(os.Args) > 1 {
		root = os.Args[1]
	}
	var idx Index
	idx.Root = root

	err := filepath.WalkDir(root, func(path string, d fs.DirEntry, err error) error {
		if err != nil { return err }
		if d.IsDir() {
			name := d.Name()
			if name == ".git" || name == "build" || name == "logs" || name == ".notebooks_cache" {
				return filepath.SkipDir
			}
			return nil
		}
		k := classify(path)
		switch k {
		case "tex":
			idx.Counts.Tex++
		case "bib":
			idx.Counts.Bib++
		case "lean":
			idx.Counts.Lean++
		case "python":
			idx.Counts.Python++
		case "haskell":
			idx.Counts.Haskell++
		case "racket":
			idx.Counts.Racket++
		default:
			idx.Counts.Other++
		}
		idx.Files = append(idx.Files, path)
		return nil
	})
	if err != nil {
		fmt.Fprintf(os.Stderr, "error: %v\n", err)
		os.Exit(1)
	}

	enc := json.NewEncoder(os.Stdout)
	enc.SetIndent("", "  ")
	_ = enc.Encode(idx)
}

