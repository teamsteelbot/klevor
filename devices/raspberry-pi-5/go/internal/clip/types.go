package clip

import (
	"bufio"
	"bytes"
	"context"
	"errors"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"sync"
	"sync/atomic"
	"time"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal"
	internallog "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/log"
	"golang.org/x/sync/errgroup"
)

type (
	// DefaultHandler is the handler for the Hailo CLIP application
	DefaultHandler struct {
		handlerMutex                     sync.Mutex
		classificationMutex              sync.RWMutex
		isRunning                        atomic.Bool
		generateClipEmbeddingsPath       string
		runClipPath                      string
		positiveLabels                   *[]internal.PositiveLabel
		negativeLabels                   *[]internal.NegativeLabel
		classification                   *internal.Classification
		stdoutLinesRead                  int
		clipApplicationInitialized       bool
		logger                           internallog.Logger
		handlerLoggerProducer            internallog.LoggerProducer
		generateEmbeddingsLoggerProducer internallog.LoggerProducer
	}
)

// NewDefaultHandler creates a new DefaultHandler instance.
//
// Parameters:
//
// generateClipEmbeddingsPath: Path to the .sh file that generates CLIP embeddings.
// runClipPath: Path to the .sh file that runs CLIP.
// positiveLabels: Slice of positive labels for classification.
// negativeLabels: Slice of negative labels for classification (optional, can be nil).
// logger: Logger instance for logging messages.
//
// Returns:
//
// A pointer to a DefaultHandler instance or an error if any parameter is invalid.
func NewDefaultHandler(
	generateClipEmbeddingsPath,
	runClipPath string,
	positiveLabels *[]internal.PositiveLabel,
	negativeLabels *[]internal.NegativeLabel,
	logger internallog.Logger,
) (*DefaultHandler, error) {
	// Check if the logger is nil
	if logger == nil {
		return nil, internallog.ErrNilLogger
	}

	// Check if the runClipPath is empty
	if runClipPath == "" {
		return nil, ErrEmptyRunClipPath
	}

	// Check if the positiveLabels is nil
	if positiveLabels == nil {
		return nil, ErrNilPositiveLabels
	}

	// Create a new DefaultHandler instance
	handler := &DefaultHandler{
		generateClipEmbeddingsPath: generateClipEmbeddingsPath,
		runClipPath:                runClipPath,
		positiveLabels:             positiveLabels,
		negativeLabels:             negativeLabels,
		logger:                     logger,
	}

	return handler, nil
}

// generateEmbeddingsJSONContent generates the content for the embeddings JSON file.
//
// Returns:
//
// A string containing the JSON content.
func (h *DefaultHandler) generateEmbeddingsJSONContent() string {
	var builder strings.Builder

	// Add the opening brace and positive labels key
	builder.WriteString("{\n")
	builder.WriteString("\t\"")
	builder.WriteString(EmbeddingsJSONPositiveKeyName)
	builder.WriteString("\": [\n")

	// Add the positive labels
	for i, label := range *h.positiveLabels {
		builder.WriteString("\t\t\"")
		builder.WriteString(label.String())
		builder.WriteString("\"")
		if i < len(*h.positiveLabels)-1 {
			builder.WriteString(",\n")
		} else {
			builder.WriteString("\n")
		}
	}

	// Add the negative labels
	if h.negativeLabels == nil {
		builder.WriteString("\t]\n")
	} else {
		builder.WriteString("\t],\n")
		builder.WriteString("\t\"")
		builder.WriteString(EmbeddingsJSONNegativeKeyName)
		builder.WriteString("\": [\n")
		for i, label := range *h.negativeLabels {
			builder.WriteString("\t\t\"")
			builder.WriteString(label.String())
			builder.WriteString("\"")
			if i < len(*h.negativeLabels)-1 {
				builder.WriteString(",\n")
			} else {
				builder.WriteString("\n")
			}
		}
		builder.WriteString("\t]\n")
	}

	// Add the closing brace
	builder.WriteString("}\n")
	return builder.String()
}

// GenerateEmbeddings generates CLIP embeddings by executing the specified script.
//
// Returns:
//
// An error if any issue occurs during the execution of the script.
func (h *DefaultHandler) GenerateEmbeddings() error {
	// Check if the generateClipEmbeddingsPath is empty
	if h.generateClipEmbeddingsPath == "" {
		return ErrEmptyGenerateEmbeddingsPath
	}

	// Create a logger producer
	generateEmbeddingsLoggerProducer, err := h.logger.NewProducer(
		GenerateEmbeddingsLoggerProducerTag,
	)
	if err != nil {
		return fmt.Errorf("failed to create generate embeddings logger producer: %w", err)
	}
	h.generateEmbeddingsLoggerProducer = generateEmbeddingsLoggerProducer
	defer h.generateEmbeddingsLoggerProducer.Close()

	// Log the start of generating embeddings
	h.generateEmbeddingsLoggerProducer.Info(GenerateEmbeddingsStartMessage)

	// Generate JSON file
	jsonContent := h.generateEmbeddingsJSONContent()

	// Ensure the directory for the JSON file exists
	parentDir := filepath.Dir(EmbeddingsJSONPath)
	if err := os.MkdirAll(parentDir, os.ModePerm); err != nil {
		return fmt.Errorf(
			"failed to create directory for embeddings JSON file: %w",
			err,
		)
	}

	// Write the JSON content to the file
	if err := os.WriteFile(
		EmbeddingsJSONPath,
		[]byte(jsonContent),
		0644,
	); err != nil {
		return fmt.Errorf("failed to write embeddings JSON file: %w", err)
	}

	// Check if the generate embeddings executable exists
	if _, err := os.Stat(h.generateClipEmbeddingsPath); errors.Is(
		err,
		os.ErrNotExist,
	) {
		return fmt.Errorf(
			"generate embeddings executable not found at path: %s",
			h.generateClipEmbeddingsPath,
		)
	}

	// Arguments (do not include the executable itself)
	args := []string{
		GenerateEmbeddingsJSONPathArgument,
		EmbeddingsJSONPath,
		GenerateEmbeddingsThresholdArgument,
		fmt.Sprintf("%f", MinimumConfidenceThreshold),
	}

	// Execute the command
	cmd := exec.Command(h.generateClipEmbeddingsPath, args...)

	var stdoutBuf, stderrBuf bytes.Buffer
	cmd.Stdout = &stdoutBuf
	cmd.Stderr = &stderrBuf

	// Run and wait
	if err := cmd.Run(); err != nil {
		h.generateEmbeddingsLoggerProducer.Warning(
			fmt.Sprintf(
				"Embeddings script failed: %v; stderr: %s",
				err,
				strings.TrimSpace(stderrBuf.String()),
			),
		)
		return fmt.Errorf("generate embeddings script error: %w", err)
	}

	// Log outputs if debug
	if h.generateEmbeddingsLoggerProducer.IsDebug() {
		stdout := strings.TrimSpace(stdoutBuf.String())
		if stdout != "" {
			h.generateEmbeddingsLoggerProducer.Debug(
				fmt.Sprintf(
					"embeddings script stdout: %s",
					stdout,
				),
			)
		}
		stderr := strings.TrimSpace(stderrBuf.String())
		if stderr != "" {
			h.generateEmbeddingsLoggerProducer.Debug(
				fmt.Sprintf(
					"embeddings script stderr: %s",
					stderr,
				),
			)
		}
	}

	h.generateEmbeddingsLoggerProducer.Info(GenerateEmbeddingsCompletedMessage)
	return nil
}

// IsRunning returns whether the handler is currently running.
//
// Returns:
//
// True if the handler is running, false otherwise.
func (h *DefaultHandler) IsRunning() bool {
	return h.isRunning.Load()
}

// runToWrap is the internal function to read incoming classifications from the CLIP application.
//
// Parameters:
//
// ctx: Context for managing cancellation and timeouts.
// stopFn: Function to call to stop the context.
//
// Returns:
//
// An error if any issue occurs during execution.
func (h *DefaultHandler) runToWrap(ctx context.Context, stopFn func()) error {
	// Reset the stdout lines read counter
	h.stdoutLinesRead = 0

	// Log the start of reading measures
	h.handlerLoggerProducer.Info(HandlerStartedMessage)

	// Check if the run clip executable exists
	if _, err := os.Stat(h.runClipPath); errors.Is(err, os.ErrNotExist) {
		return fmt.Errorf(
			"run clip executable not found at path: %s",
			h.runClipPath,
		)
	}

	// Execute the command with a context
	cmd := exec.CommandContext(ctx, h.runClipPath)

	// Stream output line by line
	stdout, err := cmd.StdoutPipe()
	if err != nil {
		return fmt.Errorf("stdout pipe error: %w", err)
	}
	stderr, err := cmd.StderrPipe()
	if err != nil {
		return fmt.Errorf("stderr pipe error: %w", err)
	}

	// Start the command
	if err = cmd.Start(); err != nil {
		return fmt.Errorf("start command error: %w", err)
	}

	// Create an error group to wait for all goroutines to finish
	g := &errgroup.Group{}

	// Stream stdout
	g.Go(
		internallog.StopContextAndLogOnError(
			ctx,
			stopFn, 
			func(ctx context.Context) error {
				return h.scanLines(
					ctx,
					StdoutTag,
					stdout,
					h.handleStdoutLine,
				)
			},
			h.handlerLoggerProducer,
		),
	)

	// Stream stderr
	g.Go(
		internallog.StopContextAndLogOnError(
			ctx,
			stopFn, 
			func(ctx context.Context) error {
				return h.scanLines(
					ctx,
					StderrTag,
					stderr,
					h.handleStderrLine,
				)
			},
			h.handlerLoggerProducer,
		),
	)

	// Wait for completion or context cancel
	if err = g.Wait(); err != nil && !errors.Is(err, context.Canceled) {
		return fmt.Errorf("error reading lines: %w", err)
	}

	// Close the stdout and stderr pipes
	if err = stdout.Close(); err != nil {
		return fmt.Errorf("stdout close error: %w", err)
	}
	if err = stderr.Close(); err != nil {
		return fmt.Errorf("stderr close error: %w", err)
	}

	// Signal the process to stop
	_ = cmd.Process.Signal(os.Interrupt) // Unix

	// Sleep for a grace period to allow clean shutdown
	time.Sleep(CloseTimeout)

	// Hard kill fallback if still running after grace period
	if cmd.ProcessState == nil || !cmd.ProcessState.Exited() {
		_ = cmd.Process.Kill()
	}
	return nil
}

// Run reads incoming classifications from the CLIP application.
//
// Parameters:
//
// ctx: Context for managing cancellation and timeouts.
// stopFn: Function to call to stop the context.
//
// Returns:
//
// An error if any issue occurs during reading or processing classifications.
func (h *DefaultHandler) Run(ctx context.Context, stopFn func()) error {
	h.handlerMutex.Lock()

	// Check if it's already running
	if h.IsRunning() {
		h.handlerMutex.Unlock()
		return ErrHandlerAlreadyRunning
	}
	defer func() {
		h.handlerMutex.Lock()

		// Set running to false
		h.isRunning.Store(false)

		h.handlerMutex.Unlock()
	}()

	// Set running to true
	h.isRunning.Store(true)

	h.handlerMutex.Unlock()

	// Create a logger producer
	handlerLoggerProducer, err := h.logger.NewProducer(
		HandlerLoggerProducerTag,
	)
	if err != nil {
		return fmt.Errorf("failed to create handler logger producer: %w", err)
	}
	h.handlerLoggerProducer = handlerLoggerProducer
	defer h.handlerLoggerProducer.Close()

	return internallog.LogOnError(
		func() error {
			return h.runToWrap(ctx, stopFn)
		},
		h.handlerLoggerProducer,
	)
}

// scanLines reads lines from the provided reader and processes them using the given lineHandler.
//
// Parameters:
//
// ctx: Context for managing cancellation and timeouts.
// tag: Tag to identify the source of the lines (e.g., "stdout" or "stderr").
// r: Reader to read lines from.
// lineHandler: Function to process each line.
//
// Returns:
//
// An error if any issue occurs during reading or processing lines.
func (h *DefaultHandler) scanLines(
	ctx context.Context,
	tag string,
	r interface{ Read([]byte) (int, error) },
	lineHandler func(string) error,
) error {
	// Check if the lineHandler is nil
	if lineHandler == nil {
		return ErrNilLineHandler
	}

	// Create a new scanner
	sc := bufio.NewScanner(r)

	// Set the buffer size
	buf := make([]byte, 0, InitialSizeBuffer)
	sc.Buffer(buf, MaxSizeBuffer)

	for sc.Scan() {
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
			// Read the line
			line := strings.TrimSpace(sc.Text())

			// Process the line
			if h.handlerLoggerProducer.IsDebug() {
				h.handlerLoggerProducer.Debug(
					fmt.Sprintf(
						"Received line from %s: %s",
						tag,
						line,
					),
				)
			}

			// Handle the line
			if err := lineHandler(line); err != nil {
				return err
			}
		}
	}

	// Check for scanning errors
	if err := sc.Err(); err != nil {
		return fmt.Errorf("scan error: %w", err)
	}
	return nil
}

// handleStdoutLine processes a single line from stdout.
//
// Parameters:
//
// line: The line to process.
//
// Returns:
//
// An error if any issue occurs during processing the line.
func (h *DefaultHandler) handleStdoutLine(line string) error {
	// Increment the stdout lines read counter
	h.stdoutLinesRead++

	// Check if the message should be ignored
	if h.stdoutLinesRead <= IgnoreFirstStdoutMessages {
		return nil
	}

	// Check if the Clip Application has been initialized
	if !h.clipApplicationInitialized {
		if line == HailoClipApplicationInitializedMessage {
			h.clipApplicationInitialized = true
			h.handlerLoggerProducer.Info(HailoClipApplicationInitializedMessage)
		}
		return nil
	}

	// Lock the measures map for writing
	h.classificationMutex.Lock()
	defer h.classificationMutex.Unlock()

	// Check if there is a classification in the line
	if line == NoClassification {
		h.handlerLoggerProducer.Info("No classification detected")
		h.classification = nil
		return nil
	}

	// Create a classification from the given string
	classification, err := internal.NewClassificationFromString(line)
	if err != nil {
		h.handlerLoggerProducer.Warning(
			fmt.Sprintf(
				"Failed to parse classification: %v",
				err,
			),
		)
		return nil // Ignore parsing errors
	}

	// Check if the confidence is below the threshold
	if classification.Confidence < MinimumConfidenceThreshold {
		h.handlerLoggerProducer.Info(
			fmt.Sprintf(
				"Ignoring classification of label '%s' with low confidence: %f",
				classification.Label.String(),
				classification.Confidence,
			),
		)
		return nil
	}

	// Update the current classification
	if h.classification != classification {
		h.handlerLoggerProducer.Info(
			fmt.Sprintf(
				"New classification detected for label '%s' with confidence: %f",
				classification.Label.String(),
				classification.Confidence,
			),
		)
	}
	h.classification = classification
	return nil
}

// GetClassification returns a copy of the current classification.
//
// Returns:
//
// A copy of the current classification.
func (h *DefaultHandler) GetClassification() *internal.Classification {
	// Lock the classification for reading
	h.classificationMutex.RLock()
	defer h.classificationMutex.RUnlock()

	// Create a copy of the classification
	if h.classification == nil {
		return nil
	}
	classification, _ := internal.NewClassification(
		h.classification.Label,
		h.classification.Confidence,
	)
	return classification
}

// handleStderrLine processes a single line from stderr.
//
// Parameters:
//
// line: The line to process.
//
// Returns:
//
// An error if any issue occurs during processing the line.
func (h *DefaultHandler) handleStderrLine(line string) error {
	// Log the stderr line as a warning
	h.handlerLoggerProducer.Warning(fmt.Sprintf("stderr: %s", line))
	return nil
}
