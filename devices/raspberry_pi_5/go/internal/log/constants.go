package log

import (
	"path/filepath"
	"strings"
	"time"

	"github.com/ralvarezdev/klevor/devices/raspberry_pi_5/go/internal"
)

const (
	// LogsFolderName is the name of the logs folder
	LogsFolderName = "logs"
)

var (
	// MessagesChannelClosedMessage is the message logged when the messages channel is closed
	MessagesChannelClosedMessage = NewMessage(
		CategoryInfo,
		"Messages channel closed",
		nil,
	)

	// NilMessageReceivedMessage is the message logged when a nil message is received
	NilMessageReceivedMessage = NewMessage(
		CategoryWarning,
		"Nil message received",
		nil,
	)

	// ContextCancelledMessage is the message logged when the context is cancelled
	ContextCancelledMessage = NewMessage(
		CategoryInfo,
		"Context cancelled by caller",
		nil,
	)

	// LogsFolder is the folder where logs are stored
	LogsFolder string

	// Filename is the default log filename
	Filename = strings.ReplaceAll(
		time.Now().Format(time.DateTime),
		" ",
		"_",
	) + ".log"

	// FilePath is the default log file path
	FilePath string
)

func init() {
	// Initialize LogsFolder with the correct path
	LogsFolder = filepath.Join(internal.BinaryFolder, LogsFolderName)

	// Initialize FilePath with the correct path
	FilePath = filepath.Join(LogsFolder, Filename)
}
