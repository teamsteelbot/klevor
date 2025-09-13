package clip

import (
	goconcurrentlogger "github.com/ralvarezdev/go-concurrent-logger"
	gohailocliphandler "github.com/ralvarezdev/go-hailo-clip-handler"
)

// NewDefaultHandler creates a new CLIP handler with default settings
func NewDefaultHandler(
	generateClipEmbeddingsPath string,
	runClipPath string,
	positiveLabels []PositiveLabel,
	negativeLabels []NegativeLabel,
	logger goconcurrentlogger.Logger,
) (*gohailocliphandler.DefaultHandler, error) {
	// Convert 
	return gohailocliphandler.NewDefaultHandler(
		generateClipEmbeddingsPath,
		EmbeddingsJSONPath,
		runClipPath,
		PositiveLabelSliceToStringSlice(positiveLabels),
		NegativeLabelSliceToStringSlice(negativeLabels),
		MinimumConfidenceThreshold,
		logger,
	)
}