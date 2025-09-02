package usbcdc

import (
	"fmt"
	"log"
	"time"

	"go.bug.st/serial"
)

func main() {
	ports, err := serial.GetPortsList()
	if err != nil {
		log.Fatalf("failed to list ports: %v", err)
	}
	if len(ports) == 0 {
		fmt.Println("No serial ports found.")
		return
	}
	fmt.Println("Available serial ports:")
	for _, p := range ports {
		fmt.Println(" -", p)
	}
	// Open the serial port
	mode := &serial.Mode{
		BaudRate: 9600,
	}
	port, err := serial.Open("/dev/ttyUSB0", mode) // Use "COM3" on Windows
	if err != nil {
		log.Fatal(err)
	}
	defer port.Close()

	// Set a timeout to prevent blocking forever
	port.SetReadTimeout(time.Second * 5)

	// Create a buffer for reading data
	buff := make([]byte, 100)

	// Loop to continuously read from the serial port
	for {
		n, err := port.Read(buff)
		if err != nil {
			// A timeout error means no data was received
			if err.Error() == "serial: reading timed out" {
				fmt.Println("Read timed out, no new data.")
				continue
			}
			log.Fatal(err)
		}
		if n == 0 {
			// Read can return 0 bytes, especially on Windows
			continue
		}
		// Process the data read
		fmt.Printf("Read %d bytes: %s\n", n, string(buff[:n]))
	}
}
