package internal

import (
    "runtime"
	"os"
	"encoding/binary"
)

var (
	// MemoryStatsHeader is the header for memory statistics output
	MemoryStatsHeader = []byte("\nMemory Stats:")

	// MemoryStatsAllocKey is the key for currently allocated memory in KB
	MemoryStatsAllocKey = []byte("\n\tCurrently Allocated (KB) = ")
	
	// MemoryStatsTotalAllocKey is the key for cumulative allocated memory in KB
	MemoryStatsTotalAllocKey = []byte("\n\tTotal Allocated (KB) = ")

	// MemoryStatsAlloc is the currently allocated memory in bytes
	MemoryStatsAlloc [8]byte = [8]byte{}

	// MemoryStatsTotalAlloc is the cumulative allocated memory in bytes
	MemoryStatsTotalAlloc [8]byte = [8]byte{}
)

// PrintMemory prints the current memory statistics.
func PrintMemory() {
    var m runtime.MemStats
    runtime.ReadMemStats(&m)

	// Log memory stats
	os.Stdout.Write(MemoryStatsHeader)

	// Convert Alloc and TotalAlloc to byte slices
	binary.LittleEndian.PutUint64(MemoryStatsAlloc[:], m.Alloc)
	binary.LittleEndian.PutUint64(MemoryStatsTotalAlloc[:], m.TotalAlloc)

	// Log Alloc and TotalAlloc as byte slices
	os.Stdout.Write(MemoryStatsAllocKey)
	os.Stdout.Write(MemoryStatsAlloc[:])
	os.Stdout.Write(MemoryStatsTotalAllocKey)
	os.Stdout.Write(MemoryStatsTotalAlloc[:])
}