package internal

var (
	// BinaryFolder is the folder where the running binary resides
	BinaryFolder string
)

func init() {
	dir, err := ExecutableDir()
	if err != nil {
		panic(err)
	}
	BinaryFolder = dir
}
