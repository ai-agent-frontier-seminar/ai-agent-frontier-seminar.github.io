import os
import subprocess

input_dir = "/media/andrew/DATA/postdoc/submission-papers/Open-space-reasoning/Dataset/donghao_haoyu/water_space"  # 修改为你的目录

for filename in os.listdir(input_dir):
    if filename.lower().endswith('.avi'):
        avi_path = os.path.join(input_dir, filename)
        mp4_path = os.path.join(input_dir, os.path.splitext(filename)[0] + '_compressed.mp4')
        cmd = [
            "ffmpeg",
            "-i", avi_path,
            "-vf", "scale=-2:720",           # 压缩分辨率到 720p，如需保留原分辨率，去掉这一行
            "-c:v", "libx264",
            "-preset", "medium",
            "-b:v", "1200k",                 # 视频比特率控制，1200k 为常见压缩档
            "-c:a", "aac",
            "-b:a", "128k",                  # 音频比特率
            "-movflags", "faststart",        # 优化网页播放
            mp4_path
        ]
        print(f"Converting and compressing: {avi_path} -> {mp4_path}")
        subprocess.run(cmd, check=True)
print("Batch conversion and compression complete.")
