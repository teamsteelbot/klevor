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
		AddSpace()
		AddNewline()
		AddTab()
		AddHexCode(hexCode []byte, newline bool)
		AddErrorCode(errCode tinygotypes.ErrorCode, newline bool)
		AddUint8(value uint8, newline bool, hexCode bool)
		AddUint16(value uint16, newline bool, hexCode bool)
		AddUint32(value uint32, newline bool, hexCode bool)
		AddMessage(message []byte, newline bool)
		AddMessageWithHexCode(message []byte, hexBuffer []byte, separate bool, newline bool)
		AddMessageWithErrorCode(message []byte, errCode tinygotypes.ErrorCode, separate bool, newline bool)
		AddMessageWithUint8(message []byte, value uint8, separate bool, newline bool, hexCode bool)
		AddMessageWithUint16(message []byte, value uint16, separate bool, newline bool, hexCode bool)
		AddMessageWithUint32(message []byte, value uint32, separate bool, newline bool, hexCode bool)
		Debug()
		DebugMessage(message []byte)
		Info()
		InfoMessage(message []byte)
		Warning()
		WarningMessage(message []byte)
		WarningMessageWithErrorCode(message []byte, errCode tinygotypes.ErrorCode, separate bool)
		Error()
		ErrorMessage(message []byte)
		ErrorMessageWithErrorCode(message []byte, errCode tinygotypes.ErrorCode, separate bool)
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
