package clip

import (
	goconcurrentlogger "github.com/ralvarezdev/go-concurrent-logger"
	gohailocliphandler "github.com/ralvarezdev/go-hailo-clip-handler"
)

// NewDefaultHandler creates a new CLIP handler with default settings
//
// Parameters:
//
// generateClipEmbeddingsPath: The path to the script that generates CLIP embeddings
// runClipPath: The path to the script that runs CLIP
// positiveLabels: A slice of PositiveLabel representing the positive labels for classification
// negativeLabels: A slice of NegativeLabel representing the negative labels for classification
// logger: A goconcurrentlogger.Logger instance for logging
// debug: A boolean indicating if debug logging is enabled
//
// Returns:
//
// A pointer to the DefaultHandler instance and an error if any
func NewDefaultHandler(
	generateClipEmbeddingsPath string,
	runClipPath string,
	positiveLabels []PositiveLabel,
	negativeLabels []NegativeLabel,
	logger goconcurrentlogger.Logger,
	debug bool,
) (*gohailocliphandler.DefaultHandler, error) {
	return gohailocliphandler.NewDefaultHandler(
		generateClipEmbeddingsPath,
		EmbeddingsJSONPath,
		runClipPath,
		PositiveLabelSliceToStringSlice(positiveLabels),
		NegativeLabelSliceToStringSlice(negativeLabels),
		MinimumConfidenceThreshold,
		logger,
		debug,
	)
}