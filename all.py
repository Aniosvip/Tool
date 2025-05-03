import subprocess

# Danh sách các file cần chạy
scripts = ["sunwin.py", "lag.py", "key.py", "room.py", "acc.py"]

# Chạy đồng thời các file
processes = [subprocess.Popen(["python", script]) for script in scripts]

# Đợi tất cả các tiến trình kết thúc
for process in processes:
    process.wait()