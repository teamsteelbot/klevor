package clip

import (
	"errors"
)

var (
	ErrNilHandler                  = errors.New("handler cannot be nil")
	ErrNilLineHandler              = errors.New("line handler cannot be nil")
	ErrNilPositiveLabels           = errors.New("positive labels cannot be nil")
	ErrEmptyGenerateEmbeddingsPath = errors.New("generate embeddings path cannot be empty")
	ErrEmptyRunClipPath            = errors.New("run clip path cannot be empty")
	ErrHandlerAlreadyRunning       = errors.New("handler is already running")
)
