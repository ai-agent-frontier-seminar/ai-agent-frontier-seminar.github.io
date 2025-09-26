import re

model_links = {
    "GPT 4o": "https://arxiv.org/pdf/2410.21276",
    "Gemini 1.5 pro": "https://arxiv.org/pdf/2403.05530",
    "InternVL2.5 26B": "https://huggingface.co/OpenGVLab/InternVL2_5-26B",
    "InternVL2.5 8B": "https://huggingface.co/OpenGVLab/InternVL2_5-8B",
    "InternVL2.5 4B": "https://huggingface.co/OpenGVLab/InternVL2_5-4B",
    "LLaVA Next 32B": "https://huggingface.co/lmms-lab/llava-next-qwen-32b",
    "LLaVA Video 7B": "https://huggingface.co/lmms-lab/LLaVA-Video-7B-Qwen2",
    "LLaVA OneVision 7B": "https://huggingface.co/lmms-lab/llava-onevision-qwen2-7b-ov",
    "Qwen2.5 VL 32B": "https://huggingface.co/Qwen/Qwen2.5-VL-32B-Instruct",
    "Qwen2.5 VL 7B": "https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct",
    "Qwen2.5 VL 3B": "https://huggingface.co/Qwen/Qwen2.5-VL-3B-Instruct",
}

def get_model_link(model, size):
    key_full = f"{model} {size}".strip()
    key_model = model.strip()
    if key_full in model_links:
        return model_links[key_full]
    elif key_model in model_links:
        return model_links[key_model]
    return None

with open("open_space_tbody.html", "r", encoding="utf-8") as f:
    html = f.read()

def model_td_replace(match):
    # 捕获模型名, 可选🥇, 尺寸(可有可无), 🥇可在名字后，也可能单独有td
    model = match.group("model").strip()
    trophy = match.group("trophy") or ""
    size = match.group("size")
    size = size.strip() if size else "-"
    rest = match.group("rest") if match.group("rest") else ""

    link = get_model_link(model, size)
    label = f"{model}{trophy}"
    if link:
        model_cell = f'<a href="{link}">{label}</a>'
    else:
        model_cell = label

    # 保证原始td结构
    return f"<td>{model_cell}</td><td>{size}</td>{rest}"

# 支持<td>模型名[ 🥇]</td><td>Size</td> 也支持<td>模型名 🥇</td><td>-</td>
pattern = re.compile(
    r"<td>(?P<model>[A-Za-z0-9\.\s]+?)(?P<trophy> 🥇)?</td><td>(?P<size>[0-9A-Za-z\-]+|-)</td>(?P<rest>(?:<td>.*?</td>)*)"
)

# 替换所有模型td
new_html = re.sub(pattern, model_td_replace, html)

with open("all_space_tbody_table_linked.html", "w", encoding="utf-8") as f:
    f.write(new_html)

print("模型链接添加完成，输出文件: all_space_tbody_table_linked.html")
