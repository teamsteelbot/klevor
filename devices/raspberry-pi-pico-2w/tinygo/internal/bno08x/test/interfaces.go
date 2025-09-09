//go:build tinygo && (rp2040 || rp2350)

package tinygo_bno08x

type (
	// PacketReader is an interface for reading packets from the BNO08x sensor
	PacketReader interface {
		ReadPacket() (*Packet, error)
		IsDataReady() bool
	}

	// PacketWriter is an interface for writing packets to the BNO08x sensor
	PacketWriter interface {
		SendPacket(channel uint8, data *[]byte) (uint8, error)
	}

	// BNO08XService is an interface to wrap the BNO08X implementation methods.
	BNO08XService interface {
		Update()
		GetAcceleration() *[3]float64
		GetEulerDegrees() *[3]float64
		Initialize() error
		HardwareReset()
		SoftwareReset() error
		Reset() error
	}
)
