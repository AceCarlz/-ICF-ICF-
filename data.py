import pandas as pd

# 第一類失智症專用 ICD 代碼清單 (保留原本邏輯)
DEMENTIA_ICD = [
    "290.0", "290.10", "290.11", "290.12", "290.13", "290.20", "290.21", "290.3", 
    "290.40", "290.41", "290.42", "290.43", "290.8", "290.9", "294.0", "294.10", "294.11", 
    "331.0", "331.1", "F01.50", "F01.51", "F02.80", "F02.81", "F03", "F03.9", "F03.90", 
    "F03.91", "F04", "F05", "G30.0", "G30.1", "G30.8", "G30.9", "G31.0", "G31.09"
]

def load_device_data():
    """從 CSV 讀取輔具資料庫"""
    try:
        # 讀取 CSV，確保項次是字串以防搜尋出錯
        df = pd.read_csv('assistive_devices.csv', dtype={'項次': str})
        # 將缺失值 (NaN) 替換為空字串，避免顯示出錯
        df = df.fillna("")
        return df
    except FileNotFoundError:
        return None

# 原本的判定規則邏輯 (保留給 app.py 使用)
RULE_DEMENTIA_STD = {"cat": "第一類(失智症)", "icf": ["b117", "b122", "b140", "b144", "b147", "b152", "b160", "b164", "10"], "and_icd": True}
RULE_PHYSICAL_STD = {"cat": "第七類", "icf": ["b710a", "b710b", "b730a", "b730b", "b735", "b765", "s730", "s750", "s760", "05"]}
