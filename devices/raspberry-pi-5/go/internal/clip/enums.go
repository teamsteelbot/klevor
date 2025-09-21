package clip

import (
	"fmt"
	"strings"
)

type (
	// PositiveLabel is an enum to define the label of a positive Hailo CLIP classification
	PositiveLabel uint8

	// NegativeLabel is an enum to define the label of a negative Hailo CLIP classification
	NegativeLabel uint8
)

const (
	PositiveLabelNil PositiveLabel = iota
	PositiveLabelGreenBlock
	PositiveLabelRedBlock
	PositiveLabelMagentaBlock
)

const (
	NegativeLabelNil NegativeLabel = iota
	NegativeLabelWhiteBackground
	NegativeLabelBlackBlock
)

var (
	// PositiveLabelNames maps a given PositiveLabel to its string name
	PositiveLabelNames = map[PositiveLabel]string{
		PositiveLabelGreenBlock:   "green block",
		PositiveLabelRedBlock:     "red block",
		PositiveLabelMagentaBlock: "magenta block",
	}

	// NegativeLabelNames maps a given NegativeLabel to its string name
	NegativeLabelNames = map[NegativeLabel]string{
		NegativeLabelWhiteBackground: "white background",
		NegativeLabelBlackBlock:      "black block",
	}
)

// String returns the string representation of the PositiveLabel
//
// Returns:
//
// The string representation of the PositiveLabel enum
func (p PositiveLabel) String() string {
	return PositiveLabelNames[p]
}

// PositiveLabelFromString returns the PositiveLabel enum based on a given string
//
// Parameters:
//
// s: The string name to search on PositiveLabelNames
//
// Returns:
//
// The PositiveLabel enum value, or an error if the key wasn't found for the given value
func PositiveLabelFromString(s string) (PositiveLabel, error) {
	// Format the string
	s = strings.ToLower(strings.TrimSpace(s))

	// Search for the given positive label name
	for key, value := range PositiveLabelNames {
		if value == s {
			return key, nil
		}
	}
	return PositiveLabelNil, fmt.Errorf(ErrInvalidPositiveLabelName, s)
}

// PositiveLabelSliceToStringSlice converts a slice of PositiveLabel enums to a slice of strings
//
// Parameters:
//
// labels: The slice of PositiveLabel enums to convert
//
// Returns:
//
// A slice of strings representing the names of the PositiveLabel enums
func PositiveLabelSliceToStringSlice(labels []PositiveLabel) []string {
	strLabels := make([]string, len(labels))
	for i, label := range labels {
		strLabels[i] = label.String()
	}
	return strLabels
}

// String returns the string representation of the NegativeLabel
//
// Returns:
//
// The string representation of the NegativeLabel enum
func (n NegativeLabel) String() string {
	return NegativeLabelNames[n]
}

// NegativeLabelSliceToStringSlice converts a slice of NegativeLabel enums to a slice of strings
//
// Parameters:
//
// labels: The slice of NegativeLabel enums to convert
//
// Returns:
//
// A slice of strings representing the names of the NegativeLabel enums
func NegativeLabelSliceToStringSlice(labels []NegativeLabel) []string {
	strLabels := make([]string, len(labels))
	for i, label := range labels {
		strLabels[i] = label.String()
	}
	return strLabels
}
