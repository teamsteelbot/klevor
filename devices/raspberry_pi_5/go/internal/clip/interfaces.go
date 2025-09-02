package clip

import (
	"context"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal"
)

type (
	// Handler is the interface to handle the Hailo CLIP application
	Handler interface {
		GenerateEmbeddings() error
		ReadIncomingClassifications(ctx context.Context) error
		GetClassification() *internal.Classification
	}
)
