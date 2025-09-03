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

	// TimestampFormat is the format for timestamps in log messages
	TimestampFormat = "15:04:05.000"

	// filePerm is the permission for log files
	filePerm = 0o644

	// dirPerm is the permission for log directories
	dirPerm = 0o755
)

var (
	// ChannelBufferSize is the size of the message channel buffer
	ChannelBufferSize = 1024

	// FileBufferSize is the size of the file buffer
	FileBufferSize = 1024 * 1024 // 1 MB

	// LoggerTag is the logger tag
	LoggerTag = "LOGGER"

	// MessagesChannelClosedMessage is the message logged when the messages channel is closed
	MessagesChannelClosedMessage = NewMessage(
		CategoryInfo,
		"Messages channel closed",
		LoggerTag,
	)

	// NilMessageReceivedMessage is the message logged when a LoggerTag message is received
	NilMessageReceivedMessage = NewMessage(
		CategoryWarning,
		"Nil message received",
		LoggerTag,
	)

	// ContextCancelledMessage is the message logged when the context is cancelled
	ContextCancelledMessage = NewMessage(
		CategoryInfo,
		"Context cancelled by caller",
		LoggerTag,
	)

	// LoggerStartedMessage is the message logged when the logger starts
	LoggerStartedMessage = NewMessage(
		CategoryInfo,
		"Started",
		LoggerTag,
	)

	// LogsFolder is the folder name where logs are stored
	LogsFolder string

	// Filename is the default log filename
	Filename = strings.ReplaceAll(
		strings.ReplaceAll(
			time.Now().Format(time.DateTime),
			" ",
			"-",
		),
		":",
		"-",
	) + ".log"

	// FilePath is the default log file path
	FilePath string
)

func init() {
	// Initialize LogsFolder with the correct path
	LogsFolder = filepath.Join(internal.RootFolderPath, LogsFolderName)

	// Initialize FilePath with the correct path
	FilePath = filepath.Join(LogsFolder, Filename)
}
