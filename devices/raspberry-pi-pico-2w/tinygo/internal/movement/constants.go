package movement

import (
	"machine"

	internalpullupenabler "github.com/ralvarezdev/klevor/devices/raspberry_pi_pico_2w/tinygo/internal/pullup/enabler"
)

var (
	// Handler is the handler for the pull-down for the movement mode.
	Handler = internalpullupenabler.NewDefaultHandlerFromPin(machine.GPIO14)
)

func init() {
	// Call the setup function to initialize the pull-up enabler
	Handler.Setup()
}
