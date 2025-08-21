package bno08x

import (
	bno08x "github.com/ralvarezdev/go-adafruit-bno08x"
)

type (
	// DefaultHandler is the default handler for the BNO08x sensor.
	DefaultHandler struct {
		bno08x.BNO08X
	}
)
