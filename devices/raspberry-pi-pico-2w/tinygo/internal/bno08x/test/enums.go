//go:build tinygo && (rp2040 || rp2350)

package go_bno08x

type (
	// ReportAccuracyStatus is an enumeration of accuracy status values
	ReportAccuracyStatus int
)

const (
	ReportAccuracyStatusUnreliable ReportAccuracyStatus = iota
	ReportAccuracyStatusLow
	ReportAccuracyStatusMedium
	ReportAccuracyStatusHigh
)