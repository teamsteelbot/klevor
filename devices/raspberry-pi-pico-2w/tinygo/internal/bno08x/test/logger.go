//go:build tinygo && (rp2040 || rp2350)

package tinygo_bno08x

import (
	"os"
	"encoding/binary"

	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

type (
	// DefaultLogger is a simple implementation of the Logger interface
	DefaultLogger struct{}
)

var (
	// Header is the header for debug messages
	Header = []byte("[BNO08x] ")
	
	// newlineBuffer is a byte slice representing a newline character
	newlineBuffer = []byte("\n")

	// hexPrefix is the prefix for error codes
	hexPrefix = []byte("0x")

	// uint8Buffer is the buffer used for hex code messages
	uint8Buffer = [1]byte{}

	// uint16Buffer is the buffer used for hex code messages
	uint16Buffer = [2]byte{}

	// uint32Buffer is the buffer used for hex code messages
	uint32Buffer = [4]byte{}
)

// NewDefaultLogger creates a new DefaultLogger instance
func NewDefaultLogger() *DefaultLogger {
	return &DefaultLogger{}
}

// logNewline is a helper function to print a newline if required
//
// Parameters:
//
//	newline: Whether to include a newline at the end of the log message.
func (l *DefaultLogger) logNewline(newline bool) {
	if newline {
		os.Stdout.Write(newlineBuffer)
	}
}

// logHeader is a helper function to print the header if required
//
// Parameters:
//
//	header: Whether to include the header in the log message.
func (l *DefaultLogger) logHeader(header bool) {
	if header {
		os.Stdout.Write(Header)
	}
}

// logHexCode is a helper function to print the hex code in hexadecimal format
//
// Parameters:
//
//	hexBuffer: The byte slice representing the hex code to print in hexadecimal format.
func (l *DefaultLogger) logHexCode(hexBuffer []byte) {
	if hexBuffer != nil {
		os.Stdout.Write(hexPrefix)
		os.Stdout.Write(hexBuffer)
	}
}

// LogMessage function to print log messages with messageBuffer content
//
// Parameters:
//
//	messageBuffer: The byte slice representing the message to print.
// header: Whether to include the header in the log message.
// newline: Whether to include a newline at the end of the log message.
func (l *DefaultLogger) LogMessage(messageBuffer []byte, header bool, newline bool) {
	if messageBuffer == nil {
		return
	}

	// Print the message
	l.logHeader(header)
	os.Stdout.Write(messageBuffer)
	l.logNewline(newline)
}

// LogMessageWithHexCode function to print log messages with messageBuffer and hexBuffer content
//
// Parameters:
//
//	messageBuffer: The byte slice representing the message to print.
//	hexBuffer: The byte slice representing the hex code to print in hexadecimal format.
// header: Whether to include the header in the log message.
// newline: Whether to include a newline at the end of the log message.
func (l *DefaultLogger) LogMessageWithHexCode(messageBuffer []byte, hexBuffer []byte, header bool, newline bool) {
	l.logHeader(header)
	if messageBuffer != nil {
		os.Stdout.Write(messageBuffer)
	}
	l.logHexCode(hexBuffer)
	l.logNewline(newline)
}

// LogMessageWithErrorCode function to print error messages with messageBuffer and errBuffer content
//
// Parameters:
//
//	messageBuffer: The byte slice representing the message to print.
//	errBuffer: The byte slice representing the error to print in hexadecimal format.
// header: Whether to include the header in the log message.
// newline: Whether to include a newline at the end of the log message.
func (l *DefaultLogger) LogMessageWithErrorCode(messageBuffer []byte, errCode tinygotypes.ErrorCode, header bool, newline bool) {
	// Store the error code in the buffer
	binary.BigEndian.PutUint16(uint16Buffer[:], uint16(errCode))

	// Print the message
	l.LogMessageWithHexCode(messageBuffer, uint16Buffer[:], header, newline)
}

// LogMessageWithUint8AsHexCode function to print log messages with messageBuffer and a uint8 value in hexadecimal format
//
// Parameters:
//
//	messageBuffer: The byte slice representing the message to print.
//	value: The uint8 value to print in hexadecimal format.
// header: Whether to include the header in the log message.
// newline: Whether to include a newline at the end of the log message.
func (l *DefaultLogger) LogMessageWithUint8AsHexCode(messageBuffer []byte, value uint8, header bool, newline bool) {
	// Store the uint8 value in the buffer
	uint8Buffer[0] = value
	
	// Print the message
	l.LogMessageWithHexCode(messageBuffer, uint8Buffer[:], header, newline)
}

// LogMessageWithUint16AsHexCode function to print log messages with messageBuffer and a uint16 value in hexadecimal format
//
// Parameters:
//
//	messageBuffer: The byte slice representing the message to print.
//	value: The uint16 value to print in hexadecimal format.
// header: Whether to include the header in the log message.
// newline: Whether to include a newline at the end of the log message.
func (l *DefaultLogger) LogMessageWithUint16AsHexCode(messageBuffer []byte, value uint16, header bool, newline bool) {
	// Store the uint16 value in the buffer
	binary.BigEndian.PutUint16(uint16Buffer[:], value)
	
	// Print the message
	l.LogMessageWithHexCode(messageBuffer, uint16Buffer[:], header, newline)
}

// LogMessageWithUint32AsHexCode function to print log messages with messageBuffer and a uint32 value in hexadecimal format
//
// Parameters:
//
//	messageBuffer: The byte slice representing the message to print.
//	value: The uint32 value to print in hexadecimal format.
// header: Whether to include the header in the log message.
// newline: Whether to include a newline at the end of the log message.
func (l *DefaultLogger) LogMessageWithUint32AsHexCode(messageBuffer []byte, value uint32, header bool, newline bool) {
	// Store the uint32 value in the buffer
	binary.BigEndian.PutUint32(uint32Buffer[:], value)
	
	// Print the message
	l.LogMessageWithHexCode(messageBuffer, uint32Buffer[:], header, newline)
}

// LogErrorCode function to print error messages with errBuffer content
//
// Parameters:
//
//	errBuffer: The byte slice representing the error to print in hexadecimal format.
// header: Whether to include the header in the log message.
// newline: Whether to include a newline at the end of the log message.
func (l *DefaultLogger) LogErrorCode(errCode tinygotypes.ErrorCode, header bool, newline bool) {
	// Store the error code in the buffer
	binary.BigEndian.PutUint16(uint16Buffer[:], uint16(errCode))

	// Print the message
	l.LogMessageWithHexCode(nil, uint16Buffer[:], header, newline)
}

// LogHexCode function to print hex code messages with hexBuffer content
//
// Parameters:
//
//	hexBuffer: The byte slice representing the hex code to print in hexadecimal format.
// header: Whether to include the header in the log message.
// newline: Whether to include a newline at the end of the log message.
func (l *DefaultLogger) LogHexCode(hexBuffer []byte, header bool, newline bool) {
	l.logHeader(header)
	l.logHexCode(hexBuffer)
	l.logNewline(newline)
}

// LogErrorCode function to print the hex code in hexadecimal format
//
// Parameters:
//
//	errCodeBuffer: The byte slice representing the error code to print in hexadecimal format.
// header: Whether to include the header in the log message.
// newline: Whether to include a newline at the end of the log message.
func (l *DefaultLogger) LogErrorCode(errCode tinygotypes.ErrorCode, header bool, newline bool) {
	// Store the error code in the buffer
	binary.BigEndian.PutUint16(uint16Buffer[:], uint16(errCode))

	// Print the message
	l.LogHexCode(uint16Buffer[:], header, newline)
}