package usbcdc 

// CalculateChecksum calculates the checksum for a message based on its category and data bytes.
//
// Parameters:
//
// category: The category byte of the message
// data: A slice of bytes representing the data of the message
func CalculateChecksum(category byte, data []byte) byte {
	checksum := category
	for _, b := range data {
		checksum += b
	}
	return checksum
}