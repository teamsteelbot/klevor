//go:build tinygo && (rp2040 || rp2350)

package tinygo_bno08x

import (
	"encoding/binary"

	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

type (
	// report represents a BNO08x report
	report struct {
		ID   uint8
		Data []byte
	}

	// sensorReport represents a report from the BNO08x sensor
	sensorReport struct {
		Scalar       float64
		Count        int
		ReportLength int
	}

	// sensorReportData represents a parsed sensor report with 16-bit fields
	sensorReportData struct {
		Count    int
		Results  []float64
		Accuracy ReportAccuracyStatus
	}

	// threeDimensionalReport represents a 3D sensor report
	threeDimensionalReport struct {
		Accuracy ReportAccuracyStatus
		Results  [3]float64
	}

	// FourDimensionalReport represents a 4D sensor report
	fourDimensionalReport struct {
		Accuracy ReportAccuracyStatus
		Results  [4]float64
	}

	// getFeatureReport represents the response report for a Get Feature request
	getFeatureReport struct {
		ReportID                 byte
		FeatureReportID          byte
		FeatureFlags             byte
		ChangeSensitivity        uint16
		ReportInterval           uint32
		BatchIntervalWord        uint32
		SensorSpecificConfigWord uint32
	}

	// shakeReport represents a shake report from the BNO08x device
	shakeReport struct {
		AreShakesDetected bool
	}

	// stepCounterReport represents a step counter report from the BNO08x device
	stepCounterReport struct {
		Count uint16
	}

	// stabilityClassifierReport represents a stability classification report from the BNO08x device
	stabilityClassifierReport struct {
		StabilityClassification ReportStabilityClassification
	}

	// sensorID represents the identification of a sensor
	sensorID struct {
		SoftwareMajorVersion uint8
		SoftwareMinorVersion uint8
		SoftwarePatchVersion uint16
		SoftwarePartNumber   uint32
		SoftwareBuildNumber  uint32
	}

	// commandResponse represents a command response from the BNO08x device
	commandResponse struct {
		SequenceNumber         byte
		Command                byte
		CommandSequenceNumber  byte
		ResponseSequenceNumber byte
		ResponseValues         []byte
	}

	// activityClassifierReport represents an activity classifier report from the BNO08x device
	activityClassifierReport struct {
		SequenceNumber           byte
		Status                   byte
		Delay                    byte
		PageNumber               byte
		MostLikely               byte
		MostLikelyClassification ReportClassification
		Classifications          [ReportClassificationsNumber]int
	}
)

//

// newReport creates a new report from the Packet data.
//
// Parameters:
//
//	id: The report ID as an uint8.
//	data: A byte slice containing the report data.
//
// Returns:
//
//	A report object containing the ID and data, or an error if the report length is invalid
func newReport(id uint8, data []byte) (*report, tinygotypes.ErrorCode) {
	// Check for nil data
	if data == nil {
		return nil, ErrorCodeBNO08XNilReportData
	}

	// Validate the report length
	expectedLength, err := ReportLength(id)
	if err != tinygotypes.ErrorCodeNil {
		return nil, ErrorCodeBNO08XFailedToGetExpectedReportLength
	}
	if expectedLength != len(data) {
		return nil, ErrorCodeBNO08XInvalidReportLength
	}

	return &report{
		ID:   id,
		Data: data,
	}, tinygotypes.ErrorCodeNil
}

// newReportFromPacket creates a new report from the provided Packet.
//
// Parameters:
//
//	Packet: A pointer to a Packet containing the report data.
//
// Returns:
//
// A pointer to the newly created report or an error if the Packet is nil
func newReportFromPacket(packet *Packet) (*report, tinygotypes.ErrorCode) {
	// Check if the provided Packet is nil
	if packet == nil {
		return nil, ErrorCodeBNO08XNilPacket
	}

	// Get the report ID from the Packet
	reportID, err := packet.ReportID()
	if err != tinygotypes.ErrorCodeNil {
		return nil, ErrorCodeBNO08XFailedToGetReportID
	}

	// Create a new report from the Packet data
	return newReport(reportID, packet.Data)
}

// newSensorReport creates a new sensorReport from the provided report bytes.
//
// Parameters:
//
//	scalar: The scalar value for the report
//	count: The count of the report
//	ReportLength: The length of the report in bytes
//
// Returns:
//
//	A pointer to the newly created sensorReport
func newSensorReport(scalar float64, count, ReportLength int) *sensorReport {
	return &sensorReport{
		Scalar:       scalar,
		Count:        count,
		ReportLength: ReportLength,
	}
}

// newSetFeatureEnableReportData creates a byte slice of the data to enable a feature on the BNO08X sensor.
//
// Parameters:
//
//	featureID: The ID of the feature to enable.
//	reportInterval: The interval for reporting (default: DefaultReportInterval).
//	sensorSpecificConfig: Sensor-specific configuration bits.
//
// Returns:
//
//	A byte slice representing the feature enable report data.
func newSetFeatureEnableReportData(
	featureID uint8,
	reportInterval uint32,
	sensorSpecificConfig uint32,
) []byte {
	setFeatureReport := make([]byte, 17)
	setFeatureReport[0] = ReportIDSetFeatureCommand
	setFeatureReport[1] = featureID
	binary.LittleEndian.PutUint32(setFeatureReport[5:], reportInterval)
	binary.LittleEndian.PutUint32(setFeatureReport[13:], sensorSpecificConfig)
	return setFeatureReport
}

// newGetFeatureReport creates a new getFeatureReport from the provided report.
//
// Parameters:
//
//	report: A pointer to a report containing the report bytes
//
// Returns:
//
//	A pointer to the newly created getFeatureReport, or an error if the report bytes are too short
func newGetFeatureReport(report *report) (
	*getFeatureReport,
	tinygotypes.ErrorCode,
) {
	// Check if the provided report is nil
	if report == nil {
		return nil, ErrorCodeBNO08XNilReport
	}

	// Check if the report ID is valid for a get feature report
	if report.ID != ReportIDGetFeatureResponse {
		return nil, ErrorCodeBNO08XInvalidReportIDToParseReport
	}

	// Validate the length of the report bytes
	if len(report.Data) != ReportGetFeatureResponseLength {
		return nil, ErrorCodeBNO08XInvalidReportLength
	}

	return &getFeatureReport{
		ReportID:                 report.Data[0],
		FeatureReportID:          report.Data[1],
		FeatureFlags:             report.Data[2],
		ChangeSensitivity:        binary.LittleEndian.Uint16(report.Data[3:5]),
		ReportInterval:           binary.LittleEndian.Uint32(report.Data[5:9]),
		BatchIntervalWord:        binary.LittleEndian.Uint32(report.Data[9:13]),
		SensorSpecificConfigWord: binary.LittleEndian.Uint32(report.Data[13:17]),
	}, tinygotypes.ErrorCodeNil
}

// newShakeReport creates a new shakeReport from the provided report.
//
// Parameters:
//
//	report: A pointer to a report containing the report bytes
//
// Returns:
//
//	A pointer to the newly created shakeReport or an error if the report bytes are too short
func newShakeReport(report *report) (*shakeReport, tinygotypes.ErrorCode) {
	// Check if the provided report is nil
	if report == nil {
		return nil, ErrorCodeBNO08XNilReport
	}

	// Check if the report ID is valid for a shake report
	if report.ID != ReportIDShakeDetector {
		return nil, ErrorCodeBNO08XInvalidReportIDToParseReport
	}

	// Validate the length of the report bytes
	if len(report.Data) < SensorReportShakeDetector.ReportLength {
		return nil, ErrorCodeBNO08XInvalidReportLength
	}

	return &shakeReport{
		AreShakesDetected: binary.LittleEndian.Uint16(report.Data[4:6])&0x111 > 0,
	}, tinygotypes.ErrorCodeNil
}

// newStepCounterReport creates a new stepCounterReport from the provided report.
//
// Parameters:
//
//	report: A pointer to a report containing the report bytes
//
// Returns:
//
//	A pointer to the newly created stepCounterReport or an error if the report bytes are too short
func newStepCounterReport(report *report) (*stepCounterReport, tinygotypes.ErrorCode) {
	// Check if the provided report is nil
	if report == nil {
		return nil, ErrorCodeBNO08XNilReport
	}

	// Check if the report ID is valid for a step counter report
	if report.ID != ReportIDStepCounter {
		return nil, ErrorCodeBNO08XInvalidReportIDToParseReport
	}

	// Validate the length of the report bytes
	if len(report.Data) != SensorReportStepCounter.ReportLength {
		return nil, ErrorCodeBNO08XInvalidReportLength
	}

	return &stepCounterReport{
		Count: binary.LittleEndian.Uint16(report.Data[8:10]),
	}, tinygotypes.ErrorCodeNil
}

// newStabilityClassifierReport creates a new stabilityClassifierReport from the provided report.
//
// Parameters:
//
//	report: A pointer to a report containing the report bytes
//
// Returns:
//
//	A pointer to the newly created stabilityClassifierReport or an error if the report bytes are too short
func newStabilityClassifierReport(report *report) (
	*stabilityClassifierReport,
	tinygotypes.ErrorCode,
) {
	// Check if the provided report is nil
	if report == nil {
		return nil, ErrorCodeBNO08XNilReport
	}

	// Check if the report ID is valid for a stability classifier report
	if report.ID != ReportIDStabilityClassifier {
		return nil, ErrorCodeBNO08XInvalidReportIDToParseReport
	}

	// Validate the length of the report bytes
	if len(report.Data) != SensorReportStabilityClassifier.ReportLength {
		return nil, ErrorCodeBNO08XInvalidReportLength
	}

	// Check if the classification bitfield is within the valid range
	classificationBitfield := report.Data[4]
	stabilityClassification, err := ReportStabilityClassificationFromUint8(classificationBitfield)
	if err != tinygotypes.ErrorCodeNil {
		return nil, err
	}

	return &stabilityClassifierReport{
		StabilityClassification: stabilityClassification,
	}, tinygotypes.ErrorCodeNil
}

// newSensorID parses the sensor ID from the provided report.
//
// Parameters:
//
//	report: A pointer to a report containing the report bytes
//
// Returns:
//
//	A pointer to the newly created sensorID or an error if the buffer is too short
func newSensorID(report *report) (*sensorID, tinygotypes.ErrorCode) {
	// Check if the provided report is nil
	if report == nil {
		return nil, ErrorCodeBNO08XNilReport
	}

	// Check if the report ID is valid for a SHTP report product ID response
	if report.ID != ReportIDProductIDResponse {
		return nil, ErrorCodeBNO08XInvalidReportIDToParseReport
	}

	// Validate the length of the buffer
	if len(report.Data) != ReportProductIDResponseLength {
		return nil, ErrorCodeBNO08XInvalidReportLength
	}

	return &sensorID{
		SoftwareMajorVersion: report.Data[2],
		SoftwareMinorVersion: report.Data[3],
		SoftwarePatchVersion: binary.LittleEndian.Uint16(report.Data[12:14]),
		SoftwarePartNumber:   binary.LittleEndian.Uint32(report.Data[4:8]),
		SoftwareBuildNumber:  binary.LittleEndian.Uint32(report.Data[8:12]),
	}, tinygotypes.ErrorCodeNil
}

// PrintBuffer returns a byte slice representation of the sensorID for debugging purposes.
//
// Returns:
//
// A byte slice representing the sensorID
func (s *sensorID) PrintBuffer() []byte {
	// Preallocate a byte slice with the appropriate length
	buffer := make([]byte, 0, 100)

	// Append the sensor ID details to the buffer
	buffer = append(buffer, "Sensor ID Report"...)
	buffer = append(buffer, "\n\t Part Number: "...)
	buffer = append(buffer, uint32ToString(s.SoftwarePartNumber)...)
	buffer = append(buffer, "\n\t Version: "...)
	buffer = append(buffer, uint8ToString(s.SoftwareMajorVersion)...)
	buffer = append(buffer, "."...)
	buffer = append(buffer, uint8ToString(s.SoftwareMinorVersion)...)
	buffer = append(buffer, "."...)
	buffer = append(buffer, uint16ToString(s.SoftwarePatchVersion)...)
	buffer = append(buffer, "\n\t Build: "...)
	buffer = append(buffer, uint32ToString(s.SoftwareBuildNumber)...)
	return buffer
}

// newCommandResponse creates a new commandResponse from the provided report.
//
// Parameters:
//
//	report: A pointer to a report containing the report bytes
//
// Returns:
//
//	A pointer to the newly created commandResponse or an error if the report bytes are too short
func newCommandResponse(report *report) (*commandResponse, tinygotypes.ErrorCode) {
	// Check if the provided report is nil
	if report == nil {
		return nil, ErrorCodeBNO08XNilReport
	}

	// Check if the report ID is valid for a command response
	if report.ID != ReportIDCommandResponse {
		return nil, ErrorCodeBNO08XInvalidReportIDToParseReport
	}

	// Validate the length of the report bytes
	if len(report.Data) != ReportCommandResponseLength {
		return nil, ErrorCodeBNO08XInvalidReportLength
	}

	return &commandResponse{
		SequenceNumber:         report.Data[1],
		Command:                report.Data[2],
		CommandSequenceNumber:  report.Data[3],
		ResponseSequenceNumber: report.Data[4],
		ResponseValues:         report.Data[5:16],
	}, tinygotypes.ErrorCodeNil
}

// Status is the status of the command response.
//
// Returns:
//
// The status of the command response as a byte
func (cr *commandResponse) Status() byte {
	if cr == nil || len(cr.ResponseValues) < 1 {
		return 0
	}
	return cr.ResponseValues[0]
}

// newActivityClassifierReport creates a new activityClassifierReport from the provided report.
//
// Parameters:
//
//	report: A pointer to a report containing the report bytes
//
// Returns:
//
//	A pointer to the newly created activityClassifierReport or an error if the report bytes are too short
func newActivityClassifierReport(report *report) (
	*activityClassifierReport,
	tinygotypes.ErrorCode,
) {
	// Check if the provided report is nil
	if report == nil {
		return nil, ErrorCodeBNO08XNilReport
	}

	// Check if the report ID is valid for an activity classifier report
	if report.ID != ReportIDActivityClassifier {
		return nil, ErrorCodeBNO08XInvalidReportIDToParseReport
	}

	// Validate the length of the report bytes
	if len(report.Data) != SensorReportActivityClassifier.ReportLength {
		return nil, ErrorCodeBNO08XInvalidReportLength
	}

	mostLikely := report.Data[5]
	pageNumber := report.Data[4] & 0x7F
	confidences := report.Data[6:15]

	// Create a map to hold the classifications with their confidence levels
	classifications := [ReportClassificationsNumber]int{}
	for idx, rawConfidence := range confidences {
		confidence := int(10*pageNumber) + int(rawConfidence)
		classification, err := ReportActivityFromUint8(uint8(idx))
		if err != tinygotypes.ErrorCodeNil {
			return nil, err
		}
		classifications[classification] = confidence
	}

	return &activityClassifierReport{
		SequenceNumber:           report.Data[1],
		Status:                   report.Data[2],
		Delay:                    report.Data[3],
		PageNumber:               pageNumber,
		MostLikely:               mostLikely,
		MostLikelyClassification: ReportClassificationUnknown,
		Classifications:          classifications,
	}, tinygotypes.ErrorCodeNil
}

// newSensorReportData parses sensor reports with only 16-bit fields.
//
// Parameters:
//
//	report: A pointer to a report containing the report bytes
//
// Returns:
//
//	A pointer to the newly created sensorReportData or an error if the report bytes are too short
func newSensorReportData(report *report) (*sensorReportData, tinygotypes.ErrorCode) {
	// Check if the provided report is nil
	if report == nil {
		return nil, ErrorCodeBNO08XNilReport
	}

	// The data offset is assumed to be 4 bytes for sensor reports
	dataOffset := 4 // may not always be true

	// Validate the length of the report bytes
	if len(report.Data) < dataOffset {
		return nil, ErrorCodeBNO08XSensorReportDataTooShort
	}

	// Get the sensor report for the given report ID
	sensorReport, err := SensorReportFromReportID(report.ID)
	if err != tinygotypes.ErrorCodeNil {
		return nil, err
	}	
	if sensorReport == nil {
		return nil, ErrorCodeBNO08XNilSensorReport
	}
	scalar := sensorReport.Scalar
	count := sensorReport.Count

	// Check if it's signed or unsigned data
	formatUnsigned := false
	if _, ok := RawReports[report.ID]; ok {
		formatUnsigned = true
	}

	// Get the accuracy and results from the report bytes
	accuracy, err := ReportAccuracyStatusFromUint8((report.Data)[2] & 0b11)
	if err != tinygotypes.ErrorCodeNil {
		return nil, err
	}
	results := make([]float64, 0, count)

	for offsetIdx := 0; offsetIdx < count; offsetIdx++ {
		// Calculate the total offset for the current data point
		totalOffset := dataOffset + (offsetIdx * 2)
		if totalOffset+2 > len(report.Data) {
			return nil, ErrorCodeBNO08XSensorReportDataTooShort
		}

		// Read the raw data from the report bytes
		var rawData float64
		if formatUnsigned {
			rawData = float64(binary.LittleEndian.Uint16(report.Data[totalOffset : totalOffset+2]))
		} else {
			rawData = float64(int16(binary.LittleEndian.Uint16(report.Data[totalOffset : totalOffset+2])))
		}
		scaledData := rawData * scalar
		results = append(results, scaledData)
	}

	return &sensorReportData{
		Count:    count,
		Results:  results,
		Accuracy: accuracy,
	}, tinygotypes.ErrorCodeNil
}

// newThreeDimensionalReport creates a new threeDimensionalReport from the provided report.
//
// Parameters:
//
//	report: A pointer to a report containing the report bytes
//
// Returns:
//
//	A pointer to the newly created threeDimensionalReport or an error if the report bytes are too short
func newThreeDimensionalReport(
	report *report,
) (*threeDimensionalReport, tinygotypes.ErrorCode) {
	// Initialize the sensorReportData
	sensorReportData, err := newSensorReportData(report)
	if err != tinygotypes.ErrorCodeNil {
		return nil, err
	}

	// Ensure the report has exactly 3 results for three-dimensional parsing
	if sensorReportData.Count != 3 {
		return nil, ErrorCodeBNO08XInvalidReportIDForThreeDimensionalParsing
	}

	return &threeDimensionalReport{
		Accuracy: sensorReportData.Accuracy,
		Results: [3]float64{
			sensorReportData.Results[0],
			sensorReportData.Results[1],
			sensorReportData.Results[2],
		},
	}, tinygotypes.ErrorCodeNil
}

// newFourDimensionalReport creates a new fourDimensionalReport from the provided report.
//
// Parameters:
//
//	report: A pointer to a report containing the report bytes
//
// Returns
//
//	A pointer to the newly created fourDimensionalReport or an error if the report bytes are too short
func newFourDimensionalReport(
	report *report,
) (*fourDimensionalReport, tinygotypes.ErrorCode) {
	// Initialize the sensorReportData
	sensorReportData, err := newSensorReportData(report)
	if err != tinygotypes.ErrorCodeNil {
		return nil, err
	}

	// Ensure the report has exactly 4 results for four-dimensional parsing
	if sensorReportData.Count != 4 {
		return nil, ErrorCodeBNO08XInvalidReportIDForFourDimensionalParsing
	}

	return &fourDimensionalReport{
		Accuracy: sensorReportData.Accuracy,
		Results: [4]float64{
			sensorReportData.Results[0],
			sensorReportData.Results[1],
			sensorReportData.Results[2],
			sensorReportData.Results[3],
		},
	}, tinygotypes.ErrorCodeNil
}

// SensorReportFromReportID returns the sensorReport based on the report ID.
//
// Parameters:
//
//	reportID: The ID of the report
//
// Returns:
//
//	The sensorReport corresponding to the report ID, or an error if the report ID is unknown
func SensorReportFromReportID(reportID uint8) (*sensorReport, tinygotypes.ErrorCode) {
	switch reportID {
	case ReportIDAccelerometer:
		return SensorReportAccelerometer, tinygotypes.ErrorCodeNil
	case ReportIDGravity:
		return SensorReportGravity, tinygotypes.ErrorCodeNil
	case ReportIDGyroscope:
		return SensorReportGyroscope, tinygotypes.ErrorCodeNil
	case ReportIDMagnetometer:
		return SensorReportMagnetometer, tinygotypes.ErrorCodeNil
	case ReportIDLinearAcceleration:
		return SensorReportLinearAcceleration, tinygotypes.ErrorCodeNil
	case ReportIDRotationVector:
		return SensorReportRotationVector, tinygotypes.ErrorCodeNil
	case ReportIDGeomagneticRotationVector:
		return SensorReportGeomagneticRotationVector, tinygotypes.ErrorCodeNil
	case ReportIDGameRotationVector:
		return SensorReportGameRotationVector, tinygotypes.ErrorCodeNil
	case ReportIDStepCounter:
		return SensorReportStepCounter, tinygotypes.ErrorCodeNil
	case ReportIDShakeDetector:
		return SensorReportShakeDetector, tinygotypes.ErrorCodeNil
	case ReportIDStabilityClassifier:
		return SensorReportStabilityClassifier, tinygotypes.ErrorCodeNil
	case ReportIDActivityClassifier:
		return SensorReportActivityClassifier, tinygotypes.ErrorCodeNil
	case ReportIDRawAccelerometer:
		return SensorReportRawAccelerometer, tinygotypes.ErrorCodeNil
	case ReportIDRawGyroscope:
		return SensorReportRawGyroscope, tinygotypes.ErrorCodeNil
	case ReportIDRawMagnetometer:
		return SensorReportRawMagnetometer, tinygotypes.ErrorCodeNil
	default:
		return nil, ErrorCodeBNO08XUnknownReportID
	}
}

// ReportLength returns the length of the report based on the report ID.
//
// Parameters:
//
//	reportID: The ID of the report
//
// Returns:
//
//	The length of the report in bytes, or an error if the report ID is unknown
func ReportLength(reportID uint8) (int, tinygotypes.ErrorCode) {
	if reportID < 0xF0 {
		sensorReport, err := SensorReportFromReportID(reportID)
		if err != tinygotypes.ErrorCodeNil {
			return 0, err
		}
		if sensorReport == nil {
			return 0, ErrorCodeBNO08XNilSensorReport
		}
		return sensorReport.ReportLength, tinygotypes.ErrorCodeNil
	}

	switch reportID {
	case ReportIDProductIDResponse:
		return ReportProductIDResponseLength, tinygotypes.ErrorCodeNil
	case ReportIDGetFeatureResponse:
		return ReportGetFeatureResponseLength, tinygotypes.ErrorCodeNil
	case ReportIDCommandResponse:
		return ReportCommandResponseLength, tinygotypes.ErrorCodeNil
	case ReportIDBaseTimestamp:
		return ReportBaseTimestampLength, tinygotypes.ErrorCodeNil
	case ReportIDTimestampRebase:
		return ReportTimestampRebaseLength, tinygotypes.ErrorCodeNil
	default:
		return 0, ErrorCodeBNO08XUnknownReportID
	}
}

// insertCommandRequestReport inserts a command request report into the provided buffer.
//
// Parameters:
//
//	command: The command to be inserted
//	buffer: A byte slice where the command request report will be inserted
//	nextSequenceNumber: The next sequence number for the command request
//	commandParameters: A slice of integers containing the command parameters
//
// Returns:
//
// An error if the command parameters exceed the limit or if the buffer is too short
func insertCommandRequestReport(
	command uint8,
	buffer []byte,
	nextSequenceNumber uint8,
	commandParameters []byte,
) tinygotypes.ErrorCode {
	// Check for nil buffer
	if buffer == nil {
		return ErrorCodeBNO08XCommandRequestReportNilBuffer
	}

	// Validate the number of command parameters and buffer length
	if commandParameters != nil && len(commandParameters) > 9 {
		return ErrorCodeBNO08XInsertCommandRequestReportTooManyArguments
	}
	if len(buffer) < 12 {
		return ErrorCodeBNO08XInsertCommandRequestReportBufferTooShort
	}

	// Initialize the buffer with zeros
	for i := 0; i < 12; i++ {
		buffer[i] = 0
	}

	// Insert the command request report into the buffer
	buffer[0] = ReportIDCommandRequest
	buffer[1] = byte(nextSequenceNumber)
	buffer[2] = command
	if commandParameters != nil {
		for idx, param := range commandParameters {
			buffer[3+idx] = param
		}
	}
	return tinygotypes.ErrorCodeNil
}
