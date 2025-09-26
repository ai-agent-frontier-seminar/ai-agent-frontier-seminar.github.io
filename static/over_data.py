import pandas as pd
from bs4 import BeautifulSoup
import os

# =============== 配置 ====================
AGG_METHOD = "mean"   # "sum" 或 "mean"

# =============== 工具函数 ====================
def normalize_model_name(name):
    """去除🥇等特殊符号，避免对不上"""
    return name.replace("🥇", "").strip() if isinstance(name, str) else name

def html_tbody_to_csv(html_file, csv_file):
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    rows = []
    difficulty = None
    for tr in soup.find_all('tr'):
        tds = tr.find_all(['td'])
        if not tds: continue
        row = []
        if tds[0].has_attr('rowspan'):
            difficulty = tds[0].get_text(strip=True)
            tds = tds[1:]
        row.append(difficulty)
        for td in tds:
            row.append(td.get_text(strip=True))
        rows.append(row)
    # 自动生成表头（支持最长行）
    max_len = max(len(row) for row in rows)
    default_header = ['Difficulty', 'Models', 'Size']
    other_header = [f'Col{i}' for i in range(1, max_len-len(default_header)+1)]
    header = default_header + other_header
    with open(csv_file, 'w', encoding='utf-8') as f:
        f.write(','.join(header[:max_len]) + '\n')
        for row in rows:
            row = [str(x) if x is not None else '' for x in row]
            f.write(','.join(row + ['']*(max_len-len(row))) + '\n')

def merge_csv_and_agg(land_csv, air_csv, output_csv, agg_method='mean'):
    df_land = pd.read_csv(land_csv).fillna('')
    df_air = pd.read_csv(air_csv).fillna('')
    # 标准化模型名字，避免对不齐
    df_land['Models_norm'] = df_land['Models'].map(normalize_model_name)
    df_air['Models_norm'] = df_air['Models'].map(normalize_model_name)
    # key列
    key_cols = ['Difficulty', 'Models_norm', 'Size']
    val_cols = [c for c in df_land.columns if c not in ['Difficulty', 'Models', 'Models_norm', 'Size']]
    records = {}
    # 填充land
    for _, row in df_land.iterrows():
        key = (row['Difficulty'], row['Models_norm'], str(row['Size']))
        records[key] = [float(row[c]) if row[c] != '' else 0.0 for c in val_cols]
    # 合并air
    for _, row in df_air.iterrows():
        key = (row['Difficulty'], row['Models_norm'], str(row['Size']))
        vals_air = [float(row[c]) if row[c] != '' else 0.0 for c in val_cols]
        if key in records:
            vals_land = records[key]
            if agg_method == "sum":
                agg_vals = [round(x + y, 2) for x, y in zip(vals_land, vals_air)]
            elif agg_method == "mean":
                agg_vals = [round((x + y)/2, 2) for x, y in zip(vals_land, vals_air)]
            else:
                raise ValueError("agg_method must be 'sum' or 'mean'")
            records[key] = agg_vals
        else:
            records[key] = vals_air
    # 导出合并结果
    out_rows = []
    for key, vals in records.items():
        # 找原始模型名字（land优先）
        modname = ''
        modsize = ''
        for df in [df_land, df_air]:
            match = df[
                (df['Difficulty']==key[0]) &
                (df['Models_norm']==key[1]) &
                (df['Size']==key[2])
            ]
            if not match.empty:
                modname = match.iloc[0]['Models']
                modsize = match.iloc[0]['Size']
                break
        out_rows.append([key[0], modname, modsize] + vals)
    df_out = pd.DataFrame(out_rows, columns=['Difficulty','Models','Size']+val_cols)

    # ===== 关键修改：所有数值列保留两位小数，且以字符串写入csv =====
    for c in val_cols:
        df_out[c] = df_out[c].apply(lambda x: f"{float(x):.2f}" if x != '' else '')

    df_out.to_csv(output_csv, index=False)
    return df_out

def df_to_html_tbody(df):
    html = ''
    prev_difficulty = None
    for idx, row in df.iterrows():
        cells = ''
        # 合并单元格
        if row['Difficulty'] != prev_difficulty:
            rowspan = (df['Difficulty'] == row['Difficulty']).sum()
            cells += f'<td rowspan="{rowspan}" style="vertical-align: middle;">{row["Difficulty"]}</td>'
            prev_difficulty = row['Difficulty']
        cells += f'<td>{row["Models"]}</td><td>{row["Size"]}</td>'
        for c in df.columns[3:]:
            val = row[c]
            cells += f'<td>{val}</td>'
        html += f'<tr>{cells}</tr>\n'
    return html

if __name__ == "__main__":
    # 步骤1: HTML -> CSV
    html_tbody_to_csv('land_space_tbody.html', 'land_space.csv')
    html_tbody_to_csv('air_space_tbody.html', 'air_space.csv')
    # 步骤2: 合并CSV
    AGG_METHOD = "mean"  # 或 "sum"
    merged_df = merge_csv_and_agg('land_space.csv', 'air_space.csv', 'open_space.csv', agg_method=AGG_METHOD)
    # 步骤3: 输出HTML
    html_out = df_to_html_tbody(merged_df)
    with open('open_space_tbody.html', 'w', encoding='utf-8') as f:
        f.write(html_out)
    print("已生成 open_space_tbody.html")
