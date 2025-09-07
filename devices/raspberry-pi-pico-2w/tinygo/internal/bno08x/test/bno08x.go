//go:build tinygo && (rp2040 || rp2350)

package go_bno08x

import (
	"fmt"
	"math"
	"strings"
	"time"

	"machine"
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
	// PacketReader is an interface for reading packets from the BNO08x sensor
	PacketReader interface {
		ReadPacket() (*Packet, error)
		IsDataReady() bool
	}

	// PacketWriter is an interface for writing packets to the BNO08x sensor
	PacketWriter interface {
		SendPacket(channel uint8, data *[]byte) (uint8, error)
	}

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
		idRead                          bool
		accelerometer                   *[3]float64
		gravity                         *[3]float64
		gyroscope                       *[3]float64
		magnetometer                    *[3]float64
		linearAcceleration              *[3]float64
		rotationVector                  *[4]float64
		geomagneticRotationVector       *[4]float64
		gameRotationVector              *[4]float64
		stepCount                       *uint16
		shakesDetected                  *bool
		stabilityClassification         *string
		mostLikelyClassification        *string
		classifications                 *map[string]int
		rawAccelerometer                *[3]float64
		rawGyroscope                    *[3]float64
		rawMagnetometer                 *[3]float64
		enabledFeatures                 map[uint8]bool
		afterResetFn                    func(b *BNO08X) error
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
// resetPin: The pin used to reset the BNO08X sensor.
//
//		packetReader: The PacketReader to read packets from the BNO08X sensor.
//		packetWriter: The PacketWriter to write packets to the BNO08X sensor.
//		dataBuffer: The DataBuffer to store Packet data.
//	 afterResetFn: An optional function to be called after a reset.
//		options: Optional configuration options for the BNO08X instance.
//
// Returns:
//
// A pointer to a new BNO08X instance or an error if initialization fails.
func NewBNO08X(
	resetPin machine.Pin,
	packetReader PacketReader,
	packetWriter PacketWriter,
	dataBuffer DataBuffer,
	afterResetFn func(b *BNO08X) error,
	options *Options,
) (*BNO08X, error) {
	// Check if packetReader, packetWriter and dataBuffer are provided
	if packetReader == nil {
		return nil, ErrNilPacketReader
	}
	if packetWriter == nil {
		return nil, ErrNilPacketWriter
	}
	if dataBuffer == nil {
		return nil, ErrNilDataBuffer
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
		idRead:                          false,
		accelerometer:                   &InitialBnoSensorReportThreeDimensional,
		gravity:                         &InitialBnoSensorReportThreeDimensional,
		gyroscope:                       &InitialBnoSensorReportThreeDimensional,
		magnetometer:                    &InitialBnoSensorReportThreeDimensional,
		linearAcceleration:              &InitialBnoSensorReportThreeDimensional,
		rotationVector:                  &InitialBnoSensorReportFourDimensional,
		geomagneticRotationVector:       &InitialBnoSensorReportFourDimensional,
		gameRotationVector:              &InitialBnoSensorReportFourDimensional,
		stepCount:                       &InitialBnoStepCount,
		shakesDetected:                  &InitialBnoShakeDetected,
		stabilityClassification:         &InitialBnoStabilityClassification,
		mostLikelyClassification:        &InitialBnoMostLikelyClassification,
		classifications:                 &InitialBnoClassifications,
		rawAccelerometer:                &InitialBnoSensorReportThreeDimensional,
		rawGyroscope:                    &InitialBnoSensorReportThreeDimensional,
		rawMagnetometer:                 &InitialBnoSensorReportThreeDimensional,
		enabledFeatures:                 make(map[uint8]bool),
		afterResetFn:                    afterResetFn,
	}

	// Perform initialization
	if err := bno08x.Initialize(); err != nil {
		return nil, fmt.Errorf("failed to initialize bno08x: %w", err)
	}
	return bno08x, nil
}

// HardwareReset performs a hardware reset of the BNO08X sensor using the specified reset pin.
func (b *BNO08X) HardwareReset() {
	HardwareReset(b.resetPin, b.debugger)
}

// SoftwareReset performs a software reset of the BNO08X sensor to an initial unconfigured state.
//
// Returns:
//
// An error if the reset process fails, otherwise nil.
func (b *BNO08X) SoftwareReset() error {
	if b.debugger != nil {
		b.debugger.Debug("Software resetting...")
	}

	// Resets the sequence numbers in the data buffer
	b.dataBuffer.ResetSequenceNumbers()

	// Clear the read ID status
	b.idRead = false

	// Reset enabled features
	b.enabledFeatures = make(map[uint8]bool)

	// Clear calibration status
	b.calibrationComplete = false

	// Send the reset command
	if _, err := b.packetWriter.SendPacket(ChannelExe, &[]byte{CommandReset}); err != nil {
		return fmt.Errorf("error sending reset command: %w", err)
	}

	// Clear out any packets that may have been sent during the reset process
	time.Sleep(ResetPacketDelay)

	// Clear out any pending packets
	startTime := time.Now()
	for time.Since(startTime) < MaxClearPendingPacketsTimeout {
		packet, err := b.waitForPacket(WaitForPacketTimeout)
		if err != nil {
			break // No more packets
		}

		// Log what we're clearing
		if b.debugger != nil {
			if packet.ChannelNumber() == ChannelSHTPCommand && len(packet.Data) == AdvertisementPacketLength {
				b.debugger.Debug("Found SHTP advertisement packet")
			} else {
				b.debugger.Debug(
					fmt.Sprintf(
						"Clearing packet from channel %d with %d bytes",
						packet.ChannelNumber(),
						len(packet.Data),
					),
				)
			}
		}
	}

	// Call after reset function if provided
	if b.afterResetFn != nil {
		if err := b.afterResetFn(b); err != nil {
			return err
		}
	}

	// Wait for the reset to complete
	if b.debugger != nil {
		b.debugger.Debug("OK!")
	}
	return nil
}

// Reset performs a hardware reset and then a software reset of the BNO08X sensor to an initial unconfigured state.
//
// Returns:
//
// An error if the reset process fails, otherwise nil.
func (b *BNO08X) Reset() error {
	// Perform hardware reset
	b.HardwareReset()

	// Perform software reset
	return b.SoftwareReset()
}

// Initialize performs the initial setup of the BNO08X sensor, including hardware and software resets.
//
// Returns:
//
// An error if the initialization fails, otherwise nil.
func (b *BNO08X) Initialize() error {
	// Log initialization start
	if b.debugger != nil {
		b.debugger.Debug("Initializing BNO08X sensor...")
	}

	// Try up to 3 times to initialize the sensor
	for i := 0; i < InitializeAttempts; i++ {
		// Reset
		if err := b.Reset(); err != nil {
			return err
		}

		// Check if the sensor ID can be read
		ok, err := b.checkID()
		if err != nil {
			time.Sleep(CheckIDDelay)
		}
		if ok {
			return nil
		}
	}
	return ErrFailedToReadSensorID
}

// checkID checks if the sensor ID can be read from the BNO08X sensor.
//
// Returns:
//
// A boolean indicating whether the sensor ID was successfully read, and an error if there was an issue during the process.
func (b *BNO08X) checkID() (bool, error) {
	if b.debugger != nil {
		b.debugger.Debug("********** READ ID **********")
	}
	if b.idRead {
		return true, nil
	}

	// Send the ID request report
	if b.debugger != nil {
		b.debugger.Debug("** Sending ID Request Report **")
	}
	if _, err := b.packetWriter.SendPacket(
		ChannelControl,
		&ReportIDProductIDRequestData,
	); err != nil {
		return false, fmt.Errorf("error sending id request packet: %w", err)
	}

	// Wait for the ID response report
	reportID := ReportIDProductIDResponse
	packet, err := b.waitForPacketType(
		ChannelControl,
		&reportID,
	)
	if err != nil {
		return false, fmt.Errorf("error waiting for id response packet: %w", err)
	}

	// Read the Packet data into the data buffer
	sensorIDReport, err := newReportFromPacket(packet)
	if err != nil {
		return false, fmt.Errorf("error creating sensor id report from packet data: %w", err)
	}

	// Parse the sensor ID from the report
	sensorID, err := newSensorID(sensorIDReport)
	if err != nil {
		return false, fmt.Errorf("error parsing sensor id: %w", err)
	}

	// Log the sensor ID details
	if b.debugger != nil {
		var builder strings.Builder
		builder.WriteString("** Sensor ID Report **")
		builder.WriteString(
			fmt.Sprintf(
				"\n\t *** Part Number: %d",
				sensorID.SoftwarePartNumber,
			),
		)
		builder.WriteString(
			fmt.Sprintf(
				"\n\t *** Software Version: %d.%d.%d",
				sensorID.SoftwareMajorVersion,
				sensorID.SoftwareMinorVersion,
				sensorID.SoftwarePatchVersion,
			),
		)
		builder.WriteString(
			fmt.Sprintf(
				" Build: %d",
				sensorID.SoftwareBuildNumber,
			),
		)
		b.debugger.Debug(builder.String())
	}

	b.idRead = true
	return true, nil
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
) (*Packet, error) {
	startTime := time.Now()

	// Debug message
	if b.debugger != nil {
		if reportID == nil {
			b.debugger.Debug(
				fmt.Sprintf(
					"** Waiting for Packet on Channel %d **",
					channelNumber,
				),
			)
		} else {
			b.debugger.Debug(
				fmt.Sprintf(
					"** Waiting for Packet with Report ID 0x%02X on Channel %d **",
					*reportID,
					channelNumber,
					
				),
			)
		}
	}

	// Loop until timeout
	for time.Since(startTime) < WaitForPacketTypeTimeout {
		// Check if data is ready to be read
		newPacket, err := b.waitForPacket(WaitForPacketTypeTimeout - time.Since(startTime))
		if err != nil {
			continue
		}

		// If the packet is on the desired channel, check the report ID if provided
		if newPacket.ChannelNumber() == channelNumber {
			if reportID == nil {
				return newPacket, nil
			}

			// Get the report ID of the new packet
			newPacketReportID, err := newPacket.ReportID()
			if err != nil {
				return nil, err
			}

			// If the report ID matches, return the packet
			if newPacketReportID == *reportID {
				return newPacket, nil
			}
		}

		if newPacket.ChannelNumber() != ChannelExe && newPacket.ChannelNumber() != ChannelSHTPCommand {
			if b.debugger != nil {
				b.debugger.Debug("Passing Packet to handler for de-slicing")
			}
			if err = b.handlePacket(newPacket); err != nil {
				return nil, err
			}
		}
	}
	return nil, fmt.Errorf(
		"timed out waiting for a packet on channel %d",
		channelNumber,
	)
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
func (b *BNO08X) waitForPacket(timeout time.Duration) (*Packet, error) {
	startTime := time.Now()
	for time.Since(startTime) < timeout {
		// Check if data is ready to be read
		if !b.packetReader.IsDataReady() {
			time.Sleep(PacketReadyCheckDelay)
			continue
		}

		// Read the Packet from the Packet reader
		newPacket, err := b.packetReader.ReadPacket()
		if err != nil {
			if b.debugger != nil {
				b.debugger.Debug(
					fmt.Sprintf(
						"An error occurred when reading a packet while waiting for a packet: %v",
						err,
					),
				)
			}
			continue
		}
		return newPacket, nil
	}
	return nil, ErrPacketTimeout
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
func (b *BNO08X) handlePacket(packet *Packet) error {
	// Check if the packet is nil
	if packet == nil {
		return ErrNilPacket
	}

	// Check if the packet header is nil
	if packet.Header == nil {
		return ErrNilPacketHeader
	}

	// Check packet data length
	if len(packet.Data) != int(packet.Header.DataLength) {
		return fmt.Errorf(
			ErrMismatchedPacketDataLength,
			packet.Header.DataLength,
			len(packet.Data),
		)
	}

	// Ensure the Packet has a valid header
	idx := 0
	for idx < packet.Header.DataLength {
		// Check if there are enough bytes left in the Packet to read the report ID
		reportID := packet.Data[idx]
		requiredBytes := reportLength(reportID)
		unprocessedByteCount := packet.Header.DataLength - idx

		// If there are not enough bytes left, return an error
		if unprocessedByteCount < requiredBytes {
			return fmt.Errorf(
				ErrUnprocessableBatchBytes,
				reportID,
				unprocessedByteCount,
				requiredBytes,
			)
		}

		// Create a new report from the Packet data
		reportBytes := packet.Data[idx : idx+requiredBytes]
		report, err := newReport(reportID, &reportBytes)
		if err != nil {
			return fmt.Errorf(
				"failed to create report from bytes: %w",
				err,
			)
		}

		// Process the report
		if err := b.processReport(report); err != nil {
			if b.debugger != nil {
				b.debugger.Debug(
					fmt.Sprintf(
						"Error processing report: %v",
						err,
					),
				)
			}
			return err
		}

		// Move to the next report in the Packet
		idx += requiredBytes
	}
	return nil
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
func (b *BNO08X) processReport(report *report) error {
	// Check if the report is nil
	if report == nil {
		return ErrNilReport
	}

	// Check if it's a control report
	if isControlReport(report.ID) {
		return b.processControlReport(report)
	}

	// Check if the feature that was reported is enabled
	if enabled, ok := b.enabledFeatures[report.ID]; !ok || !enabled {
		b.enabledFeatures[report.ID] = true
	}

	if b.debugger != nil {
		var builder strings.Builder
		builder.WriteString(
			fmt.Sprintf(
				"Processing report: %s (0x%02X)",
				SHTPCommandsNames[report.ID],
				report.ID,
			),
		)

		// Log the report data in hex format
		for idx, packetByte := range report.Data {
			packetIndex := idx
			if (packetIndex % 4) == 0 {
				builder.WriteString(
					fmt.Sprintf(
						"\n\t\t [0x%02X] ",
						packetIndex,
					),
				)
			}
			builder.WriteString(fmt.Sprintf("0x%02X ", packetByte))
		}
		b.debugger.Debug(builder.String())
	}

	// Process the sensor report based on its ID+
	switch report.ID {
	case ReportIDStepCounter:
		// Parse the step counter report
		stepCounterReport, err := newStepCounterReport(report)
		if err != nil {
			return fmt.Errorf("failed to parse step counter report: %w", err)
		}

		// Update the step count in the BNO08X instance
		b.stepCount = &stepCounterReport.Count
		return nil
	case ReportIDShakeDetector:
		// Parse the shake detector report
		shakeReport, err := newShakeReport(report)
		if err != nil {
			return fmt.Errorf("failed to parse shake report: %w", err)
		}

		// Update the shake detection status in the BNO08X instance
		b.shakesDetected = &shakeReport.AreShakesDetected
		return nil
	case ReportIDStabilityClassifier:
		// Parse the stability classifier report
		stabilityReport, err := newStabilityClassifierReport(report)
		if err != nil {
			return fmt.Errorf(
				"failed to parse stability classifier report: %w",
				err,
			)
		}

		// Update the stability classification in the BNO08X instance
		b.stabilityClassification = &stabilityReport.StabilityClassification
		return nil
	case ReportIDActivityClassifier:
		// Parse the activity classifier report
		activityReport, err := newActivityClassifierReport(report)
		if err != nil {
			return fmt.Errorf(
				"failed to parse activity classifier report: %w",
				err,
			)
		}

		// Update the activity classification and classifications in the BNO08X instance
		b.classifications = &activityReport.Classifications
		return nil
	case ReportIDMagnetometer:
		// Parse the magnetometer report
		magnetometerReport, err := newThreeDimensionalReport(report)
		if err != nil {
			return fmt.Errorf("failed to parse magnetometer report: %w", err)
		}

		// Update the magnetometer readings in the BNO08X instance
		b.magnetometerAccuracy = magnetometerReport.Accuracy
		b.magnetometer = &magnetometerReport.Results
	case ReportIDRotationVector:
		// Parse the rotation vector report
		rotationReport, err := newFourDimensionalReport(report)
		if err != nil {
			return fmt.Errorf("failed to parse rotation vector report: %w", err)
		}

		// Update the rotation vector readings in the BNO08X instance
		b.rotationVector = &rotationReport.Results
	case ReportIDGeomagneticRotationVector:
		// Parse the geomagnetic rotation vector report
		geomagneticReport, err := newFourDimensionalReport(report)
		if err != nil {
			return fmt.Errorf(
				"failed to parse geomagnetic rotation vector report: %w",
				err,
			)
		}

		// Update the geomagnetic rotation vector readings in the BNO08X instance
		b.geomagneticRotationVector = &geomagneticReport.Results
	case ReportIDGameRotationVector:
		// Parse the game rotation vector report
		gameReport, err := newFourDimensionalReport(report)
		if err != nil {
			return fmt.Errorf(
				"failed to parse game rotation vector report: %w",
				err,
			)
		}

		// Update the game rotation vector readings in the BNO08X instance
		b.gameRotationVector = &gameReport.Results
	case ReportIDAccelerometer:
		// Parse the accelerometer report
		accelerometerReport, err := newThreeDimensionalReport(report)
		if err != nil {
			return fmt.Errorf("failed to parse accelerometer report: %w", err)
		}

		// Update the accelerometer readings in the BNO08X instance
		b.accelerometer = &accelerometerReport.Results
	case ReportIDLinearAcceleration:
		// Parse the linear acceleration report
		linearAccelerationReport, err := newThreeDimensionalReport(report)
		if err != nil {
			return fmt.Errorf(
				"failed to parse linear acceleration report: %w",
				err,
			)
		}

		// Update the linear acceleration readings in the BNO08X instance
		b.linearAcceleration = &linearAccelerationReport.Results
	case ReportIDGravity:
		// Parse the gravity report
		gravityReport, err := newThreeDimensionalReport(report)
		if err != nil {
			return fmt.Errorf("failed to parse gravity report: %w", err)
		}

		// Update the gravity readings in the BNO08X instance
		b.gravity = &gravityReport.Results
	case ReportIDGyroscope:
		// Parse the gyroscope report
		gyroscopeReport, err := newThreeDimensionalReport(report)
		if err != nil {
			return fmt.Errorf("failed to parse gyroscope report: %w", err)
		}

		// Update the gyroscope readings in the BNO08X instance
		b.gyroscope = &gyroscopeReport.Results
	case ReportIDRawAccelerometer:
		// Parse the raw accelerometer report
		rawAccelerometerReport, err := newThreeDimensionalReport(report)
		if err != nil {
			return fmt.Errorf(
				"failed to parse raw accelerometer report: %w",
				err,
			)
		}

		// Update the raw accelerometer readings in the BNO08X instance
		b.rawAccelerometer = &rawAccelerometerReport.Results
	case ReportIDRawGyroscope:
		// Parse the raw gyroscope report
		rawGyroscopeReport, err := newThreeDimensionalReport(report)
		if err != nil {
			return fmt.Errorf("failed to parse raw gyroscope report: %w", err)
		}

		// Update the raw gyroscope readings in the BNO08X instance
		b.rawGyroscope = &rawGyroscopeReport.Results
	case ReportIDRawMagnetometer:
		// Parse the raw magnetometer report
		rawMagnetometerReport, err := newThreeDimensionalReport(report)
		if err != nil {
			return fmt.Errorf(
				"failed to parse raw magnetometer report: %w",
				err,
			)
		}

		// Update the raw magnetometer readings in the BNO08X instance
		b.rawMagnetometer = &rawMagnetometerReport.Results
	}

	// If we reach here, the report was processed successfully
	return nil
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
func (b *BNO08X) processControlReport(report *report) error {
	// Check if the report is nil
	if report == nil {
		return ErrNilReport
	}

	// Handle the control report based on its ID
	switch report.ID {
	case ReportIDProductIDResponse:
		// Parse the sensor ID from the report bytes
		sensorID, err := newSensorID(report)
		if err != nil {
			return fmt.Errorf("failed to parse sensor ID: %w", err)
		}

		if b.debugger != nil {
			var builder strings.Builder
			builder.WriteString("FROM PACKET SLICE:")
			builder.WriteString(
				fmt.Sprintf(
					"\n\t *** Part Number: %d",
					sensorID.SoftwarePartNumber,
				),
			)
			builder.WriteString(
				fmt.Sprintf(
					"\n\t *** Software Version: %d.%d.%d",
					sensorID.SoftwareMajorVersion,
					sensorID.SoftwareMinorVersion,
					sensorID.SoftwarePatchVersion,
				),
			)
			builder.WriteString(
				fmt.Sprintf(
					" Build: %d",
					sensorID.SoftwareBuildNumber,
				),
			)
			b.debugger.Debug(builder.String())
		}
	case ReportIDGetFeatureResponse:
		// Parse the Get Feature report from the report bytes
		getFeatureReport, err := newGetFeatureReport(report)
		if err != nil {
			return fmt.Errorf("failed to parse get feature report: %w", err)
		}

		// Set the feature as enabled
		b.enabledFeatures[getFeatureReport.FeatureReportID] = true
	case ReportIDCommandResponse:
		// Parse the command response from the report bytes
		commandResponse, err := newCommandResponse(report)
		if err != nil {
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
				return ErrFailedToSaveCalibrationData
			}

			// Record the time when dynamic configuration data was saved
			b.dynamicConfigurationDataSavedAt = time.Now()
		}
		return nil
	}
	return nil
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
		if err != nil {
			if b.debugger != nil {
				b.debugger.Debug(
					fmt.Sprintf(
						"Error reading Packet: %v",
						err,
					),
				)
			}
			continue
		}

		// Pass the packet to the handler
		if err = b.handlePacket(newPacket); err != nil {
			if b.debugger != nil {
				b.debugger.Debug(fmt.Sprintf("Error handling Packet: %v", err))
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
func (b *BNO08X) GetMagnetic() *[3]float64 {
	return b.magnetometer
}

// GetQuaternion returns a pointer to a [4]float64 array representing the current rotation vector as a quaternion.
//
// Returns:
//
// A pointer to a [4]float64 array containing the quaternion values.
func (b *BNO08X) GetQuaternion() *[4]float64 {
	return b.rotationVector
}

// GetEulerDegrees returns the current rotation vector as Euler angles in degrees.
//
// Returns:
//
// A tuple of three float64 values representing the roll, pitch, and yaw angles in degrees.
func (b *BNO08X) GetEulerDegrees() *[3]float64 {
	// Get the quaternion readings
	b.GetQuaternion()

	// If rotation vector is nil, return nil
	if b.rotationVector == nil {
		return nil
	}

	// Convert quaternion to Euler angles in degrees
	eulerDegrees, _ := QuaternionToEulerDegrees(b.rotationVector)
	return eulerDegrees
}

// GetGeomagneticQuaternion returns a pointer to a [4]float64 array representing the current geomagnetic rotation vector as a quaternion.
//
// Returns:
//
// A pointer to a [4]float64 array containing the geomagnetic quaternion values.
func (b *BNO08X) GetGeomagneticQuaternion() *[4]float64 {
	return b.geomagneticRotationVector
}

// GetGameQuaternion returns a pointer to a [4]float64 array representing the current rotation vector expressed as a quaternion with no specific reference for heading.
//
// Returns:
//
// A pointer to a [4]float64 array containing the game quaternion values.
func (b *BNO08X) GetGameQuaternion() *[4]float64 {
	return b.gameRotationVector
}

// GetSteps returns the number of steps detected since the sensor was initialized.
//
// Returns:
//
//	A pointer to an uint16 representing the step count.
func (b *BNO08X) GetSteps() *uint16 {
	return b.stepCount
}

// GetLinearAcceleration returns the current linear acceleration values on the X, Y, and Z axes in meters per second squared.
//
// Returns:
//
//	A pointer to a [3]float64 array containing the linear acceleration values.
func (b *BNO08X) GetLinearAcceleration() *[3]float64 {
	return b.linearAcceleration
}

// GetAcceleration returns the acceleration measurements on the X, Y, and Z axes in meters per second squared.
//
// Returns:
//
//	A pointer to a [3]float64 array containing the acceleration values.
func (b *BNO08X) GetAcceleration() *[3]float64 {
	return b.accelerometer
}

// GetGravity returns the gravity vector in the X, Y, and Z components in meters per second squared.
//
// Returns:
//
//	A pointer to a [3]float64 array containing the gravity vector.
func (b *BNO08X) GetGravity() *[3]float64 {
	return b.gravity
}

// GetGyro returns Gyro's rotation measurements on the X, Y, and Z axes in radians per second.
//
// Returns:
//
//	A pointer to a [3]float64 array containing the gyroscope values.
func (b *BNO08X) GetGyro() *[3]float64 {
	return b.gyroscope
}

// GetGyroDegrees returns Gyro's rotation measurements on the X, Y, and Z axes in degrees per second.
//
// Returns:
//
// A pointer to a [3]float64 array containing the gyroscope values in degrees.
func (b *BNO08X) GetGyroDegrees() *[3]float64 {
	// Get the gyroscope readings
	b.GetGyro()

	// If gyroscope is nil, return nil
	if b.gyroscope == nil {
		return nil
	}

	// Convert radians to degrees
	gyroDegrees := [3]float64{
		b.gyroscope[0] * (180.0 / math.Pi),
		b.gyroscope[1] * (180.0 / math.Pi),
		b.gyroscope[2] * (180.0 / math.Pi),
	}
	return &gyroDegrees
}

// GetShake returns true if a shake was detected on any axis since the last time it was checked.
// This method has a latching behavior: once a shake is detected, it stays "shaken" until read.
//
// Returns:
//
//	A pointer to a bool indicating if a shake was detected.
func (b *BNO08X) GetShake() *bool {
	// If shakesDetected is nil, return nil
	if b.shakesDetected == nil {
		return nil
	}

	// If a shake was detected, clear the flag on read
	if *b.shakesDetected {
		*b.shakesDetected = false
	}
	return b.shakesDetected
}

// GetStabilityClassification returns the sensor's assessment of its current stability.
//
// Returns:
//
//	A pointer to a string describing the stability classification.
func (b *BNO08X) GetStabilityClassification() *string {
	return b.stabilityClassification
}

// GetActivityClassification returns the sensor's assessment of the activity creating the sensed motions.
//
// Returns:
//
//	A pointer to a map[string]int representing activity classifications.
func (b *BNO08X) GetActivityClassification() *map[string]int {
	return b.classifications
}

// GetRawAcceleration returns the sensor's raw, unscaled value from the accelerometer registers.
//
// Returns:
//
//	A pointer to a [3]float64 array containing the raw accelerometer values.
func (b *BNO08X) GetRawAcceleration() *[3]float64 {
	return b.rawAccelerometer
}

// GetRawGyro returns the sensor's raw, unscaled value from the gyro registers.
//
// Returns:
//
//	A pointer to a [3]float64 array containing the raw gyroscope values.
func (b *BNO08X) GetRawGyro() *[3]float64 {
	return b.rawGyroscope
}

// GetRawMagnetic returns the sensor's raw, unscaled value from the magnetometer registers.
//
// Returns:
//
//	A pointer to a [3]float64 array containing the raw magnetometer values.
func (b *BNO08X) GetRawMagnetic() *[3]float64 {
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
func (b *BNO08X) EnableFeature(featureID uint8) error {
	if b.debugger != nil {
		b.debugger.Debug(
			fmt.Sprintf(
				"********** Enabling Feature ID: 0x%02X **********",
				featureID,
			),
		)
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
		if b.debugger != nil {
			b.debugger.Debug(
				fmt.Sprintf(
					"Enabling feature dependency: %s (0x%02X)",
					SHTPCommandsNames[featureDependency],
					featureDependency,
				),
			)
		}
		if err := b.EnableFeature(featureDependency); err != nil {
			return err
		}
	}

	// Send the feature enable report
	if b.debugger != nil {
		b.debugger.Debug(
			fmt.Sprintf(
				"Enabling feature: %s (0x%02X)",
				SHTPCommandsNames[featureID],
				featureID,
			),
		)
	}
	if _, err := b.packetWriter.SendPacket(
		ChannelControl,
		&setFeatureReport,
	); err != nil {
		return err
	}

	// Wait for the feature to be enabled
	startTime := time.Now()
	for time.Since(startTime) < FeatureEnableTimeout {
		b.Update()
		if b.IsFeatureEnabled(featureID) {
			return nil
		}
	}
	return fmt.Errorf(
		"was not able to enable feature %s (0x%0X)",
		SHTPCommandsNames[featureID],
		featureID,
	)
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
func (b *BNO08X) BeginCalibration() error {
	// Begin the sensor's self-calibration routine
	params := []byte{
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
	if err := b.sendMeCommand(&params); err != nil {
		return fmt.Errorf("error starting calibration: %w", err)
	}
	return nil
}

// CalibrationStatus retrieves the status of the self-calibration process.
//
// Returns:
//
// An integer representing the calibration status, where 0 indicates no calibration needed,
func (b *BNO08X) CalibrationStatus() ReportAccuracyStatus {
	// Get the status of the self-calibration
	params := []byte{
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
	b.sendMeCommand(&params)

	// Log the calibration status if debugger is enabled
	if b.debugger != nil {
		b.debugger.Debug(
			fmt.Sprintf(
				"Calibration Status: %s",
				ReportAccuracyStatusNames[b.magnetometerAccuracy],
			),
		)
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
func (b *BNO08X) sendMeCommand(subcommandParams *[]byte) error {
	// Check if the subcommandParams is nil
	if subcommandParams == nil {
		return ErrNilSubcommandParams
	}

	// Start the command request process
	startTime := time.Now()
	localBuffer := b.commandBuffer

	// Insert the command request report into the local buffer
	if err := insertCommandRequestReport(
		MagnetometerCalibration,
		&b.commandBuffer, // should use b.dataBuffer, but sendPacket doesn't
		b.dataBuffer.GetReportSequenceNumber(ReportIDCommandRequest),
		subcommandParams,
	); err != nil {
		return fmt.Errorf("error inserting command request report: %w", err)
	}

	// Send the command request Packet
	if _, err := b.packetWriter.SendPacket(ChannelControl, &localBuffer); err != nil {
		return fmt.Errorf("error sending me command request packet: %w", err)
	}
	b.dataBuffer.IncrementReportSequenceNumber(ReportIDCommandRequest)

	// Wait for the command response
	for time.Since(startTime) < CalibrationCommandsTimeout {
		b.Update()
		if b.meCalibrationStartedAt.After(startTime) {
			break
		}
	}
	return nil
}

// SaveCalibrationData saves the self-calibration data to the BNO08X sensor.
//
// Returns:
//
// An error if the calibration data could not be saved, otherwise nil.
func (b *BNO08X) SaveCalibrationData() error {
	// Save the self-calibration data
	startTime := time.Now()
	localBuffer := make([]byte, 12)
	err := insertCommandRequestReport(
		SaveDynamicCalibrationData,
		&localBuffer, // should use b.dataBuffer, but sendPacket doesn't
		b.dataBuffer.GetReportSequenceNumber(ReportIDCommandRequest),
		nil,
	)
	if err != nil {
		return err
	}

	// Send the command request Packet to save calibration data
	_, err = b.packetWriter.SendPacket(ChannelControl, &localBuffer)
	if err != nil {
		return err
	}
	b.dataBuffer.IncrementReportSequenceNumber(ReportIDCommandRequest)

	// Wait for the command response indicating that the calibration data was saved
	for time.Since(startTime) < CalibrationCommandsTimeout {
		b.Update()
		if b.dynamicConfigurationDataSavedAt.After(startTime) {
			return nil
		}
	}
	return ErrFailedToSaveCalibrationData
}
