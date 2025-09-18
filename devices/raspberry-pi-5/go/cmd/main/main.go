package main

import (
	"flag"
	"fmt"
	"log"

	internalclip "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/clip"
	internallog "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/log"
	internalpilot "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/pilot"
	internalrplidar "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/rplidar"
	internalusbcdc "github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal/usbcdc"
)

func main() {
	// Define optional flags
	clipDebug := flag.Bool("clip-debug", false, "Enable CLIP debug logging")
	rplidarDebug := flag.Bool(
		"rplidar-debug",
		false,
		"Enable RPLiDAR debug logging",
	)
	usbCDCDebug := flag.Bool(
		"usb-cdc-debug",
		false,
		"Enable USB-CDC debug logging",
	)
	pilotDebug := flag.Bool("pilot-debug", false, "Enable Pilot debug logging")

	// Define required flags
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

	// Parse flags
	flag.Parse()

	// Enforce required flags
	/*
		if *generateClipEmbeddingsPath == "" {
			log.Fatal("missing required flag: --generate-clip-embeddings-path")
		}
	*/
	if *runClipPath == "" {
		log.Fatal("missing required flag: --run-clip-path")
	}

	// Initialize the logger
	logger, err := internallog.NewDefaultLogger()
	if err != nil {
		log.Fatalf("failed to create logger: %v\n", err)
	}

	// Initialize the CLIP handler
	clipHandler, err := internalclip.NewDefaultHandler(
		*generateClipEmbeddingsPath,
		*runClipPath,
		internalclip.PositiveLabels,
		internalclip.NegativeLabels,
		logger,
		*clipDebug,
	)
	if err != nil {
		log.Fatalf("failed to initialize clip handler: %v", err)
	}

	// Initialize the USB-CDC handler
	usbCDCHandler, err := internalusbcdc.NewDefaultHandler(
		internalusbcdc.BaudRate,
		logger,
		*usbCDCDebug,
	)
	if err != nil {
		log.Fatalf("failed to initialize usb-cdc handler: %v", err)
	}

	// Initialize the Slamtec C1 handler
	rplidarHandler, err := internalrplidar.NewSlamtecC1Handler(
		logger,
		*rplidarDebug,
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
		*pilotDebug,
	)
	if err != nil {
		log.Fatalf("failed to initialize pilot handler: %v", err)
	}

	// Print a startup message
	fmt.Println("Klevor Raspberry Pi 5 device is up and running")

	// Run the pilot handler
	if err = pilotHandler.Run(); err != nil {
		log.Fatalf("failed to run pilot handler: %v", err)
	}
}
