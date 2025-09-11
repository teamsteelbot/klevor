//go:build tinygo && (rp2040 || rp2350)

package tinygo_bno08x

import (
	"time"

	"machine"

	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

/*
Reset reasons from ID Report response:
0 – Not Applicable
1 – Power On Reset
2 – Internal System Reset
3 – Watchdog Timeout
4 – External Reset
5 – Other
*/

type (
	// BNO08X struct represents the BNO08x IMU sensor
	BNO08X struct {
		packetReader                    PacketReader
		packetWriter                    PacketWriter
		debugger                        Debugger
		resetPin                        machine.Pin
		dataBuffer                      DataBuffer
		commandBuffer                   []byte
		dynamicConfigurationDataSavedAt time.Time
		meCalibrationStartedAt          time.Time
		calibrationComplete             bool
		magnetometerAccuracy            ReportAccuracyStatus
		initComplete                    bool
		accelerometer                   [3]float64
		gravity                         [3]float64
		gyroscope                       [3]float64
		magnetometer                    [3]float64
		linearAcceleration              [3]float64
		rotationVector                  [4]float64
		geomagneticRotationVector       [4]float64
		gameRotationVector              [4]float64
		stepCount                       uint16
		shakesDetected                  bool
		stabilityClassification         ReportStabilityClassification
		mostLikelyClassification        ReportClassification
		classifications                 [ReportClassificationsNumber]int
		rawAccelerometer                [3]float64
		rawGyroscope                    [3]float64
		rawMagnetometer                 [3]float64
		enabledFeatures                 map[uint8]bool
		afterHardwareResetFn                    func(b *BNO08X) func() tinygotypes.ErrorCode
		afterResetFn                    func(b *BNO08X) tinygotypes.ErrorCode
	}

	// Options struct holds configuration options for the BNO08X instance
	Options struct {
		Debugger Debugger // Debugger instance for debug messages
	}
)

// NewOptions creates a new Options instance with the specified debugger.
//
// Parameters:
//
//	debugger: The Debugger instance for debug messages.
//
// Returns:
//
// A pointer to a new Options instance.
func NewOptions(debugger Debugger) *Options {
	return &Options{
		Debugger: debugger,
	}
}

// NewBNO08X creates a new BNO08X instance with the specified reset pin and debug mode
//
// Parameters:
//
//  resetPin: The pin used to reset the BNO08X sensor.
//	packetReader: The PacketReader to read packets from the BNO08X sensor.
//	packetWriter: The PacketWriter to write packets to the BNO08X sensor.
//	dataBuffer: The DataBuffer to store Packet data.
//	afterHardwareResetFn: An optional function to be called after a hardware reset.
//	afterResetFn: An optional function to be called after a software reset.
//	options: Optional configuration options for the BNO08X instance.
//
// Returns:
//
// A pointer to a new BNO08X instance or an error if initialization fails.
func NewBNO08X(
	resetPin machine.Pin,
	packetReader PacketReader,
	packetWriter PacketWriter,
	dataBuffer DataBuffer,
	afterHardwareResetFn func(b *BNO08X) func() tinygotypes.ErrorCode,
	afterResetFn func(b *BNO08X) tinygotypes.ErrorCode,
	options *Options,
) (*BNO08X, tinygotypes.ErrorCode) {
	// Check if packetReader, packetWriter and dataBuffer are provided
	if packetReader == nil {
		return nil, ErrorCodeBNO08XNilPacketReader
	}
	if packetWriter == nil {
		return nil, ErrorCodeBNO08XNilPacketWriter
	}
	if dataBuffer == nil {
		return nil, ErrorCodeBNO08XNilDataBuffer
	}

	// If options are nil, initialize with default values
	if options == nil {
		options = NewOptions(nil)
	}

	// Create the BNO08X instance
	bno08x := &BNO08X{
		packetReader:                    packetReader,
		packetWriter:                    packetWriter,
		debugger:                        options.Debugger,
		resetPin:                        resetPin,
		dataBuffer:                      dataBuffer,
		commandBuffer:                   make([]byte, CommandBufferSize),
		calibrationComplete:             false,
		magnetometerAccuracy:            ReportAccuracyStatusUnreliable,
		initComplete:                    false,
		stepCount:                       0,
		shakesDetected:                  false,
		stabilityClassification:        ReportStabilityClassificationUnknown,
		mostLikelyClassification:        ReportClassificationUnknown,
		enabledFeatures:                 make(map[uint8]bool),
		afterHardwareResetFn:            afterHardwareResetFn,
		afterResetFn:            afterResetFn,
	}

	// Perform reset
	if err := bno08x.Reset(); err != tinygotypes.ErrorCodeNil {
		return nil, ErrorCodeBNO08XFailedToResetBNO08X
	}
	return bno08x, tinygotypes.ErrorCodeNil
}

// hardwareReset performs a hardware reset of the BNO08X sensor using the specified reset pin.
func (b *BNO08X) hardwareReset() {
	if b.afterHardwareResetFn == nil {
		HardwareReset(b.resetPin, b.debugger, nil)
	} else {
		HardwareReset(b.resetPin, b.debugger, b.afterHardwareResetFn(b))
	}
}

// softwareReset performs a software reset of the BNO08X sensor to an initial unconfigured state.
//
// Returns:
//
// An error if the reset process fails, otherwise nil.
func (b *BNO08X) softwareReset() tinygotypes.ErrorCode {
	if b.debugger != nil {
		b.debugger.Debug("Software resetting...")
	}

	// Send the reset command
	if _, err := b.packetWriter.SendPacket(ChannelExe, ResetCommandData); err != tinygotypes.ErrorCodeNil {
		return ErrorCodeBNO08XFailedToSendResetCommandRequestPacket
	}

	// Clear out any packets that may have been sent during the reset process
	time.Sleep(ResetPacketDelay)

	// Clear out any pending packets
	startTime := time.Now()
	for time.Since(startTime) < MaxClearPendingPacketsTimeout {
		packet, err := b.waitForPacket(WaitForPacketTimeout)
		if err == ErrorCodeBNO08XWaitingForPacketTimedOut {
			break
		}
		if err != tinygotypes.ErrorCodeNil {
			// Log the error
			if b.debugger != nil {
				b.debugger.Debug("Error waiting for packet: " + uint16ToHex(uint16(err)))
			}
			continue
		}

		// Log what we're clearing
		if b.debugger != nil {
			if packet.ChannelNumber() == ChannelSHTPCommand && len(packet.Data) == AdvertisementPacketLength {
				b.debugger.Debug("Found SHTP advertisement packet")
			} else {
				b.debugger.Debug("Clearing packet from channel " + uint8ToHex(packet.ChannelNumber()) + " with " + intToString(len(packet.Data)) + " bytes")
			}
		}
	}
	

	// Wait for the reset to complete
	if b.debugger != nil {
		b.debugger.Debug("Software reset complete")
	}
	return tinygotypes.ErrorCodeNil
}

// Reset performs the initial setup of the BNO08X sensor, including hardware and software resets.
//
// Returns:
//
// An error if the initialization fails, otherwise nil.
func (b *BNO08X) Reset() tinygotypes.ErrorCode {
	// Try up to 3 times to initialize the sensor
	for i := 0; i < ResetAttempts; i++ {
		// Hardware reset
		b.hardwareReset()

		// Software reset
		if err := b.softwareReset(); err != tinygotypes.ErrorCodeNil {
			return err
		}

		// Reset enabled features
		for k := range b.enabledFeatures {
			delete(b.enabledFeatures, k)
		}

		// Clear calibration status
		b.calibrationComplete = false

		// Check if the sensor ID can be read
		if err := b.checkID(); err != tinygotypes.ErrorCodeNil {
			b.debugger.Debug("An error ocurred while waiting for the sensor ID: " + uint16ToHex(uint16(err)))
			time.Sleep(CheckIDDelay)
			continue
		}
		
		// Call after reset function if provided
		if b.afterResetFn != nil {
			if err := b.afterResetFn(b); err != tinygotypes.ErrorCodeNil {
				return err
			}
		}
		return tinygotypes.ErrorCodeNil
	}
	return ErrorCodeBNO08XFailedToReadSensorID
}

// checkID checks if the sensor ID can be read from the BNO08X sensor.
//
// Returns:
//
// An error if there was an issue during the ID check process, otherwise nil.
func (b *BNO08X) checkID() tinygotypes.ErrorCode {
	if b.debugger != nil {
		b.debugger.Debug("READ ID REQUEST")
	}

	// Send the ID request report
	if b.debugger != nil {
		b.debugger.Debug("Sending ID Request Report")
	}
	if _, err := b.packetWriter.SendPacket(
		ChannelControl,
		ReportIDProductIDRequestData,
	); err != tinygotypes.ErrorCodeNil {
		return err
	}

	// Wait for the ID response report
	reportID := ReportIDProductIDResponse
	packet, err := b.waitForPacketType(
		ChannelControl,
		&reportID,
	)
	if err != tinygotypes.ErrorCodeNil {
		return err
	}

	// Read the Packet data into the data buffer
	sensorIDReport, err := newReportFromPacket(packet)
	if err != tinygotypes.ErrorCodeNil {
		return err
	}

	// Parse the sensor ID from the report
	sensorID, err := newSensorID(sensorIDReport)
	if err != tinygotypes.ErrorCodeNil {
		return err
	}

	// Log the sensor ID details
	if b.debugger != nil {
		b.debugger.DebugBuffer(sensorID.PrintBuffer())
	}
	return tinygotypes.ErrorCodeNil
}

// waitForPacketType waits for a Packet of a specific type on a given channel, optionally filtering by report ID.
//
// Parameters:
//
//	channelNumber: The channel number to wait for.
//	reportID: An optional pointer to a report ID to filter packets by.
//
// Returns:
//
//	A pointer to the Packet if found, or an error if the timeout is reached or an error occurs.
func (b *BNO08X) waitForPacketType(
	channelNumber uint8,
	reportID *uint8,
) (*Packet, tinygotypes.ErrorCode) {
	startTime := time.Now()

	// Debug message
	if b.debugger != nil {
		if reportID == nil {
			b.debugger.Debug("** Waiting for Packet on Channel " + uint8ToHex(channelNumber) + " **")
		} else {
			b.debugger.Debug("** Waiting for Packet with Report ID " + uint8ToHex(*reportID) + " on Channel " + uint8ToHex(channelNumber) + " **")
		}
	}

	// Loop until timeout
	for time.Since(startTime) < WaitForPacketTypeTimeout {
		// Check if data is ready to be read
		newPacket, err := b.waitForPacket(WaitForPacketTypeTimeout - time.Since(startTime))
		if err != tinygotypes.ErrorCodeNil {
			continue
		}

		// If the packet is on the desired channel, check the report ID if provided
		if newPacket.ChannelNumber() == channelNumber {
			if reportID == nil {
				return newPacket, tinygotypes.ErrorCodeNil
			}

			// Get the report ID of the new packet
			newPacketReportID, err := newPacket.ReportID()
			if err != tinygotypes.ErrorCodeNil {
				return nil, err
			}

			// If the report ID matches, return the packet
			if newPacketReportID == *reportID {
				return newPacket, tinygotypes.ErrorCodeNil
			}
		}

		if newPacket.ChannelNumber() != ChannelExe && newPacket.ChannelNumber() != ChannelSHTPCommand {
			if b.debugger != nil {
				b.debugger.Debug("Passing Packet to handler for de-slicing")
			}
			if err = b.handlePacket(newPacket); err != tinygotypes.ErrorCodeNil {
				return nil, err
			}
		}
	}
	return nil, ErrorCodeBNO08XWaitingForPacketTimedOut
}

// waitForPacket waits for a Packet to be available from the Packet reader within the specified timeout.
//
// Parameters:
//
//	timeout: The maximum duration to wait for a Packet.
//
// Returns:
//
//	A pointer to the Packet if available, or an error if the timeout is reached or an error occurs.
func (b *BNO08X) waitForPacket(timeout time.Duration) (*Packet, tinygotypes.ErrorCode) {
	startTime := time.Now()
	for time.Since(startTime) < timeout {
		// Check if data is ready to be read
		if !b.packetReader.IsDataReady() {
			time.Sleep(PacketReadyCheckDelay)
			continue
		}

		// Read the Packet from the Packet reader
		newPacket, err := b.packetReader.ReadPacket()
		if err != tinygotypes.ErrorCodeNil {
			if b.debugger != nil {
				b.debugger.Debug("An error occurred when reading a packet while waiting for a packet: " + uint16ToHex(uint16(err)))
			}
			continue
		}
		return newPacket, tinygotypes.ErrorCodeNil
	}
	return nil, ErrorCodeBNO08XWaitingForPacketTimedOut
}

// handlePacket processes a Packet by separating it into individual reports and processing each report.
//
// Parameters:
//
//	Packet: A pointer to the Packet to be processed.
//
// Returns:
//
//	An error if the Packet cannot be processed, otherwise nil.
func (b *BNO08X) handlePacket(packet *Packet) tinygotypes.ErrorCode {
	// Check if the packet is nil
	if packet == nil {
		return ErrorCodeBNO08XNilPacket
	}

	// Check if the packet header is nil
	if packet.Header == nil {
		return ErrorCodeBNO08XNilPacketHeader
	}

	// Check packet data length
	if len(packet.Data) != int(packet.Header.DataLength) {
		return ErrorCodeBNO08XMismatchedPacketDataLength
	}

	// Ensure the Packet has a valid header
	idx := 0
	for idx < packet.Header.DataLength {
		// Check if there are enough bytes left in the Packet to read the report ID
		reportID := packet.Data[idx]
		
		if b.debugger != nil {
			b.debugger.Debug("Processing report ID: " + uint8ToHex(reportID) + " at index " + intToString(idx))
		}

		requiredBytes, err := ReportLength(reportID)
		if err != tinygotypes.ErrorCodeNil {
			return ErrorCodeBNO08XFailedToGetReportLengthForTheGivenReportID
		}
		unprocessedByteCount := packet.Header.DataLength - idx

		// If there are not enough bytes left, return an error
		if unprocessedByteCount < requiredBytes {
			return ErrorCodeBNO08XUnprocessableBatchBytes
		}

		// Create a new report from the Packet data
		reportData := packet.Data[idx : idx+requiredBytes]
		report, err := newReport(reportID, reportData)
		if err != tinygotypes.ErrorCodeNil {
			return err
		}

		// Process the report
		if err := b.processReport(report); err != tinygotypes.ErrorCodeNil {
			if b.debugger != nil {
				b.debugger.Debug("Failed to process report ID " + uint8ToHex(report.ID))
			}
			return err
		}

		// Move to the next report in the Packet
		idx += requiredBytes
	}
	return tinygotypes.ErrorCodeNil
}

// processReport processes a report by checking if it is a control report or a sensor report, and then parsing the data accordingly.
//
// Parameters:
//
//	report: A pointer to the report to be processed.
//
// Returns:
//
//	An error if the report cannot be processed, otherwise nil.
func (b *BNO08X) processReport(report *report) tinygotypes.ErrorCode {
	// Check if the report is nil
	if report == nil {
		return ErrorCodeBNO08XNilReport
	}

	// Check if it's a control report
	if IsControlReportID(report.ID) {
		return b.processControlReport(report)
	}

	// Check if the feature that was reported is enabled
	if enabled, ok := b.enabledFeatures[report.ID]; !ok || !enabled {
		b.enabledFeatures[report.ID] = true
	}

	if b.debugger != nil {
		b.debugger.Debug("Processing report: " + SHTPCommandNameString(report.ID) + " (" + uint8ToHex(report.ID) + ")")
	}

	// Process the sensor report based on its ID+
	switch report.ID {
	case ReportIDStepCounter:
		// Parse the step counter report
		stepCounterReport, err := newStepCounterReport(report)
		if err != tinygotypes.ErrorCodeNil {
			return ErrorCodeBNO08XFailedToParseStepCounterReport
		}

		// Update the step count in the BNO08X instance
		b.stepCount = stepCounterReport.Count
	case ReportIDShakeDetector:
		// Parse the shake detector report
		shakeReport, err := newShakeReport(report)
		if err != tinygotypes.ErrorCodeNil {
			return ErrorCodeBNO08XFailedToParseShakeReport
		}

		// Update the shake detection status in the BNO08X instance
		b.shakesDetected = shakeReport.AreShakesDetected
	case ReportIDStabilityClassifier:
		// Parse the stability classifier report
		stabilityReport, err := newStabilityClassifierReport(report)
		if err != tinygotypes.ErrorCodeNil {
			return ErrorCodeBNO08XFailedToParseStabilityClassifierReport
		}

		// Update the stability classification in the BNO08X instance
		b.stabilityClassification = stabilityReport.StabilityClassification
	case ReportIDActivityClassifier:
		// Parse the activity classifier report
		activityReport, err := newActivityClassifierReport(report)
		if err != tinygotypes.ErrorCodeNil {
			return ErrorCodeBNO08XFailedToParseActivityClassifierReport
		}

		// Update the activity classification and classifications in the BNO08X instance
		b.classifications = activityReport.Classifications
	case ReportIDMagnetometer:
		// Parse the magnetometer report
		magnetometerReport, err := newThreeDimensionalReport(report)
		if err != tinygotypes.ErrorCodeNil {
			return ErrorCodeBNO08XFailedToParseMagnetometerReport
		}

		// Update the magnetometer readings in the BNO08X instance
		b.magnetometerAccuracy = magnetometerReport.Accuracy
		b.magnetometer = magnetometerReport.Results
	case ReportIDRotationVector:
		// Parse the rotation vector report
		rotationReport, err := newFourDimensionalReport(report)
		if err != tinygotypes.ErrorCodeNil {
			return ErrorCodeBNO08XFailedToParseRotationVectorReport
		}

		// Update the rotation vector readings in the BNO08X instance
		b.rotationVector = rotationReport.Results
	case ReportIDGeomagneticRotationVector:
		// Parse the geomagnetic rotation vector report
		geomagneticReport, err := newFourDimensionalReport(report)
		if err != tinygotypes.ErrorCodeNil {
			return ErrorCodeBNO08XFailedToParseGeomagneticRotationVectorReport
		}

		// Update the geomagnetic rotation vector readings in the BNO08X instance
		b.geomagneticRotationVector = geomagneticReport.Results
	case ReportIDGameRotationVector:
		// Parse the game rotation vector report
		gameReport, err := newFourDimensionalReport(report)
		if err != tinygotypes.ErrorCodeNil {
			return ErrorCodeBNO08XFailedToParseGameRotationVectorReport
		}

		// Update the game rotation vector readings in the BNO08X instance
		b.gameRotationVector = gameReport.Results
	case ReportIDAccelerometer:
		// Parse the accelerometer report
		accelerometerReport, err := newThreeDimensionalReport(report)
		if err != tinygotypes.ErrorCodeNil {
			return ErrorCodeBNO08XFailedToParseAccelerometerReport
		}

		// Update the accelerometer readings in the BNO08X instance
		b.accelerometer = accelerometerReport.Results
	case ReportIDLinearAcceleration:
		// Parse the linear acceleration report
		linearAccelerationReport, err := newThreeDimensionalReport(report)
		if err != tinygotypes.ErrorCodeNil {
			return ErrorCodeBNO08XFailedToParseLinearAccelerationReport
		}

		// Update the linear acceleration readings in the BNO08X instance
		b.linearAcceleration = linearAccelerationReport.Results
	case ReportIDGravity:
		// Parse the gravity report
		gravityReport, err := newThreeDimensionalReport(report)
		if err != tinygotypes.ErrorCodeNil {
			return ErrorCodeBNO08XFailedToParseGravityReport
		}

		// Update the gravity readings in the BNO08X instance
		b.gravity = gravityReport.Results
	case ReportIDGyroscope:
		// Parse the gyroscope report
		gyroscopeReport, err := newThreeDimensionalReport(report)
		if err != tinygotypes.ErrorCodeNil {
			return ErrorCodeBNO08XFailedToParseGyroscopeReport
		}

		// Update the gyroscope readings in the BNO08X instance
		b.gyroscope = gyroscopeReport.Results
	case ReportIDRawAccelerometer:
		// Parse the raw accelerometer report
		rawAccelerometerReport, err := newThreeDimensionalReport(report)
		if err != tinygotypes.ErrorCodeNil {
			return ErrorCodeBNO08XFailedToParseRawAccelerometerReport
		}

		// Update the raw accelerometer readings in the BNO08X instance
		b.rawAccelerometer = rawAccelerometerReport.Results
	case ReportIDRawGyroscope:
		// Parse the raw gyroscope report
		rawGyroscopeReport, err := newThreeDimensionalReport(report)
		if err != tinygotypes.ErrorCodeNil {
			return ErrorCodeBNO08XFailedToParseRawGyroscopeReport
		}

		// Update the raw gyroscope readings in the BNO08X instance
		b.rawGyroscope = rawGyroscopeReport.Results
	case ReportIDRawMagnetometer:
		// Parse the raw magnetometer report
		rawMagnetometerReport, err := newThreeDimensionalReport(report)
		if err != tinygotypes.ErrorCodeNil {
			return ErrorCodeBNO08XFailedToParseRawMagnetometerReport
		}

		// Update the raw magnetometer readings in the BNO08X instance
		b.rawMagnetometer = rawMagnetometerReport.Results
	}
	return tinygotypes.ErrorCodeNil
}

// processControlReport processes control reports and updates the BNO08X state accordingly.
//
// Parameters:
//
//	report: A pointer to the report containing control data.
//
// Returns:
//
//	An error if the control report cannot be processed, otherwise nil.
func (b *BNO08X) processControlReport(report *report) tinygotypes.ErrorCode {
	// Check if the report is nil
	if report == nil {
		return ErrorCodeBNO08XNilReport
	}

	// Handle the control report based on its ID
	switch report.ID {
	case ReportIDProductIDResponse:
		// Parse the sensor ID from the report bytes
		sensorID, err := newSensorID(report)
		if err != tinygotypes.ErrorCodeNil {
			return ErrorCodeBNO08XFailedToParseSensorID
		}

		if b.debugger != nil {
			b.debugger.DebugBuffer(sensorID.PrintBuffer())
		}
	case ReportIDGetFeatureResponse:
		// Parse the Get Feature report from the report bytes
		getFeatureReport, err := newGetFeatureReport(report)
		if err != tinygotypes.ErrorCodeNil {
			return ErrorCodeBNO08XFailedToParseGetFeatureReport
		}

		// Set the feature as enabled
		b.enabledFeatures[getFeatureReport.FeatureReportID] = true
	case ReportIDCommandResponse:
		// Parse the command response from the report bytes
		commandResponse, err := newCommandResponse(report)
		if err != tinygotypes.ErrorCodeNil {
			return err
		}

		// Get the command and its status from the command response
		command := commandResponse.Command
		commandStatus := commandResponse.Status()

		
		if command == MagnetometerCalibration && commandStatus == 0 {
			b.meCalibrationStartedAt = time.Now()
		}

		if command == SaveDynamicCalibrationData {
			if commandStatus != 0 {
				return ErrorCodeBNO08XFailedToSaveDynamicCalibrationData
			}

			// Record the time when dynamic configuration data was saved
			b.dynamicConfigurationDataSavedAt = time.Now()
		}
	}
	return tinygotypes.ErrorCodeNil
}

// processAvailablePackets processes all available packets from the Packet reader, handling each Packet until the maximum number of packets is reached.
func (b *BNO08X) processAvailablePackets() {
	processedCount := 0
	for b.packetReader.IsDataReady() {
		// Check if we've reached the maximum number of packets to process
		if processedCount >= MaxPackets {
			break
		}

		// Read the next available Packet
		newPacket, err := b.packetReader.ReadPacket()
		if err != tinygotypes.ErrorCodeNil {
			if b.debugger != nil {
				b.debugger.Debug("Error reading Packet: " + uint16ToHex(uint16(err)))
			}
			continue
		}

		// Pass the packet to the handler
		if err = b.handlePacket(newPacket); err != tinygotypes.ErrorCodeNil {
			if b.debugger != nil {
				b.debugger.Debug("Error handling Packet: " + uint16ToHex(uint16(err)))
			}
			continue
		}
		processedCount++
	}
}

// Update processes all available packets from the Packet reader to update the sensor data.
func (b *BNO08X) Update() {
	b.processAvailablePackets()
}

// GetMagnetic returns the current magnetic field measurements on the X, Y, and Z axes.
//
// Returns:
//
// A pointer to a [3]float64 array containing the magnetic field values.
func (b *BNO08X) GetMagnetic() [3]float64 {
	return b.magnetometer
}

// GetQuaternion returns a pointer to a [4]float64 array representing the current rotation vector as a quaternion.
//
// Returns:
//
// A pointer to a [4]float64 array containing the quaternion values.
func (b *BNO08X) GetQuaternion() [4]float64 {
	return b.rotationVector
}

// GetGeomagneticQuaternion returns a pointer to a [4]float64 array representing the current geomagnetic rotation vector as a quaternion.
//
// Returns:
//
// A pointer to a [4]float64 array containing the geomagnetic quaternion values.
func (b *BNO08X) GetGeomagneticQuaternion() [4]float64 {
	return b.geomagneticRotationVector
}

// GetGameQuaternion returns a pointer to a [4]float64 array representing the current rotation vector expressed as a quaternion with no specific reference for heading.
//
// Returns:
//
// A pointer to a [4]float64 array containing the game quaternion values.
func (b *BNO08X) GetGameQuaternion() [4]float64 {
	return b.gameRotationVector
}

// GetSteps returns the number of steps detected since the sensor was initialized.
//
// Returns:
//
//	A pointer to an uint16 representing the step count.
func (b *BNO08X) GetSteps() uint16 {
	return b.stepCount
}

// GetLinearAcceleration returns the current linear acceleration values on the X, Y, and Z axes in meters per second squared.
//
// Returns:
//
//	A pointer to a [3]float64 array containing the linear acceleration values.
func (b *BNO08X) GetLinearAcceleration() [3]float64 {
	return b.linearAcceleration
}

// GetAcceleration returns the acceleration measurements on the X, Y, and Z axes in meters per second squared.
//
// Returns:
//
//	A pointer to a [3]float64 array containing the acceleration values.
func (b *BNO08X) GetAcceleration() [3]float64 {
	return b.accelerometer
}

// GetGravity returns the gravity vector in the X, Y, and Z components in meters per second squared.
//
// Returns:
//
//	A pointer to a [3]float64 array containing the gravity vector.
func (b *BNO08X) GetGravity() [3]float64 {
	return b.gravity
}

// GetGyro returns Gyro's rotation measurements on the X, Y, and Z axes in radians per second.
//
// Returns:
//
//	A pointer to a [3]float64 array containing the gyroscope values.
func (b *BNO08X) GetGyro() [3]float64 {
	return b.gyroscope
}

// GetShake returns true if a shake was detected on any axis since the last time it was checked.
// This method has a latching behavior: once a shake is detected, it stays "shaken" until read.
//
// Returns:
//
//	A pointer to a bool indicating if a shake was detected.
func (b *BNO08X) GetShake() bool {
	// If a shake was detected, clear the flag on read
	if b.shakesDetected {
		b.shakesDetected = false
	}
	return b.shakesDetected
}

// GetStabilityClassification returns the sensor's assessment of its current stability.
//
// Returns:
//
//	The stability classification as a ReportStabilityClassification value.
func (b *BNO08X) GetStabilityClassification() ReportStabilityClassification {
	return b.stabilityClassification
}

// GetActivityClassification returns the sensor's assessment of the activity creating the sensed motions.
//
// Returns:
//
//	A pointer to a map[string]int representing activity classifications.
func (b *BNO08X) GetActivityClassification() [ReportClassificationsNumber]int {
	return b.classifications
}

// GetRawAcceleration returns the sensor's raw, unscaled value from the accelerometer registers.
//
// Returns:
//
//	A pointer to a [3]float64 array containing the raw accelerometer values.
func (b *BNO08X) GetRawAcceleration() [3]float64 {
	return b.rawAccelerometer
}

// GetRawGyro returns the sensor's raw, unscaled value from the gyro registers.
//
// Returns:
//
//	A pointer to a [3]float64 array containing the raw gyroscope values.
func (b *BNO08X) GetRawGyro() [3]float64 {
	return b.rawGyroscope
}

// GetRawMagnetic returns the sensor's raw, unscaled value from the magnetometer registers.
//
// Returns:
//
//	A pointer to a [3]float64 array containing the raw magnetometer values.
func (b *BNO08X) GetRawMagnetic() [3]float64 {
	return b.rawMagnetometer
}

// EnableFeature enables a given feature of the BNO08X sensor.
//
// Parameters:
//
//	featureID: The ID of the feature to enable.
//
// Returns:
//
//	An error if the feature could not be enabled.
func (b *BNO08X) EnableFeature(featureID uint8) tinygotypes.ErrorCode {
	for i := 0; i < EnableFeatureAttempts; i++ {
		if b.debugger != nil {
			b.debugger.Debug("Enabling Feature ID: " + uint8ToHex(featureID))
		}

		// Check if debug mode is enabled
		var interval uint32
		if b.debugger != nil {
			interval = DebugReportInterval
		} else {
			interval = DefaultReportInterval
		}

		// Create the feature enable report based on the feature ID
		var setFeatureReport []byte
		if featureID == ReportIDActivityClassifier {
			setFeatureReport = newSetFeatureEnableReportData(
				featureID,
				interval,
				EnabledActivities,
			)
		} else {
			setFeatureReport = newSetFeatureEnableReportData(
				featureID,
				interval,
				0,
			)
		}

		// Check if the feature has a dependency
		featureDependency, ok := RawReports[featureID]
		if ok && !b.IsFeatureEnabled(featureDependency) {
			if err := b.EnableFeature(featureDependency); err != tinygotypes.ErrorCodeNil {
				continue
			}
		}

		// Send the feature enable report
		if _, err := b.packetWriter.SendPacket(
			ChannelControl,
			setFeatureReport,
		); err != tinygotypes.ErrorCodeNil {
			continue
		}

		// Wait for the feature to be enabled
		startTime := time.Now()
		for time.Since(startTime) < FeatureEnableTimeout {
			b.Update()
			if b.IsFeatureEnabled(featureID) {
				return tinygotypes.ErrorCodeNil
			}
		}
	}
	return ErrorCodeBNO08XFailedToEnableFeature
}

// IsFeatureEnabled checks if a specific feature is enabled on the BNO08X sensor.
//
// Parameters:
//
//	featureID: The ID of the feature to check.
//
// Returns:
//
//	A boolean indicating whether the feature is enabled.
func (b *BNO08X) IsFeatureEnabled(featureID uint8) bool {
	return b.enabledFeatures[featureID]
}

// BeginCalibration starts the self-calibration routine for the BNO08X sensor.
//
// Returns:
//
// An error indicating success or failure of the calibration initiation.
func (b *BNO08X) BeginCalibration() tinygotypes.ErrorCode {
	// Begin the sensor's self-calibration routine
	calibrationBuffer := []byte{
		1, // calibrate accel
		1, // calibrate gyro
		1, // calibrate mag
		MagnetometerCalibrationConfig,
		0, // calibrate planar acceleration
		0, // 'on_table' calibration
		0, // reserved
		0, // reserved
		0, // reserved
	}
	if err := b.sendMeCommand(calibrationBuffer); err != tinygotypes.ErrorCodeNil {
		return ErrorCodeBNO08XFailedToBeginCalibration
	}
	return tinygotypes.ErrorCodeNil
}

// CalibrationStatus retrieves the status of the self-calibration process.
//
// Returns:
//
// An integer representing the calibration status, where 0 indicates no calibration needed,
func (b *BNO08X) CalibrationStatus() ReportAccuracyStatus {
	// Get the status of the self-calibration
	calibrationBuffer := []byte{
		0, // calibrate accel
		0, // calibrate gyro
		0, // calibrate mag
		MagnetometerGetCalibration,
		0, // calibrate planar acceleration
		0, // 'on_table' calibration
		0, // reserved
		0, // reserved
		0, // reserved
	}
	b.sendMeCommand(calibrationBuffer)

	// Log the calibration status if debugger is enabled
	if b.debugger != nil {
		b.debugger.Debug("CalibrationStatus: " + b.magnetometerAccuracy.String())
	}
	return b.magnetometerAccuracy
}

// IsCalibrated checks if the BNO08X sensor accuracy status is medium or high.
//
// Returns:
//
// A boolean indicating whether the sensor is calibrated (medium or high accuracy).
func (b *BNO08X) IsCalibrated() bool {
	calibrationStatus := b.CalibrationStatus()
	return calibrationStatus == ReportAccuracyStatusMedium || calibrationStatus == ReportAccuracyStatusHigh
}

// sendMeCommand sends a command to the BNO08X sensor using the ME command protocol.
//
// Parameters:
//
//	subcommandParams: A byte slice containing the parameters for the command.
func (b *BNO08X) sendMeCommand(subcommandParams []byte) tinygotypes.ErrorCode {
	// Check if the subcommandParams is nil
	if subcommandParams == nil {
		return ErrorCodeBNO08XNilSubcommandParams
	}

	// Start the command request process
	startTime := time.Now()

	// Insert the command request report into the local buffer
	if err := insertCommandRequestReport(
		MagnetometerCalibration,
		b.commandBuffer,
		b.dataBuffer.GetReportSequenceNumber(ReportIDCommandRequest),
		subcommandParams,
	); err != tinygotypes.ErrorCodeNil {
		return ErrorCodeBNO08XFailedToInsertCommandRequestReport
	}

	// Send the command request Packet
	if _, err := b.packetWriter.SendPacket(ChannelControl, b.commandBuffer); err != tinygotypes.ErrorCodeNil {
		return ErrorCodeBNO08XFailedToSendMeCommandRequestPacket
	}
	b.dataBuffer.IncrementReportSequenceNumber(ReportIDCommandRequest)

	// Wait for the command response
	for time.Since(startTime) < CalibrationCommandsTimeout {
		b.Update()
		if b.meCalibrationStartedAt.After(startTime) {
			break
		}
	}
	return tinygotypes.ErrorCodeNil
}

// SaveCalibrationData saves the self-calibration data to the BNO08X sensor.
//
// Returns:
//
// An error if the calibration data could not be saved, otherwise nil.
func (b *BNO08X) SaveCalibrationData() tinygotypes.ErrorCode {
	// Save the self-calibration data
	startTime := time.Now()
	err := insertCommandRequestReport(
		SaveDynamicCalibrationData,
		b.commandBuffer,
		b.dataBuffer.GetReportSequenceNumber(ReportIDCommandRequest),
		nil,
	)
	if err != tinygotypes.ErrorCodeNil {
		return err
	}

	// Send the command request Packet to save calibration data
	_, err = b.packetWriter.SendPacket(ChannelControl, b.commandBuffer)
	if err != tinygotypes.ErrorCodeNil {
		return ErrorCodeBNO08XFailedToSendCommandRequestPacketToSaveCalibrationData
	}
	b.dataBuffer.IncrementReportSequenceNumber(ReportIDCommandRequest)

	// Wait for the command response indicating that the calibration data was saved
	for time.Since(startTime) < CalibrationCommandsTimeout {
		b.Update()
		if b.dynamicConfigurationDataSavedAt.After(startTime) {
			return tinygotypes.ErrorCodeNil
		}
	}
	return ErrorCodeBNO08XFailedToSaveCalibrationData
}
