package cyw43439

import (
	"os"
	
	soypatcyw43439 "github.com/soypat/cyw43439"
	"github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal"
)

var (
	// Device is the CYW43439 device instance.
	Device = soypatcyw43439.NewPicoWDevice()

	// WifiConfig is the default Wi-Fi configuration.
	WifiConfig = soypatcyw43439.DefaultWifiConfig()

	// failedToInitializeCwy43439Message is the message printed when cyw43439 initialization fails
	failedToInitializeCwy43439Message = []byte("Failed to initialize CYW43439 Device:")
)

// init initializes the CYW43439 device with the default Wi-Fi configuration.
func init() {
	if err := Device.Init(WifiConfig); err != nil {
		internal.Logger.ErrorMessageWithErrorCode(failedToInitializeCwy43439Message, ErrorCodeCyw43439FailedToInitialize, true)
		os.Exit(1)
	}
}
