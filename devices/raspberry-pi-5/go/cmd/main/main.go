package main

import (
	"flag"
	"log"

	internalclip "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/clip"
	internallog "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/log"
	internalpilot "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/pilot"
	internalrplidar "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/rplidar"
	internalusbcdc "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/usbcdc"
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

	// Enforce required flags
	if *generateClipEmbeddingsPath == "" {
		log.Fatal("missing required flag: --generate-clip-embeddings-path")
	}
	if *runClipPath == "" {
		log.Fatal("missing required flag: --run-clip-path")
	}

	// Initialize the logger
	logger := internallog.NewDefaultLogger(*logDebug)

	// Initialize the CLIP handler
	clipHandler, err := internalclip.NewDefaultHandler(
		*generateClipEmbeddingsPath,
		*runClipPath,
		internalclip.PositiveLabels,
		internalclip.NegativeLabels,
		logger,
	)
	if err != nil {
		log.Fatalf("failed to initialize clip handler: %v", err)
	}

	// Initialize the USB-CDC handler
	usbCDCHandler, err := internalusbcdc.NewDefaultHandler(
		internalusbcdc.BaudRate,
		logger,
	)
	if err != nil {
		log.Fatalf("failed to initialize usb-cdc handler: %v", err)
	}

	// Initialize the Slamtec C1 handler
	rplidarHandler, err := internalrplidar.NewSlamtecC1Handler(
		internalrplidar.SlamtecC1BaudRate,
		internalrplidar.SlamtecC1Port,
		true,
		0.0,
		logger,
	)
	if err != nil {
		log.Fatalf("failed to initialize rplidar handler: %v", err)
	}

	// Initialize the Pilot handler
	pilotHandler, err := internalpilot.NewDefaultHandler(
		logger,
		rplidarHandler,
		clipHandler,
		usbCDCHandler,
	)
	if err != nil {
		log.Fatalf("failed to initialize pilot handler: %v", err)
	}

	// Run the pilot handler
	if err = pilotHandler.Run(); err != nil {
		log.Fatalf("failed to run pilot handler: %v", err)
	}
}
