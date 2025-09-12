//go:build tinygo && (rp2040 || rp2350)

package tinygo_bno08x

import (
	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

type (
	// PacketBuffer is an interface for managing packet buffers
	PacketBuffer interface {
		GetBuffer() []byte
		SetBufferValue(index int, value byte) tinygotypes.ErrorCode
		SetBuffer(data []byte) tinygotypes.ErrorCode
		ClearBuffer()
		UpdateSequenceNumber(newPacket *Packet) tinygotypes.ErrorCode
		IncrementChannelSequenceNumber(channel uint8) (uint8, tinygotypes.ErrorCode)
		GetSequenceNumber(channel uint8) (uint8, tinygotypes.ErrorCode)
		SetSequenceNumber(channel uint8, sequenceNumber uint8) tinygotypes.ErrorCode
		IncrementReportSequenceNumber(reportID uint8)
		GetReportSequenceNumber(reportID uint8) uint8
		ResetSequenceNumbers()
	}

	// Logger is an interface for logging messages
	Logger interface {
		LogMessage(messageBuffer []byte, header bool, newline bool)
		LogMessageWithHexCode(messageBuffer []byte, hexBuffer []byte, header bool, newline bool)
		LogMessageWithUint8AsHexCode(messageBuffer []byte, value uint8, header bool, newline bool)
		LogMessageWithUint16AsHexCode(messageBuffer []byte, value uint16, header bool, newline bool)
		LogMessageWithUint32AsHexCode(messageBuffer []byte, value uint32, header bool, newline bool)
		LogMessageWithErrorCode(messageBuffer []byte, errCode tinygotypes.ErrorCode, header bool, newline bool)
		LogErrorCode(errCode tinygotypes.ErrorCode, header bool, newline bool)
		LogHexCode(hexBuffer []byte, header bool, newline bool)
	}

	// PacketReader is an interface for reading packets from the BNO08x sensor
	PacketReader interface {
		ReadPacket() (*Packet, tinygotypes.ErrorCode)
		IsAvailableToRead() bool
	}

	// PacketWriter is an interface for writing packets to the BNO08x sensor
	PacketWriter interface {
		SendPacket(channel uint8, data []byte) (uint8, tinygotypes.ErrorCode)
	}

	// BNO08XSimpleService is an interface to wrap the BNO08X implementation basic methods.
	BNO08XSimpleService interface {
		Reset() tinygotypes.ErrorCode
		Update()
		GetAcceleration() [3]float64
		GetQuaternion() [4]float64
	}

	// BNO08XService is an interface to wrap the BNO08X implementation methods.
	BNO08XService interface {
		Reset() tinygotypes.ErrorCode
		Update()
		GetMagnetic() [3]float64
		GetQuaternion() [4]float64
		GetGeomagneticQuaternion() [4]float64
		GetGameQuaternion() [4]float64
		GetSteps() uint16
		GetLinearAcceleration() [3]float64
		GetAcceleration() [3]float64
		GetGravity() [3]float64
		GetGyro() [3]float64
		GetShake() bool
		GetStabilityClassification() ReportStabilityClassification
		GetActivityClassification()  [ReportClassificationsNumber]int
		GetRawAcceleration() [3]float64
		GetRawGyro() [3]float64
		GetRawMagnetic() [3]float64
		EnableFeature(featureID uint8) tinygotypes.ErrorCode
		IsFeatureEnabled(featureID uint8) bool
		BeginCalibration() tinygotypes.ErrorCode
		CalibrationStatus() ReportAccuracyStatus 
		IsCalibrated() bool
		SaveCalibrationData() tinygotypes.ErrorCode
	}
)
