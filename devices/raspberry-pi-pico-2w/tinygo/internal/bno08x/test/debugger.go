//go:build tinygo && (rp2040 || rp2350)

package tinygo_bno08x

type (
	// DefaultDebugger is a simple implementation of the Debugger interface
	DefaultDebugger struct{}
)

// NewDefaultDebugger creates a new DefaultDebugger instance
func NewDefaultDebugger() *DefaultDebugger {
	return &DefaultDebugger{}
}

// Debug function to print debug messages
//
// Parameters:
//
//	message: The debug message to print.
func (d *DefaultDebugger) Debug(message string) {
	print(DebugHeader)
	println(message)
}

// DebugBuffer function to print debug messages with buffer content
//
// Parameters:
//
//	buffer: The byte slice to print in hexadecimal format.
func (d *DefaultDebugger) DebugBuffer(buffer []byte) {
	if buffer == nil {
		return
	}
	d.Debug(string(buffer))
}
