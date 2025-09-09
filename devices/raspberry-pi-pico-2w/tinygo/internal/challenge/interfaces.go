package challenge

type (
	// Handler is the interface to manage the challenge state.
	Handler interface {
		IsWithObstacles() bool
		IsWithoutObstacles() bool
		IsWithObstaclesAndParking() bool
		GetChallenge() Challenge
	}
)
