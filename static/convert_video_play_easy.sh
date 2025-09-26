#!/bin/bash

for i in $(seq 1 15); do
  input="/media/andrew/DATA/postdoc/submission-papers/Open-space-reasoning/Dataset/donghao_haoyu/water_space/water_space_short_compress/water_space_short_${i}_compressed.mp4"
  output="/media/andrew/DATA/postdoc/submission-papers/Open-space-reasoning/homepage/open_space_reasoning/static/videos/water_space/water_space_short_${i}_output.mp4"
  ffmpeg -i "$input" -c:v libx264 -profile:v baseline -level 3.0 -pix_fmt yuv420p -movflags faststart -c:a aac -strict -2 "$output"
done
