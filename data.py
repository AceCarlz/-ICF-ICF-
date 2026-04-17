import pandas as pd

# 1. 第一類失智症專用 ICD 代碼清單
DEMENTIA_ICD = [
    "290.0", "290.10", "290.11", "290.12", "290.13", "290.20", "290.21", "290.3", 
    "290.40", "290.41", "290.42", "290.43", "290.8", "290.9", "294.0", "294.10", "294.11", 
    "331.0", "331.1", "F01.50", "F01.51", "F02.80", "F02.81", "F03", "F03.9", "F03.90", 
    "F03.91", "F04", "F05", "G30.0", "G30.1", "G30.8", "G30.9", "G31.0", "G31.09"
]

# 2. 各類別判定規則清單
RULE_DEMENTIA_STD = {"cat": "第一類(失智症)", "icf": ["b117", "b122", "b140", "b144", "b147", "b152", "b160", "b164", "10"], "and_icd": True}
RULE_PHYSICAL_STD = {"cat": "第七類(肢障)", "icf": ["b710a", "b710b", "b730a", "b730b", "b735", "b765", "s730", "s750", "s760", "05"], "and_icd": False}
RULE_SPEECH_STD = {"cat": "第三類(語障)", "icf": ["b310", "b320", "b330", "s320", "04"], "and_icd": False}
RULE_VISION_STD = {"cat": "第二類(視障)", "icf": ["b210", "s220", "02"], "and_icd": False}
RULE_HEARING_STD = {"cat": "第二類(聽障)", "icf": ["b230", "03"], "and_icd": False}

# 3. CSV 讀取核心函數
def load_device_data():
    try:
        # 強制讀取項次為字串，避免 6 變成 6.0 導致比對失敗
        df = pd.read_csv('assistive_devices.csv', dtype={'項次': str})
        df = df.fillna("") # 處理 Excel 裡的空格
        return df
    except Exception:
        return None
