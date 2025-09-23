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

	// GracefulShutdownTimeout is the timeout for graceful shutdown
	GracefulShutdownTimeout = 10 * time.Second

	// ChannelBufferSize is the size of the message channel buffer
	ChannelBufferSize = 1024

	// FileBufferSize is the size of the file buffer
	FileBufferSize = 1024 * 1024 // 1 MB

	// HandlerLoggerTag is the logger tag
	HandlerLoggerTag = "LOGGER_HANDLER"
)

var (
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
	// Initialize logs folder with the correct path
	logsFolder := filepath.Join(internal.RootFolderPath, LogsFolderName)

	// Initialize FilePath with the correct path
	FilePath = filepath.Join(logsFolder, Filename)
}
