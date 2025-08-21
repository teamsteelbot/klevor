package led

import (
	"time"
)

const (
	// DefaultBlinkDelay is the default delay in milliseconds between LED blinks.
	DefaultBlinkDelay = time.Millisecond * 500

	// DefaultBlinkTimes is the default number of times the LED will blink when using the Blink method.
	DefaultBlinkTimes = 1
)
