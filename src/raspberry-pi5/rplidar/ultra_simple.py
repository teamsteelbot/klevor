import subprocess
import os
import time # For demonstration, to limit reading time

command = [
    "./ultra_simple",
    "--channel",
    "--serial",
    "/dev/ttyUSB0",
    "460800"
]

# Max time to read output (e.g., 30 seconds)
read_duration = 30
start_time = time.time()

print(f"Starting program to read output for {read_duration} seconds: {' '.join(command)}")

process = None # Initialize process to None
try:
    # Use Popen to start the process without waiting for it to finish
    # stdout=subprocess.PIPE allows us to read from the program's standard output
    # stderr=subprocess.PIPE allows us to read from standard error
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True, # Decode output as text
        bufsize=1, # Line-buffered output
        universal_newlines=True # Handles different newline characters
    )

    print("\n--- Streaming Program Output (reading for a limited time) ---")
    # Read output line by line until the duration expires or the process ends
    while (time.time() - start_time) < read_duration and process.poll() is None:
        line = process.stdout.readline()
        if line:
            print(f"STDOUT: {line.strip()}") # .strip() removes trailing newline

        # You can also read stderr similarly if needed
        # error_line = process.stderr.readline()
        # if error_line:
        #     print(f"STDERR: {error_line.strip()}")

        # Add a small delay to avoid busy-waiting and yield CPU
        time.sleep(0.0001)

    print(f"\n--- Finished reading after {read_duration} seconds or process termination ---")

    # If the process is still running after the read duration, terminate it
    if process.poll() is None:
        print("Program still running. Terminating it now...")
        process.terminate() #politely request termination
        process.wait(timeout=5) # Wait for it to terminate, with a small timeout
        if process.poll() is None:
            print("Program did not terminate gracefully. Killing it...")
            process.kill() # Forcefully kill it
        process.wait() # Wait for final cleanup

    # After termination, read any remaining output
    remaining_stdout, remaining_stderr = process.communicate()
    if remaining_stdout:
        print("\n--- Remaining Standard Output ---")
        print(remaining_stdout)
    if remaining_stderr:
        print("\n--- Remaining Standard Error ---")
        print(remaining_stderr)

    print(f"\n--- Program Exit Code: {process.returncode} ---")

except FileNotFoundError:
    print(f"Error: The program '{command[0]}' was not found.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    # Ensure the process is cleaned up even if an error occurs
    if process and process.poll() is None:
        print("Ensuring process is terminated in finally block...")
        process.terminate()
        process.wait(timeout=5)
        if process.poll() is None:
            process.kill()
        process.wait()
