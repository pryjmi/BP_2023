import subprocess

# runs detection with recognition and data synchronization concurrently
if __name__ == "__main__":
    process1 = subprocess.Popen(['python', '-c', 'import src_detection.detect; src_detection.detect.run()'])
    process2 = subprocess.Popen(['python', '-c', 'import src_sync_data.sync_data; src_sync_data.sync_data.run()'])
    process1.wait()
    process2.wait()
