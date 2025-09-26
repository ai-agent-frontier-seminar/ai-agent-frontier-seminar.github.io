import os
import subprocess

input_dir = "/media/andrew/DATA/postdoc/submission-papers/Open-space-reasoning/Dataset/donghao_haoyu/water_space/short"  # 修改为你的目录

for filename in os.listdir(input_dir):
    if filename.lower().endswith('.mp4'):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(input_dir, os.path.splitext(filename)[0] + '_compressed.mp4')
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-vf", "scale=-2:720",         # 压缩到 720p，如需保留原分辨率，可删去本行
            "-c:v", "libx264",
            "-preset", "medium",
            "-b:v", "1200k",               # 调整比特率以获得压缩效果
            "-c:a", "aac",
            "-b:a", "128k",
            "-movflags", "faststart",
            output_path
        ]
        print(f"Compressing: {input_path} -> {output_path}")
        subprocess.run(cmd, check=True)
print("All videos compressed.")
