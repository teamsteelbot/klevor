//go:build tinygo && (rp2040 || rp2350)

package tinygo_bno08x

import (
	"os"
	"time"
	"encoding/binary"

	tinygotypes "github.com/ralvarezdev/tinygo-types"
)

type (
	// DefaultLogger is a simple implementation of the Logger interface
	DefaultLogger struct{}
)

var (
	// timestampBuffer is the buffer used for timestamp messages
	timestampBuffer = [8]byte{}

	// messageBuffer is the buffer used for log messages
	messageBuffer = [512]byte{}

	// messageIndex is the current index in the message buffer
	messageIndex = 0

	// debugHeader is the header for debug messages
	debugHeader = []byte("DEBUG")

	// warningHeader is the header for warning messages
	warningHeader = []byte("WARNING")

	// errorHeader is the header for error messages
	errorHeader = []byte("ERROR")

	// infoHeader is the default header for info messages
	infoHeader = []byte("INFO")

	// whitespaceBuffer is a byte slice representing a whitespace character
	whitespaceBuffer = []byte(" ")
	
	// newlineBuffer is a byte slice representing a newline character
	newlineBuffer = []byte("\n")

	// tabBuffer is a byte slice representing a tab character
	tabBuffer = []byte("\t")

	// hexPrefix is the prefix for error codes
	hexPrefix = []byte("0x")

	// uint8Buffer is the buffer used for hex code messages
	uint8Buffer = [1]byte{}

	// uint16Buffer is the buffer used for hex code messages
	uint16Buffer = [2]byte{}

	// uint32Buffer is the buffer used for hex code messages
	uint32Buffer = [4]byte{}

	// uint64Buffer is the buffer used for hex code messages
	uint64Buffer = [8]byte{}
)

// NewDefaultLogger creates a new DefaultLogger instance
func NewDefaultLogger() *DefaultLogger {
	return &DefaultLogger{}
}

// writeTimestamp is a helper function to print the current timestamp
func (l *DefaultLogger) writeTimestamp() {
	now := time.Now().UnixNano() / int64(time.Millisecond)
	binary.BigEndian.PutUint64(timestampBuffer[:], uint64(now))
	os.Stdout.Write(timestampBuffer[:])
}

// writeNewline is a helper function to print a newline 
func (l *DefaultLogger) writeNewline() {
	os.Stdout.Write(newlineBuffer)
}

// writeSpace is a helper function to print a space
func (l *DefaultLogger) writeSpace() {
	os.Stdout.Write(whitespaceBuffer)
}

// writeHeader is a helper function to print the header if required
//
// Parameters:
//
//	header: Whether to include the header in the log message.
func (l *DefaultLogger) writeHeader(header []byte) {
	if header != nil {
		l.writeTimestamp()
		l.writeSpace()
		os.Stdout.Write(header)
		l.writeSpace()
	}
}

// writeMessage is a helper function to print the message from the messageBuffer
func (l *DefaultLogger) writeMessage() {
	if messageIndex > 0 {
		os.Stdout.Write(messageBuffer[:messageIndex])
		messageIndex = 0 // Reset index after printing
	}
}

// checkIndex checks if the messageIndex exceeds the messageBuffer size
func (l *DefaultLogger) checkIndex() {
	if messageIndex >= len(messageBuffer) {
		messageIndex = 0 // Reset index if it exceeds buffer size
	}
}

// AddSpace function to add a whitespace character to the messageBuffer
func (l *DefaultLogger) AddSpace() {
	messageBuffer[messageIndex] = whitespaceBuffer[0]
	messageIndex++
	l.checkIndex()
}

// AddNewline function to add a newline character to the messageBuffer
func (l *DefaultLogger) AddNewline() {
	messageBuffer[messageIndex] = newlineBuffer[0]
	messageIndex++
	l.checkIndex()
}

// AddTab function to add a tab character to the messageBuffer
func (l *DefaultLogger) AddTab() {
	messageBuffer[messageIndex] = tabBuffer[0]
	messageIndex++
	l.checkIndex()
}

// AddHexCode function to add hex code to the messageBuffer
//
// Parameters:
//
//	hexBuffer: The byte slice representing the hex code to print in hexadecimal format.
// newline: Whether to include a newline at the end of the log message.
func (l *DefaultLogger) AddHexCode(hexBuffer []byte, newline bool) {
	if hexBuffer != nil {
		for c := range hexPrefix {
			messageBuffer[messageIndex] = hexPrefix[c]
			messageIndex++
			l.checkIndex()
		}
		for c := range hexBuffer {
			messageBuffer[messageIndex] = hexBuffer[c]
			messageIndex++
			l.checkIndex()
		}

		if newline {
			l.AddNewline()
		}
	}
}

// AddErrorCode function to add an error code to the messageBuffer
//
// Parameters:
//
//	errCode: The error code to add to the message buffer.
// newline: Whether to include a newline at the end of the log message.
func (l *DefaultLogger) AddErrorCode(errCode tinygotypes.ErrorCode, newline bool) {
	// Store the error code in the buffer
	binary.BigEndian.PutUint16(uint16Buffer[:], uint16(errCode))
	l.AddHexCode(uint16Buffer[:], newline)
}

// AddUint8 function to add a uint8 value to the messageBuffer
//
// Parameters:
//
//	value: The uint8 value to add.
//	newline: Whether to include a newline at the end of the log message.
//	hexCode: Whether to add the uint8 value in hexadecimal format.
func (l *DefaultLogger) AddUint8(value uint8, newline bool, hexCode bool) {
	// Store the uint8 value in the buffer
	uint8Buffer[0] = value

	if hexCode {
		l.AddHexCode(uint8Buffer[:], newline)
	} else {
		l.AddMessage(uint8Buffer[:], newline)
	}
}

// AddUint16 function to add a uint16 value to the messageBuffer
//
// Parameters:
//
//	value: The uint16 value to add.
//	newline: Whether to include a newline at the end of the log message.
// hexCode: Whether to add the uint16 value in hexadecimal format.
func (l *DefaultLogger) AddUint16(value uint16, newline bool, hexCode bool) {
	// Store the uint16 value in the buffer
	binary.BigEndian.PutUint16(uint16Buffer[:], value)

	if hexCode {
		l.AddHexCode(uint16Buffer[:], newline)
	} else {
		l.AddMessage(uint16Buffer[:], newline)
	}
}

// AddUint32 function to add a uint32 value to the messageBuffer
//
// Parameters:
//
//	value: The uint32 value to add.
//	newline: Whether to include a newline at the end of the log message.
// hexCode: Whether to add the uint32 value in hexadecimal format.
func (l *DefaultLogger) AddUint32(value uint32, newline bool, hexCode bool) {
	// Store the uint32 value in the buffer
	binary.BigEndian.PutUint32(uint32Buffer[:], value)
	
	if hexCode {
		l.AddHexCode(uint32Buffer[:], newline)
	} else {
		l.AddMessage(uint32Buffer[:], newline)
	}
}

// AddUint64 function to add a uint64 value to the messageBuffer
//
// Parameters:
//
//	value: The uint64 value to add.
//	newline: Whether to include a newline at the end of the log message.
// hexCode: Whether to add the uint64 value in hexadecimal format.
func (l *DefaultLogger) AddUint64(value uint64, newline bool, hexCode bool) {
	// Store the uint64 value in the buffer
	binary.BigEndian.PutUint64(uint64Buffer[:], value)
	
	if hexCode {
		l.AddHexCode(uint64Buffer[:], newline)
	} else {
		l.AddMessage(uint64Buffer[:], newline)
	}
}

// AddMessage function to add a message to the messageBuffer
//
// Parameters:
//
//	message: The byte slice representing the message to add.
//	newline: Whether to include a newline at the end of the log message.
func (l *DefaultLogger) AddMessage(message []byte, newline bool) {
	if message != nil {
		for c := range message {
			messageBuffer[messageIndex] = message[c]
			messageIndex++
			l.checkIndex()
		}

		if newline {
			l.AddNewline()
		}
	}
}

// AddMessageWithHexCode function to add a message and hex code to the messageBuffer
//
// Parameters:
//
//	message: The byte slice representing the message to add.
//	hexBuffer: The byte slice representing the hex code to add in hexadecimal format.
//	separate: Whether to include a space between the message and hex code.
//	newline: Whether to include a newline at the end of the log message.
func (l *DefaultLogger) AddMessageWithHexCode(message []byte, hexBuffer []byte, separate bool, newline bool) {
	l.AddMessage(message, false)
	if separate {
		l.AddSpace()
	}
	l.AddHexCode(hexBuffer, newline)
}

// AddMessageWithErrorCode function to add a message and error code to the messageBuffer
//
// Parameters:
//
//	message: The byte slice representing the message to add.
//	errCode: The error code to add to the message buffer.
//	separate: Whether to include a space between the message and error code.
//	newline: Whether to include a newline at the end of the log message.
func (l *DefaultLogger) AddMessageWithErrorCode(message []byte, errCode tinygotypes.ErrorCode, separate bool, newline bool) {
	// Store the error code in the buffer
	binary.BigEndian.PutUint16(uint16Buffer[:], uint16(errCode))
	l.AddMessageWithHexCode(message, uint16Buffer[:], separate, newline)
}

// AddMessageWithUint8 function to add a message and uint8 value to the messageBuffer
//
// Parameters:
//
//	message: The byte slice representing the message to add.
//	value: The uint8 value to add.
//	separate: Whether to include a space between the message and uint8 value.
//	newline: Whether to include a newline at the end of the log message.
//	hexCode: Whether to add the uint8 value in hexadecimal format.
func (l *DefaultLogger) AddMessageWithUint8(message []byte, value uint8, separate bool, newline bool, hexCode bool) {
	l.AddMessage(message, false)
	if separate {
		l.AddSpace()
	}
	l.AddUint8(value, newline, hexCode)
}

// AddMessageWithUint16 function to add a message and uint16 value to the messageBuffer
//
// Parameters:
//
//	message: The byte slice representing the message to add.
//	value: The uint16 value to add.
//	separate: Whether to include a space between the message and uint16 value.
//	newline: Whether to include a newline at the end of the log message.
//	hexCode: Whether to add the uint16 value in hexadecimal format.
func (l *DefaultLogger) AddMessageWithUint16(message []byte, value uint16, separate bool, newline bool, hexCode bool) {
	l.AddMessage(message, false)
	if separate {
		l.AddSpace()
	}
	l.AddUint16(value, newline, hexCode)
}

// AddMessageWithUint32 function to add a message and uint32 value to the messageBuffer
//
// Parameters:
//
//	message: The byte slice representing the message to add.
//	value: The uint32 value to add.
//	separate: Whether to include a space between the message and uint32 value.
//	newline: Whether to include a newline at the end of the log message.
//	hexCode: Whether to add the uint32 value in hexadecimal format.
func (l *DefaultLogger) AddMessageWithUint32(message []byte, value uint32, separate bool, newline bool, hexCode bool) {
	l.AddMessage(message, false)
	if separate {
		l.AddSpace()
	}
	l.AddUint32(value, newline, hexCode)
}

// AddMessageWithUint64 function to add a message and uint64 value to the messageBuffer
//
// Parameters:
//
//	message: The byte slice representing the message to add.
//	value: The uint64 value to add.
//	separate: Whether to include a space between the message and uint64 value.
//	newline: Whether to include a newline at the end of the log message.
//	hexCode: Whether to add the uint64 value in hexadecimal format.
func (l *DefaultLogger) AddMessageWithUint64(message []byte, value uint64, separate bool, newline bool, hexCode bool) {
	l.AddMessage(message, false)
	if separate {
		l.AddSpace()
	}
	l.AddUint64(value, newline, hexCode)
}

// log functions for different log levels
//
// Parameters:
//
// header: The byte slice representing the log header to use.
func (l *DefaultLogger) log(header []byte) {
	l.writeHeader(header)
	l.writeMessage()
	l.writeNewline()
}

// Debug function to print debug messages with messageBuffer content
func (l *DefaultLogger) Debug() {
	l.log(debugHeader)
}

// Warning function to print warning messages with messageBuffer content
func (l *DefaultLogger) Warning() {
	l.log(warningHeader)
}

// Error function to print error messages with messageBuffer content
func (l *DefaultLogger) Error() {
	l.log(errorHeader)
}

// Info function to print info messages with messageBuffer content
func (l *DefaultLogger) Info() {
	l.log(infoHeader)
}

// DebugMessage function to print a debug message
//
// Parameters:
//
//	message: The byte slice representing the debug message to print.
func (l *DefaultLogger) DebugMessage(message []byte) {
	l.AddMessage(message, true)
	l.Debug()
}

// WarningMessage function to print a warning message
//
// Parameters:
//
//	message: The byte slice representing the warning message to print.
func (l *DefaultLogger) WarningMessage(message []byte) {
	l.AddMessage(message, true)
	l.Warning()
}

// ErrorMessage function to print an error message
//
// Parameters:
//
//	message: The byte slice representing the error message to print.
func (l *DefaultLogger) ErrorMessage(message []byte) {
	l.AddMessage(message, true)
	l.Error()
}

// InfoMessage function to print an info message
//
// Parameters:
//
//	message: The byte slice representing the info message to print.
func (l *DefaultLogger) InfoMessage(message []byte) {
	l.AddMessage(message, true)
	l.Info()
}

// WarningMessageWithErrorCode function to print a warning message with an error code
//
// Parameters:
//
//	message: The byte slice representing the warning message to print.
//	errCode: The error code to add to the message buffer.
//	separate: Whether to include a space between the message and error code.
func (l *DefaultLogger) WarningMessageWithErrorCode(message []byte, errCode tinygotypes.ErrorCode, separate bool) {
	l.AddMessageWithErrorCode(message, errCode, separate, true)
	l.Warning()
}

// ErrorMessageWithErrorCode function to print an error message with an error code
//
// Parameters:
//
//	message: The byte slice representing the error message to print.
//	errCode: The error code to add to the message buffer.
//	separate: Whether to include a space between the message and error code.
func (l *DefaultLogger) ErrorMessageWithErrorCode(message []byte, errCode tinygotypes.ErrorCode, separate bool) {
	l.AddMessageWithErrorCode(message, errCode, separate, true)
	l.Error()
}