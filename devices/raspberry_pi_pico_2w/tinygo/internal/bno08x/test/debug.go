//go:build tinygo && (rp2040 || rp2350)

package test

var (
	// Channels contains the channel IDs and their names
	Channels = map[uint8]string{
		ChannelSHTPCommand:            "SHTP_COMMAND",
		ChannelExe:                    "EXE",
		ChannelControl:                "CONTROL",
		ChannelInputSensorReports:     "INPUT_SENSOR_REPORTS",
		ChannelWakeInputSensorReports: "WAKE_INPUT_SENSOR_REPORTS",
		ChannelGyroRotationVector:     "GYRO_ROTATION_VECTOR",
	}

	// Reports contains the report IDs and their names
	Reports = map[uint8]string{
		ReportIDBaseTimestamp:             "BASE_TIMESTAMP",
		ReportIDCommandRequest:            "COMMAND_REQUEST",
		ReportIDCommandResponse:           "COMMAND_RESPONSE",
		ReportIDFRSReadRequest:            "FRS_READ_REQUEST",
		ReportIDFRSReadResponse:           "FRS_READ_RESPONSE",
		ReportIDFRSWriteData:              "FRS_WRITE_DATA",
		ReportIDFRSWriteRequest:           "FRS_WRITE_REQUEST",
		ReportIDFRSWriteResponse:          "FRS_WRITE_RESPONSE",
		ReportIDGetFeatureRequest:         "GET_FEATURE_REQUEST",
		ReportIDGetFeatureResponse:        "GET_FEATURE_RESPONSE",
		ReportIDSetFeatureCommand:         "SET_FEATURE_COMMAND",
		ReportIDTimestampRebase:           "TIMESTAMP_REBASE",
		ReportIDAccelerometer:             "ACCELEROMETER",
		0x29:                              "ARVR_STABILIZED_GAME_ROTATION_VECTOR",
		0x28:                              "ARVR_STABILIZED_ROTATION_VECTOR",
		0x22:                              "CIRCLE_DETECTOR",
		0x1A:                              "FLIP_DETECTOR",
		ReportIDGameRotationVector:        "GAME_ROTATION_VECTOR",
		ReportIDGeomagneticRotationVector: "GEOMAGNETIC_ROTATION_VECTOR",
		ReportIDGravity:                   "GRAVITY",
		ReportIDGyroscope:                 "GYROSCOPE",
		ReportIDLinearAcceleration:        "LINEAR_ACCELERATION",
		ReportIDMagnetometer:              "MAGNETIC_FIELD",
		ReportIDActivityClassifier:        "PERSONAL_ACTIVITY_CLASSIFIER",
		0x1B:                              "PICKUP_DETECTOR",
		0x21:                              "POCKET_DETECTOR",
		ReportIDProductIDRequest:          "PRODUCT_ID_REQUEST",
		ReportIDProductIDResponse:         "PRODUCT_ID_RESPONSE",
		ReportIDRawAccelerometer:          "RAW_ACCELEROMETER",
		ReportIDRawGyroscope:              "RAW_GYROSCOPE",
		ReportIDRawMagnetometer:           "RAW_MAGNETOMETER",
		ReportIDRotationVector:            "ROTATION_VECTOR",
		0x17:                              "SAR",
		ReportIDShakeDetector:             "SHAKE_DETECTOR",
		0x12:                              "SIGNIFICANT_MOTION",
		0x1F:                              "SLEEP_DETECTOR",
		ReportIDStabilityClassifier:       "STABILITY_CLASSIFIER",
		0x1C:                              "STABILITY_DETECTOR",
		ReportIDStepCounter:               "STEP_COUNTER",
		0x18:                              "STEP_DETECTOR",
		0x10:                              "TAP_DETECTOR",
		0x20:                              "TILT_DETECTOR",
		0x07:                              "UNCALIBRATED_GYROSCOPE",
		0x0F:                              "UNCALIBRATED_MAGNETIC_FIELD",
	}
)

/*
const (
	// ReportIDRawUncalibratedGyroscope is the report ID for uncalibrated gyroscope (rad/s).
	ReportIDRawUncalibratedGyroscope uint8 = 0x07 // 16

	// ReportIDUncalibratedMagneticField is the report ID for magnetic field uncalibrated (in µTesla).
	// The magnetic field measurement without hard-iron offset applied, the hard-iron
	// estimate is provided as a separate parameter.
	ReportIDUncalibratedMagneticField uint8 = 0x0F

	// ReportIDARVRStabilizedGameRotationVector is the reportID for AR/VR Stabilized Game Rotation vector
	ReportIDARVRStabilizedGameRotationVector uint8 = 0x29

	// ReportIDARVRStabilizedRotationVector is the reportID for AR/VR Stabilized Rotation Vector
	ReportIDARVRStabilizedRotationVector uint8 = 0x28

	// ReportIDTapDetector is the report ID for the tap detector
	ReportIDTapDetector       uint8 = 0x10

	// ReportIDSignificantMotion is the report ID for the significant motion sensor
	ReportIDSignificantMotion uint8 = 0x12

	// ReportIDSar is the report ID for the SAR (Specific Absorption Rate) sensor
	ReportIDSar               uint8 = 0x17

	// ReportIDStepDetector is the report ID for the step detector
	ReportIDStepDetector      uint8 = 0x18

	// ReportIDFlipDetector is the report ID for the flip detector
	ReportIDFlipDetector      uint8 = 0x1A

	// ReportIDPickupDetector is the report ID for the pickup detector
	ReportIDPickupDetector    uint8 = 0x1B

	// ReportIDStabilityDetector is the report ID for the stability detector
	ReportIDStabilityDetector uint8 = 0x1C

	// ReportIDSleepDetector is the report ID for the sleep detector
	ReportIDSleepDetector     uint8 = 0x1F

	// ReportIDTiltDetector is the report ID for the tilt detector
	ReportIDTiltDetector      uint8 = 0x20

	// ReportIDPocketDetector is the report ID for the pocket detector
	ReportIDPocketDetector    uint8 = 0x21

	// ReportIDCircleDetector is the report ID for the circle detector
	ReportIDCircleDetector    uint8 = 0x22
)
*/
