package internal

import (
    "runtime"
)

var (
	// MemoryStatsHeader is the header for memory statistics output
	MemoryStatsHeader = []byte("Memory Stats:")

	// MemoryStatsAllocKey is the key for currently allocated memory in KB
	MemoryStatsAllocKey = []byte("\tCurrently Allocated (KB) =")
	
	// MemoryStatsTotalAllocKey is the key for cumulative allocated memory in KB
	MemoryStatsTotalAllocKey = []byte("\tTotal Allocated (KB) =")
)

// PrintMemory prints the current memory statistics.
func PrintMemory() {
    var m runtime.MemStats
    runtime.ReadMemStats(&m)

	// Log memory stats
	Logger.AddMessage(MemoryStatsHeader, true)
	Logger.AddMessageWithUint64(MemoryStatsAllocKey, m.Alloc / 1024, true, true, false)
	Logger.AddMessageWithUint64(MemoryStatsTotalAllocKey, m.TotalAlloc / 1024, true, true, false)
	Logger.Debug()
}