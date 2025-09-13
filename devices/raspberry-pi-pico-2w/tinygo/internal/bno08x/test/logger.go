//go:build tinygo && (rp2040 || rp2350)

package tinygo_bno08x

import (
	"os"
	"time"
	"encoding/binary"
	"math"

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

	// fullBufferHeader is the header for full buffer messages
	fullBufferHeader = []byte("FULL_BUFFER")

	// whitespaceBuffer is a byte slice representing a whitespace character
	whitespaceBuffer = []byte(" ")
	
	// newlineBuffer is a byte slice representing a newline character
	newlineBuffer = []byte("\n")

	// tabBuffer is a byte slice representing a tab character
	tabBuffer = []byte("\t")

	// twoPointsBuffer is a byte slice representing two points
	twoPointsBuffer = []byte(":")

	// dotBuffer is a byte slice representing a dot character
	dotBuffer = []byte(".")

	// hexPrefix is the prefix for error codes
	hexPrefix = []byte("0x")

	// float64Buffer is the buffer used for float64 messages
	float64Buffer = [8]byte{}

	// asciiHexDigits is a byte slice representing ASCII hex digits
	asciiHexDigits = []byte("0123456789ABCDEF")

	// asciiDecimalDigits is a byte slice representing ASCII decimal digits
	asciiDecimalDigits = []byte("0123456789")

	// uintToHexBuffer is a buffer used for converting uint64 to hex
	uintToHexBuffer = [16]byte{}

	// uintToDecimalBuffer is a buffer used for converting uint64 to decimal
	uintToDecimalBuffer = [20]byte{}
)

// NewDefaultLogger creates a new DefaultLogger instance
func NewDefaultLogger() *DefaultLogger {
	return &DefaultLogger{}
}

// uintToHexIndex returns the index in the asciiHexDigits for a given uint value
//
// Parameters:
//
//	value: The uint value to convert.
// size: The size of the uint (8, 16, 32, or 64).
// pos: The position of the hex digit to retrieve (0-based).
//
// Returns:
//
// The index in the asciiHexDigits for the specified hex digit, or -1 if the position is out of range.
func (l *DefaultLogger) uintToHexIndex(value uint64, size int, pos int) int {
	if pos < 0 || pos > (size/4)-1 {
		return -1
	}
	shift := (size/4-1 - pos) * 4
	return int((value >> shift) & 0x0F)
}

// uint8ToHex converts a uint8 value to its hexadecimal representation
//
// Parameters:
//
//	value: The uint8 value to convert.
//
// Returns:
//
// A byte slice representing the hexadecimal representation of the uint8 value.
func (l *DefaultLogger) uint8ToHex(value uint8) []byte {
	for c := range uintToHexBuffer {
		index := l.uintToHexIndex(uint64(value), 8, c)
		if index >= 0 {
			uintToHexBuffer[c] = asciiHexDigits[index]
		}
	}
	return uintToHexBuffer[:2]
}

// uint16ToHex converts a uint16 value to its hexadecimal representation
//
// Parameters:
//
//	value: The uint16 value to convert.
//
// Returns:
//
// A byte slice representing the hexadecimal representation of the uint16 value.
func (l *DefaultLogger) uint16ToHex(value uint16) []byte {
	for c := range uintToHexBuffer {
		index := l.uintToHexIndex(uint64(value), 16, c)
		if index >= 0 {
			uintToHexBuffer[c] = asciiHexDigits[index]
		}
	}
	return uintToHexBuffer[:4]
}

// uint32ToHex converts a uint32 value to its hexadecimal representation
//
// Parameters:
//
//	value: The uint32 value to convert.
//
// Returns:
//
// A byte slice representing the hexadecimal representation of the uint32 value.
func (l *DefaultLogger) uint32ToHex(value uint32) []byte {
	for c := range uintToHexBuffer {
		index := l.uintToHexIndex(uint64(value), 32, c)
		if index >= 0 {
			uintToHexBuffer[c] = asciiHexDigits[index]
		}
	}
	return uintToHexBuffer[:8]
}

// uint64ToHex converts a uint64 value to its hexadecimal representation
//
// Parameters:
//
//	value: The uint64 value to convert.
//
// Returns:
//
// A byte slice representing the hexadecimal representation of the uint64 value.
func (l *DefaultLogger) uint64ToHex(value uint64) []byte {
	for c := range uintToHexBuffer {
		index := l.uintToHexIndex(value, 64, c)
		if index >= 0 {
			uintToHexBuffer[c] = asciiHexDigits[index]
		}
	}
	return uintToHexBuffer[:16]
}

// uintToDecimal converts a uint8 value to its decimal representation
//
// Parameters:
//
//	value: The uint8 value to convert.
//
// Returns:
//
// A byte slice representing the decimal representation of the uint8 value.
func (l *DefaultLogger) uintToDecimal(value uint64) []byte {
    // Fill buffer from the end
    i := len(uintToDecimalBuffer)
    v := value
    if v == 0 {
        i--
        uintToDecimalBuffer[i] = asciiDecimalDigits[0]
    }
    for v > 0 && i > 0 {
        i--
        uintToDecimalBuffer[i] = asciiDecimalDigits[v%10]
        v /= 10
    }
    return uintToDecimalBuffer[i:]
}

// uintToDecimalFixed converts a uint value to its decimal representation with fixed width
//
// Parameters:
//
//	value: The uint value to convert.
//	width: The fixed width for the decimal representation.
//
// Returns:
//
// A byte slice representing the decimal representation of the uint value with leading zeros if necessary.
func (l *DefaultLogger) uintToDecimalFixed(value uint64, width int) []byte {
    buffer := l.uintToDecimal(uint64(value))
    pad := width - len(buffer)

	// Check if padding is needed
	if pad <= 0 {
		return buffer
	}
    
	// Move existing digits to the right
	copy(uintToDecimalBuffer[pad:], buffer)
    // Prepend leading zeros
    for i := 0; i < pad; i++ {
        uintToDecimalBuffer[i] = asciiDecimalDigits[0]
    }
    return uintToDecimalBuffer[:width]
}

// writeTimestamp is a helper function to print the current timestamp
func (l *DefaultLogger) writeTimestamp() {
	now := time.Now().UnixNano() / int64(time.Millisecond)

	// Get the hour, minute, second, and millisecond components
	hour := now / time.Hour.Milliseconds()
	minute := (now % time.Hour.Milliseconds()) / time.Minute.Milliseconds()
	second := (now % time.Minute.Milliseconds()) / time.Second.Milliseconds()
	millisecond := now % time.Second.Milliseconds()

	// Print the timestamp in the format HH:MM:SS.mmm
	buffer := l.uintToDecimalFixed(uint64(hour), 2)
	os.Stdout.Write(buffer)
	os.Stdout.Write(twoPointsBuffer)
	buffer = l.uintToDecimalFixed(uint64(minute), 2)
	os.Stdout.Write(buffer)
	os.Stdout.Write(twoPointsBuffer)
	buffer = l.uintToDecimalFixed(uint64(second), 2)
	os.Stdout.Write(buffer)
	os.Stdout.Write(dotBuffer)
	buffer = l.uintToDecimalFixed(uint64(millisecond), 3)
	os.Stdout.Write(buffer)
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
		// Buffer full, print the message and reset the index
		l.log(fullBufferHeader)
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
	l.AddUint16(uint16(errCode), newline, true)
}

// AddUint8 function to add a uint8 value to the messageBuffer
//
// Parameters:
//
//	value: The uint8 value to add.
//	newline: Whether to include a newline at the end of the log message.
//	hexCode: Whether to add the uint8 value in hexadecimal format.
func (l *DefaultLogger) AddUint8(value uint8, newline bool, hexCode bool) {
	if hexCode {
		buffer := l.uint8ToHex(value)
		l.AddHexCode(buffer, newline)
	} else {
		buffer := l.uintToDecimal(uint64(value))
		l.AddMessage(buffer, newline)
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
	if hexCode {
		buffer := l.uint16ToHex(value)
		l.AddHexCode(buffer, newline)
	} else {
		buffer := l.uintToDecimal(uint64(value))
		l.AddMessage(buffer, newline)
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
	if hexCode {
		buffer := l.uint32ToHex(value)
		l.AddHexCode(buffer, newline)
	} else {
		buffer := l.uintToDecimal(uint64(value))
		l.AddMessage(buffer, newline)
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
	if hexCode {
		buffer := l.uint64ToHex(value)
		l.AddHexCode(buffer, newline)
	} else {
		buffer := l.uintToDecimal(uint64(value))
		l.AddMessage(buffer, newline)
	}
}

// AddFloat64 function to add a float64 value to the messageBuffer
//
// Parameters:
//
//	value: The float64 value to add.
//	newline: Whether to include a newline at the end of the log message.
func (l *DefaultLogger) AddFloat64(value float64, newline bool) {
	// Store the float64 value in the buffer
	binary.BigEndian.PutUint64(float64Buffer[:], math.Float64bits(value))
	l.AddMessage(float64Buffer[:], newline)
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
	l.AddMessageWithUint16(message, uint16(errCode), separate, newline, true)
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

// AddMessageWithFloat64 function to add a message and float64 value to the messageBuffer
//
// Parameters:
//
//	message: The byte slice representing the message to add.
//	value: The float64 value to add.
//	separate: Whether to include a space between the message and float64 value.
//	newline: Whether to include a newline at the end of the log message.
func (l *DefaultLogger) AddMessageWithFloat64(message []byte, value float64, separate bool, newline bool) {
	l.AddMessage(message, false)
	if separate {
		l.AddSpace()
	}
	l.AddFloat64(value, newline)
}

// log functions for different log levels
//
// Parameters:
//
// header: The byte slice representing the log header to use.
func (l *DefaultLogger) log(header []byte) {
	l.writeHeader(header)
	l.writeMessage()
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