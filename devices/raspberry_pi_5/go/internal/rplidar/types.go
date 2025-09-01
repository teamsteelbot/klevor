package rplidar

import (
	"bufio"
	"context"
	"errors"
	"fmt"
	"os"
	"os/exec"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal"
	internallog "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/log"
	"golang.org/x/sync/errgroup"
)

type (
	// RotationCompleted is a signal sent when a full rotation is completed
	RotationCompleted struct{}

	// SlamtecC1Handler is the handler for the Slamtec RPLiDAR C1 device
	SlamtecC1Handler struct {
		mutex               sync.RWMutex
		logger              internallog.Logger
		rotationCompletedCh chan<- RotationCompleted
		baudrate            int
		port                string
		isUpsideDown        bool
		angleAdjustment     float64
		debug               bool
		measures            [360]*internal.Measure
		stdoutLinesRead     int
		isRotationCompleted bool
	}
)

// NewSlamtecC1Handler creates a new SlamtecC1Handler instance.
//
// Parameters:
//
// writerMessagesCh: Channel to send log messages.
// rotationCompletedCh: Channel to signal when a full rotation is completed.
// baudrate: Baud rate for the serial communication.
// port: SerialCommunication port for the RPLiDAR.
// isUpsideDown: If true, the RPLiDAR is upside down, and angles will be adjusted accordingly.
// angleAdjustment: Optional angle adjustment to apply to the angles.
//
// Returns:
//
// A pointer to a SlamtecC1Handler instance or an error if any parameter is invalid.
func NewSlamtecC1Handler(
	writerMessagesCh chan<- *internallog.Message,
	rotationCompletedCh chan<- RotationCompleted,
	baudrate int,
	port string,
	isUpsideDown bool,
	angleAdjustment float64,
	debug bool,
) (*SlamtecC1Handler, error) {
	// Check if the writerMessagesCh is nil
	if writerMessagesCh == nil {
		return nil, internallog.ErrNilWriterMessagesChannel
	}

	// Check if the rotationCompletedCh is nil
	if rotationCompletedCh == nil {
		return nil, ErrNilRotationCompletedCh
	}

	// Initialize the logger
	logger, err := internallog.NewDefaultLogger(
		writerMessagesCh,
		&LoggerTag,
		true,
		debug,
	)
	if err != nil {
		return nil, err
	}

	// Create a new SlamtecC1Handler instance
	handler := &SlamtecC1Handler{
		logger:              logger,
		rotationCompletedCh: rotationCompletedCh,
		baudrate:            baudrate,
		port:                port,
		isUpsideDown:        isUpsideDown,
		angleAdjustment:     angleAdjustment,
		debug:               debug,
	}

	return handler, nil
}

// ReadIncomingMeasures reads incoming measures from the RPLiDAR and processes them.
//
// Parameters:
//
// ctx: Context for managing cancellation and timeouts.
//
// Returns:
//
// An error if any issue occurs during reading or processing measures.
func (h *SlamtecC1Handler) ReadIncomingMeasures(ctx context.Context) error {
	// Initialize the measures slice
	h.measures = [360]*internal.Measure{}

	// Reset the stdout lines read counter
	h.stdoutLinesRead = 0

	// Reset the rotation completed flag
	h.isRotationCompleted = false

	// Log the start of reading measures
	h.logger.Info(HandlerStartedMessage)

	// Arguments (do not include the executable itself)
	args := []string{
		"--channel",
		"--serial",
		h.port,
		strconv.Itoa(h.baudrate),
	}

	// Execute the command with a context
	cmd := exec.CommandContext(ctx, UltraSimplePath, args...)

	// Stream output line by line (good for long‑running tools)
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
		func() error {
			return h.scanLines(ctx, StdoutTag, stdout, h.handleStdoutLine)
		},
	)

	// Stream stderr
	g.Go(
		func() error {
			return h.scanLines(ctx, StderrTag, stderr, h.handleStderrLine)
		},
	)

	// Wait for completion or context cancel
	if err = g.Wait(); err != nil {
		// Check if the error is due to context cancellation
		if errors.Is(err, context.Canceled) {
			h.logger.Info(internallog.ContextCancelledMessage.Content)
			return ctx.Err()
		}
		h.logger.Error(fmt.Sprintf("Error reading lines: %v", err))
		return err
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
func (h *SlamtecC1Handler) scanLines(
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
			h.logger.Info(internallog.ContextCancelledMessage.Content)
			return ctx.Err()
		default:
			// Read the line
			line := strings.TrimSpace(sc.Text())

			// Process the line
			if h.debug {
				h.logger.Debug(
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
func (h *SlamtecC1Handler) handleStdoutLine(line string) error {
	// Increment the stdout lines read counter
	h.stdoutLinesRead++

	// Check if the message should be ignored
	if h.stdoutLinesRead <= IgnoreFirstStdoutMessages {
		return nil
	}

	// Create a measure from the given string
	measure, err := internal.NewMeasureFromSlamtecC1String(
		line,
		h.isUpsideDown,
		h.angleAdjustment,
	)
	if err != nil {
		h.logger.Error(fmt.Sprintf("Failed to parse measure: %v", err))
		return nil // Ignore parsing errors
	}

	// Check if the RPLiDAR has completed a full rotation
	if measure.IsRotationCompleted() {
		h.logger.Info("Full rotation completed.")
		h.isRotationCompleted = true
	}

	// Check if the distance is within the maximum limit
	if measure.GetDistance() < 0 || measure.GetDistance() > MaxDistanceLimit {
		return nil // Ignore out-of-range distances
	}

	// Lock the measures map for writing
	h.mutex.Lock()
	defer h.mutex.Unlock()

	// Store the measure in the measures map
	angle := int(measure.GetAngle()) % 360
	h.measures[angle] = measure

	// Send the signal if a full rotation is completed
	if h.isRotationCompleted {
		h.rotationCompletedCh <- RotationCompleted{}

		// Reset the rotation completed flag
		h.isRotationCompleted = false
	}
	return nil
}

// GetMeasures returns a copy of the current measures.
//
// Returns:
//
// A copy of the current measures.
func (h *SlamtecC1Handler) GetMeasures() *[360]*internal.Measure {
	// Lock the measures map for reading
	h.mutex.RLock()
	defer h.mutex.RUnlock()

	// Create a copy of the measures map
	measuresCopy := [360]*internal.Measure{}
	copy(measuresCopy[:], h.measures[:])
	return &measuresCopy
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
func (h *SlamtecC1Handler) handleStderrLine(line string) error {
	// Log the stderr line as a warning
	h.logger.Warning(fmt.Sprintf("stderr: %s", line))
	return nil
}
