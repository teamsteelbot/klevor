package main

import (
	"fmt"
	"log"

	"go.bug.st/serial/enumerator"
)

func main() {
	/*
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
	*/

	details, err := enumerator.GetDetailedPortsList()
	if err != nil {
		log.Fatalf("failed to get detailed port list: %v", err)
	}
	if len(details) == 0 {
		fmt.Println("No serial ports found.")
		return
	}

	fmt.Println("Detected serial ports (USB CDC highlighted):")
	for _, d := range details {
		if d.IsUSB {
			fmt.Printf(
				"USB CDC: %s\n  VID:PID=%04X:%04X\n Product: %s\n  SerialNumber: %s\n",
				d.Name,
				d.VID,
				d.PID,
				safe(d.Product),
				safe(d.SerialNumber),
			)
		} else {
			fmt.Printf("Other: %s\n", d.Name)
		}
	}
}

func safe(s string) string {
	if s == "" {
		return "(n/a)"
	}
	return s
}
