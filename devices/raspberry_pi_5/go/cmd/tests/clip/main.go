package main

import (
	"flag"
)

func main() {
	// Define flags
	logDebug := flag.Bool("debug", false, "Enable debug logging")
	generateClipEmbeddingsPath := flag.String(
		"generate-clip-embeddings-path",
		"",
		"Path to the .sh file that generates CLIP embeddings",
	)
	runClipPath := flag.String(
		"run-clip-path",
		"",
		"Path to the .sh file that runs CLIP",
	)
	flag.Parse()

}
