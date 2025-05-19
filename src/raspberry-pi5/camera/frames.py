import subprocess
import shlex

from camera import WIDTH, HEIGHT, FPS, CODEC


# Generate frames from the camera using libcamera-vid
def generate_frames():
    # Execute the libcamera-vid command to capture video
    command = f'libcamera-vid -n -t 0 --width {WIDTH} --height {HEIGHT} --framerate {FPS} --codec {CODEC} -o -'
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                           bufsize=-1)

    try:
        while True:
            # Read the JPEG header (2 bytes)
            header = process.stdout.read(2)
            if not header:
                print("No more data from libcamera-vid (header)")
                break
            if header != b'\xff\xd8':
                print(f"Incorrect JPEG SOI marker: {header}")
                continue

            # Read the rest of the JPEG frame
            frame_data = header
            while True:
                byte = process.stdout.read(1)
                if not byte:
                    print("No more data from libcamera-vid (frame)")
                    break

                frame_data += byte
                if frame_data.endswith(b'\xff\xd9'):
                    print(f"Found complete JPEG frame, size: {len(frame_data)}")
                    yield (frame_data)
                    break
    finally:
        process.terminate()
        stderr_output = process.stderr.read().decode()
        if stderr_output:
            print(f"libcamera-vid stderr: {stderr_output}")