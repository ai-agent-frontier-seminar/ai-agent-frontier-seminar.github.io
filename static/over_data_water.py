import pandas as pd
from bs4 import BeautifulSoup

def html_tbody_to_csv(html_file, csv_file):
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    rows = []
    difficulty = None
    for tr in soup.find_all('tr'):
        tds = tr.find_all(['td'])
        if not tds:
            continue
        row = []
        # 如果首列是rowspan，更新difficulty
        if tds[0].has_attr('rowspan'):
            difficulty = tds[0].get_text(strip=True)
            tds = tds[1:]
        row.append(difficulty)
        for td in tds:
            text = td.get_text(strip=True)
            text = text.replace('\n', '').replace('\r', '')
            row.append(text)
        rows.append(row)
    # 查最大列数
    max_len = max(len(row) for row in rows)
    # 自动填表头
    header = ['Difficulty', 'Models', 'Size'] + [f'Col{i}' for i in range(1, max_len-3+1)]
    # 补齐行
    with open(csv_file, 'w', encoding='utf-8') as f:
        f.write(','.join(header[:max_len]) + '\n')
        for row in rows:
            row = [str(x) if x is not None else '' for x in row]
            f.write(','.join(row + ['']*(max_len-len(row))) + '\n')

# 运行
html_tbody_to_csv('water_space_tbody.html', 'water_space.csv')

def normalize_model_name(name):
    if not isinstance(name, str): return name
    return name.replace("🥇", "").replace("\u200b", "").strip()

def merge_csv_and_agg(base_csv, new_csv, output_csv, agg_method='sum'):
    df_base = pd.read_csv(base_csv).fillna('')
    df_new = pd.read_csv(new_csv).fillna('')
    # 标准化模型名字
    df_base['Models_norm'] = df_base['Models'].map(normalize_model_name)
    df_new['Models_norm'] = df_new['Models'].map(normalize_model_name)
    key_cols = ['Difficulty', 'Models_norm', 'Size']
    # 自动对齐所有 value 列
    val_cols = [c for c in df_base.columns if c not in ['Difficulty','Models','Models_norm','Size']]
    # 对新数据做同样处理，确保列数相同
    for c in val_cols:
        if c not in df_new.columns:
            df_new[c] = 0.0
    for c in df_new.columns:
        if c not in val_cols and c not in key_cols and c != 'Models':
            df_base[c] = 0.0
            val_cols.append(c)
    # 合并
    records = {}
    for _, row in df_base.iterrows():
        key = (row['Difficulty'], row['Models_norm'], str(row['Size']))
        records[key] = [float(row[c]) if row[c] != '' else 0.0 for c in val_cols]
    for _, row in df_new.iterrows():
        key = (row['Difficulty'], row['Models_norm'], str(row['Size']))
        vals_new = [float(row[c]) if row[c] != '' else 0.0 for c in val_cols]
        if key in records:
            vals_base = records[key]
            if agg_method == "sum":
                agg_vals = [round(x + y, 2) for x, y in zip(vals_base, vals_new)]
            elif agg_method == "mean":
                agg_vals = [round((x + y)/2, 2) for x, y in zip(vals_base, vals_new)]
            else:
                raise ValueError("agg_method must be 'sum' or 'mean'")
            records[key] = agg_vals
        else:
            records[key] = vals_new
    # 输出
    out_rows = []
    for key, vals in records.items():
        modname = ''
        modsize = ''
        for df in [df_base, df_new]:
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
    df_out.to_csv(output_csv, index=False)
    return df_out

# 运行
merge_csv_and_agg('open_space.csv', 'water_space.csv', 'all_space.csv', agg_method='mean')


def df_to_html_tbody(df):
    html = ''
    prev_difficulty = None
    for idx, row in df.iterrows():
        cells = ''
        if row['Difficulty'] != prev_difficulty:
            rowspan = (df['Difficulty'] == row['Difficulty']).sum()
            cells += f'<td rowspan="{rowspan}" style="vertical-align: middle;">{row["Difficulty"]}</td>'
            prev_difficulty = row['Difficulty']
        cells += f'<td>{row["Models"]}</td><td>{row["Size"]}</td>'
        for c in df.columns[3:]:
            val = row[c]
            # 若是数字且为整数，去掉小数点
            try:
                v = float(val)
                if v.is_integer(): val = int(v)
            except: pass
            cells += f'<td>{val}</td>'
        html += f'<tr>{cells}</tr>\n'
    return html

df = pd.read_csv('all_space.csv')
with open('all_space_tbody.html', 'w', encoding='utf-8') as f:
    f.write(df_to_html_tbody(df))
print("已生成 all_space_tbody.html")
