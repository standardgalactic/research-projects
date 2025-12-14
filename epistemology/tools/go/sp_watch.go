package main

import (
	"crypto/sha256"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"time"
)

func hashTree(root string) ([32]byte, error) {
	h := sha256.New()
	err := filepath.Walk(root, func(path string, info os.FileInfo, err error) error {
		if err != nil { return err }
		if info.IsDir() {
			base := filepath.Base(path)
			if base == ".git" || base == "build" || base == "logs" || base == ".notebooks_cache" {
				return filepath.SkipDir
			}
			return nil
		}
		ext := filepath.Ext(path)
		switch ext {
		case ".tex", ".bib", ".lean", ".py", ".hs", ".rkt":
			f, e := os.Open(path)
			if e != nil { return e }
			defer f.Close()
			_, _ = io.Copy(h, f)
		}
		return nil
	})
	if err != nil { return [32]byte{}, err }
	var out [32]byte
	copy(out[:], h.Sum(nil))
	return out, nil
}

func main() {
	if len(os.Args) < 3 {
		fmt.Println("usage: sp-watch <dir> <command...>")
		os.Exit(2)
	}
	dir := os.Args[1]
	cmdArgs := os.Args[2:]

	prev, err := hashTree(dir)
	if err != nil {
		fmt.Fprintf(os.Stderr, "hash error: %v\n", err)
		os.Exit(1)
	}

	fmt.Println("[sp-watch] watching:", dir)
	for {
		time.Sleep(2 * time.Second)
		now, err := hashTree(dir)
		if err != nil {
			fmt.Fprintf(os.Stderr, "hash error: %v\n", err)
			continue
		}
		if now != prev {
			fmt.Println("[sp-watch] change detected, running:", cmdArgs)
			c := exec.Command(cmdArgs[0], cmdArgs[1:]...)
			c.Stdout = os.Stdout
			c.Stderr = os.Stderr
			_ = c.Run()
			prev = now
		}
	}
}

