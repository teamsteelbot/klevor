package cyw43439

import (
	"fmt"

	soypatcyw43439 "github.com/soypat/cyw43439"
)

var (
	// Device is the CYW43439 device instance.
	Device = soypatcyw43439.NewPicoWDevice()

	// WifiConfig is the default Wi-Fi configuration.
	WifiConfig = soypatcyw43439.DefaultWifiConfig()
)

// init initializes the CYW43439 device with the default Wi-Fi configuration.
func init() {
	err := Device.Init(WifiConfig)
	if err != nil {
		panic(fmt.Errorf("failed to initialize cyw43439 device: %w", err))
	}
}
