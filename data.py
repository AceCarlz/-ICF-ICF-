import pandas as pd

# 1. 第一類失智症專用 ICD 代碼清單 (維持 35 項標準代碼)
DEMENTIA_ICD = [
    "290.0", "290.10", "290.11", "290.12", "290.13", "290.20", "290.21", "290.3", 
    "290.40", "290.41", "290.42", "290.43", "290.8", "290.9", "294.0", "294.10", "294.11", 
    "331.0", "331.1", "F01.50", "F01.51", "F02.80", "F02.81", "F03", "F03.9", "F03.90", 
    "F03.91", "F04", "F05", "G30.0", "G30.1", "G30.8", "G30.9", "G31.0", "G31.09"
]

# 2. 精準判定規則清單
# 這裡定義了每一類身障類別對應的 ICF 基準碼與舊制代碼
RULE_DEMENTIA_STD = {
    "cat": "第一類(失智症)", 
    "icf": ["b117", "b122", "b140", "b144", "b147", "b152", "b160", "b164", "10"], 
    "and_icd": True  # 標記此類別需要額外比對 ICD 診斷碼
}

RULE_PHYSICAL_STD = {
    "cat": "第七類(肢障)", 
    "icf": ["b710a", "b710b", "b730a", "b730b", "b735", "b765", "s730", "s750", "s760", "05"], 
    "and_icd": False
}

RULE_SPEECH_STD = {
    "cat": "第三類(語障)", 
    "icf": ["b310", "b320", "b330", "s320", "04"], 
    "and_icd": False
}

RULE_VISION_STD = {
    "cat": "第二類(視障)", 
    "icf": ["b210", "s220", "02"], 
    "and_icd": False
}

RULE_HEARING_STD = {
    "cat": "第二類(聽障)", 
    "icf": ["b230", "03"], 
    "and_icd": False
}

# 3. CSV 檔案讀取核心函數
def load_device_data():
    """從 CSV 讀取輔具資料庫並進行格式清理"""
    try:
        # 指定 dtype={'項次': str} 避免數字變浮點數 (如 6 變成 6.0)
        df = pd.read_csv('assistive_devices.csv', dtype={'項次': str})
        # 填充空白單元格，防止顯示時出現 "NaN" 字樣
        df = df.fillna("")
        return df
    except Exception as e:
        # 如果發生錯誤，返回 None 讓主程式 app.py 顯示錯誤訊息
        print(f"Error loading CSV: {e}")
        return None
