package clip

import (
	"path/filepath"

	gohailocliphandler "github.com/ralvarezdev/go-hailo-clip-handler"
	"github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal"
)

const (
	// MinimumConfidenceThreshold is the minimum confidence threshold for a valid classification
	MinimumConfidenceThreshold float32 = 0.8
)

var (
	// EmbeddingsJSONPath is the path where the embeddings JSON file is stored
	EmbeddingsJSONPath string

	// PositiveLabels are the positive labels for CLIP
	PositiveLabels = []PositiveLabel{
		PositiveLabelMagentaBlock,
		PositiveLabelGreenBlock,
		PositiveLabelRedBlock,
	}

	// NegativeLabels are the negative labels for CLIP
	NegativeLabels = []NegativeLabel{
		NegativeLabelBackground,
		NegativeLabelBlackBlock,
	}
)

func init() {
	// Initialize EmbeddingsJSONFilename with the correct path
	EmbeddingsJSONPath = filepath.Join(
		internal.DataFolderPath,
		gohailocliphandler.EmbeddingsJSONFilename,
	)
}
