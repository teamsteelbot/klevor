package pilot

import (
	"context"
	"errors"
	"fmt"
	"log"
	"os"
	"os/signal"
	"sync"
	"sync/atomic"
	"syscall"
	"time"

	"golang.org/x/sync/errgroup"

	goconcurrentlogger "github.com/ralvarezdev/go-concurrent-logger"
	gohailocliphandler "github.com/ralvarezdev/go-hailo-clip-handler"
	gorplidarsdkhandler "github.com/ralvarezdev/go-rplidar-sdk-handler"
	"github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal"
	internalusbcdc "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/usbcdc"
)

type (
	// DefaultHandler is the default implementation of the Handler interface
	DefaultHandler struct {
		mutex                         sync.Mutex
		handlerLoggerProducer         goconcurrentlogger.LoggerProducer
		logger                        goconcurrentlogger.Logger
		rplidarHandler                gorplidarsdkhandler.Handler
		clipHandler                   gohailocliphandler.Handler
		usbCDCHandler                 internalusbcdc.Handler
		usbCDCSender                  internalusbcdc.Sender
		isRunning                     atomic.Bool
		debug                         bool
	}
)

// NewDefaultHandler creates a new instance of DefaultHandler
//
// Parameters:
//
// logger: The logger to use for logging messages.
// rplidarHandler: The RPLidar handler to use for getting distance measurements.
// clipHandler: The CLIP handler to use for controlling the robot's movement.
// usbCDCHandler: The USB-CDC handler to use for communication with the robot.
// debug: A boolean indicating if debug logging is enabled.
//
// Returns:
//
// A pointer to the newly created DefaultHandler instance, or an error if the handler could not be created.
func NewDefaultHandler(
	logger goconcurrentlogger.Logger,
	rplidarHandler gorplidarsdkhandler.Handler,
	clipHandler gohailocliphandler.Handler,
	usbCDCHandler internalusbcdc.Handler,
	debug bool,
) (*DefaultHandler, error) {
	// Check if the logger is nil
	if logger == nil {
		return nil, goconcurrentlogger.ErrNilLogger
	}

	// Check if the RPLiDAR handler is nil
	if rplidarHandler == nil {
		return nil, gorplidarsdkhandler.ErrNilHandler
	}

	// Check if the CLIP handler is nil
	if clipHandler == nil {
		return nil, gohailocliphandler.ErrNilHandler
	}

	// Check if the USB-CDC handler is nil
	if usbCDCHandler == nil {
		return nil, internalusbcdc.ErrNilHandler
	}

	return &DefaultHandler{
		logger:         logger,
		rplidarHandler: rplidarHandler,
		clipHandler:    clipHandler,
		usbCDCHandler:  usbCDCHandler,
		debug:          debug,
	}, nil
}

// IsRunning returns true if the handler is running, false otherwise
//
// Returns:
//
// A boolean indicating if the handler is running
func (h *DefaultHandler) IsRunning() bool {
	return h.isRunning.Load()
}

// runToWrap is the internal function to run the pilot handler
//
// Parameters:
//
// ctx: Context for managing cancellation and timeouts.
//
// Returns:
//
// An error if the pilot could not be run, nil otherwise
func (h *DefaultHandler) runToWrap(ctx context.Context) error {
	// Initialize the USB-CDC sender
	usbCDCSender, err := h.usbCDCHandler.NewSender()
	if err != nil {
		return fmt.Errorf("failed to create USB-CDC sender: %w", err)
	}
	h.usbCDCSender = usbCDCSender
	defer func() {
		// Log the closure
		h.handlerLoggerProducer.Info("Closing USB-CDC sender...")

		// Close the sender
		h.usbCDCSender.Close()

		// Log the closure
		h.handlerLoggerProducer.Info("USB-CDC sender closed")
	}()

	// Wait for the challenge message to be set
	h.handlerLoggerProducer.Info("Waiting for challenge message...")
	challenge, err := h.usbCDCHandler.WaitForChallenge(ctx)
	if err != nil {
		return fmt.Errorf("failed to wait for challenge message: %w", err)
	}
	h.handlerLoggerProducer.Info(
		fmt.Sprintf("Challenge message received: %s", challenge.String()),
	)

	// Get the challenge handler
	var handler func(ctx context.Context) error
	switch challenge {
	case internal.ChallengeWithObstacles:
		h.handlerLoggerProducer.Info("Starting challenge with obstacles handler")
		handler = h.challengeWithObstaclesHandler
	case internal.ChallengeWithObstaclesAndParking:
		h.handlerLoggerProducer.Info("Starting challenge with obstacles and parking handler")
		handler = h.challengeWithObstaclesAndParkingHandler
	case internal.ChallengeWithoutObstacles:
		h.handlerLoggerProducer.Info("Starting challenge without obstacles handler")
		handler = h.challengeWithoutObstaclesHandler
	default:
		return fmt.Errorf("unknown challenge: %s", challenge.String())
	}

	// Create a error group for the RPLiDAR measures update goroutine
	g := errgroup.Group{}

	// Initialize the RPLiDAR measures update goroutine
	g.Go(
		func() error {
			defer func() {
				if r := recover(); r != nil {
					h.handlerLoggerProducer.Error(
						fmt.Errorf("panic recovered: %v", r),
					)
				}
				fmt.Println("RPLiDAR average distances update goroutine exited")
			}()
			return h.updateRPLiDARAverageDistances(ctx)
		},
	)

	// Initialize the CLIP classification update goroutine
	g.Go(
		func() error {
			defer func() {
				if r := recover(); r != nil {
					h.handlerLoggerProducer.Error(
						fmt.Errorf("panic recovered: %v", r),
					)
				}
				fmt.Println("CLIP classification update goroutine exited")
			}()
			return h.updateCLIPClassification(ctx)
		},
	)

	// Wait a moment to ensure the RPLiDAR and CLIP are ready
	time.Sleep(InitializationDelay)

	// Start the pilot
	g.Go(
		func() error {
			defer func() {
				if r := recover(); r != nil {
					h.handlerLoggerProducer.Error(
						fmt.Errorf("panic recovered: %v", r),
					)
				}
				fmt.Println("Pilot challenge handler goroutine exited")
			}()
			return handler(ctx)
		},
	)

	// Wait for the goroutines to finish
	return g.Wait()
}

// Run runs the pilot handler
//
// Returns:
//
// An error if the pilot could not be run, nil otherwise
func (h *DefaultHandler) Run() error {
	h.mutex.Lock()

	// Check if it's already running
	if h.IsRunning() {
		h.mutex.Unlock()
		return ErrHandlerAlreadyRunning
	}
	defer func() {
		h.mutex.Lock()

		// Set running to false
		h.isRunning.Store(false)

		h.mutex.Unlock()
	}()

	// Set running to true
	h.isRunning.Store(true)

	h.mutex.Unlock()

	// Context canceled on SIGINT/SIGTERM.
	ctx, stop := signal.NotifyContext(
		context.Background(),
		os.Interrupt,
		syscall.SIGTERM,
	)

	// Create an error group to manage goroutines
	g := errgroup.Group{}

	// Initialize the logger goroutine
	g.Go(
		func() error {
			defer fmt.Println("Logger goroutine exited")
			return h.logger.Run(ctx, stop)
		},
	)

	// Wait a moment to ensure the logger is ready
	fmt.Println("Waiting for logger to be ready...")
	if err := h.logger.WaitUntilReady(ctx); err != nil {
		log.Fatalf("failed to wait for logger readiness: %v", err)
	}
	fmt.Println("Logger is ready")

	// Create a logger producer
	handlerLoggerProducer, err := h.logger.NewProducer(
		HandlerLoggerProducerTag,
		h.debug,
	)
	if err != nil {
		return fmt.Errorf("failed to create handler logger producer: %w", err)
	}
	h.handlerLoggerProducer = handlerLoggerProducer

	// Generate the CLIP embeddings
	h.handlerLoggerProducer.Info("Generating CLIP embeddings")
	if err = h.clipHandler.GenerateEmbeddings(ctx); err != nil {
		if errors.Is(err, gohailocliphandler.ErrEmptyGenerateEmbeddingsPath) {
			h.handlerLoggerProducer.Warning(
				fmt.Sprintf("CLIP embeddings path is empty: %v", err),
			)
		} else {
			stop()
			h.handlerLoggerProducer.Error(
				fmt.Errorf("failed to generate CLIP embeddings: %w", err),
			)
			h.handlerLoggerProducer.Info("Stopping all goroutines...")
			h.handlerLoggerProducer.Close()
			return g.Wait()
		}
	}
	h.handlerLoggerProducer.Info("CLIP embeddings generated successfully")
	defer stop()

	// Initialize the CLIP goroutine
	g.Go(
		func() error {
			defer fmt.Println("CLIP goroutine exited")
			return h.clipHandler.Run(ctx, stop)
		},
	)

	// Initialize the RPLiDAR goroutine
	g.Go(
		func() error {
			defer fmt.Println("RPLiDAR goroutine exited")
			return h.rplidarHandler.Run(ctx, stop)
		},
	)

	// Initialize the USB-CDC goroutine
	g.Go(
		func() error {
			defer fmt.Println("USB-CDC goroutine exited")
			return h.usbCDCHandler.Run(ctx, stop)
		},
	)

	// Wait USB-CDC to be ready
	h.handlerLoggerProducer.Info("Waiting for USB-CDC handler to be ready...")
	if err := h.usbCDCHandler.WaitUntilReady(ctx); err != nil {
		stop()
		h.handlerLoggerProducer.Error(
			fmt.Errorf(
				"failed to wait for USB-CDC handler readiness: %w",
				err,
			),
		)
		h.handlerLoggerProducer.Info("Stopping all goroutines...")
		h.handlerLoggerProducer.Close()
		return g.Wait()
	}
	h.handlerLoggerProducer.Info("USB-CDC handler is ready")

	// Initialize the run to wrap goroutine
	g.Go(
		func() error {
			defer func() {
				if r := recover(); r != nil {
					h.handlerLoggerProducer.Error(
						fmt.Errorf("panic recovered: %v", r),
					)
				}
				h.handlerLoggerProducer.Close()
				stop()
			}()

			return goconcurrentlogger.StopContextAndLogOnError(
				ctx,
				stop,
				func(ctx context.Context) error {
					return h.runToWrap(ctx)
				},
				h.handlerLoggerProducer,
			)()
		},
	)

	// Wait for the goroutines to finish
	return g.Wait()
}
