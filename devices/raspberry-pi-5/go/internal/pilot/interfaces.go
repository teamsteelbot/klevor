package pilot

type (
	// Handler is the interface for the pilot handler
	Handler interface {
		Run() error
		IsRunning() bool
	}
)
