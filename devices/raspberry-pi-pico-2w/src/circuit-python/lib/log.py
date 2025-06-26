class Logger:
    """
    Logger class that handles logging messages to a file.
    """

    # File path
    FILE_PATH = '/data.txt'
    
    def __init__(self, file_path: str = FILE_PATH):
        """
        Initializes the Logger with a specified file path.

        Args:
            file_path (str): The path to the log file.
        """
        # This clears the file if it exists, or creates it if it doesn't
        with open(file_path, "w") as f:
            pass

    def log(self, message: str):
        with open(self.file_path, "a") as f:
            f.write(message + "\n")