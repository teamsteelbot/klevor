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
	// GracefulShutdownTimeout is the timeout for graceful shutdown
	GracefulShutdownTimeout = 5 * time.Second

	// ChannelBufferSize is the size of the message channel buffer
	ChannelBufferSize = 1024

	// FileBufferSize is the size of the file buffer
	FileBufferSize = 1024 * 1024 // 1 MB

	// HandlerLoggerTag is the logger tag
	HandlerLoggerTag = "LOGGER_HANDLER"

	// MessagesChannelClosedMessage is the message logged when the messages channel is closed
	MessagesChannelClosedMessage = NewMessage(
		CategoryInfo,
		"Messages channel closed",
		HandlerLoggerTag,
	)

	// NilMessageReceivedMessage is the message logged when a LoggerTag message is received
	NilMessageReceivedMessage = NewMessage(
		CategoryWarning,
		"Nil message received",
		HandlerLoggerTag,
	)

	// ContextCancelledMessage is the message logged when the context is cancelled
	ContextCancelledMessage = NewMessage(
		CategoryInfo,
		"Context cancelled by caller",
		HandlerLoggerTag,
	)

	// StartedMessage is the message logged when the logger starts
	StartedMessage = NewMessage(
		CategoryInfo,
		"Started",
		HandlerLoggerTag,
	)

	// GracePeriodEndedMessage is the message logged when the grace period ends
	GracePeriodEndedMessage = NewMessage(
		CategoryInfo,
		"Grace period ended",
		HandlerLoggerTag,
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
