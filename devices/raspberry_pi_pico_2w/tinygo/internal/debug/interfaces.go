package debug

type (
	// Handler is the interface to manage the debug state.
	Handler interface {
		IsEnabled() bool
		IsDisabled() bool
	}
)
