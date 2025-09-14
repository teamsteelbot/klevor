package movement

import (
	"machine"

	tinygopullupenabler "github.com/ralvarezdev/tinygo-pullup/enabler"
)

var (
	// Handler is the handler for the pull-down for the movement mode.
	Handler = tinygopullupenabler.NewDefaultHandlerFromPin(machine.GPIO14)
)

func init() {
	// Call the setup function to initialize the pull-up enabler
	Handler.Setup()
}
