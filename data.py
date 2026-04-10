# data.py

# 第一類失智症專用 ICD 代碼清單
DEMENTIA_ICD = [
    "290.0", "290.10", "290.11", "290.12", "290.13", "290.20", "290.21", "290.3", 
    "290.40", "290.41", "290.42", "290.43", "290.8", "290.9", "294.0", "294.10", "294.11", 
    "331.0", "331.1", "F01.50", "F01.51", "F02.80", "F02.81", "F03", "F03.9", "F03.90", 
    "F03.91", "F04", "F05", "G30.0", "G30.1", "G30.8", "G30.9", "G31.0", "G31.09"
]

# 通用規則定義
RULE_DEMENTIA_STD = {"cat": "第一類(失智症)", "icf": ["b117", "b122", "b140", "b144", "b147", "b152", "b160", "b164", "10"], "and_icd": True}
RULE_PHYSICAL_STD = {"cat": "第七類", "icf": ["b710a", "b710b", "b730a", "b730b", "b735", "b765", "s730", "s750", "s760", "05"]}
RULE_SPEECH_STD = {"cat": "第三類(語障)", "icf": ["b310", "b320", "b330", "s320", "04"]}
RULE_VISION_STD = {"cat": "第二類(視障)", "icf": ["b210", "s220", "02"]}

DEVICES = {}

# 批量錄入邏輯 (依據您提供的範圍)
# 3-6, 7-9: 輪椅與附加功能 (甲類)
for i in range(3, 10):
    DEVICES[str(i)] = {"name": f"輪椅相關項次 {i}", "eval": "甲類", "center_only": (i in [6, 10]), "rules": [RULE_DEMENTIA_STD, RULE_PHYSICAL_STD]}

# 13: 輪椅配件
DEVICES["13"] = {"name": "輪椅配件-後推式動力套件", "eval": "甲類", "center_only": False, "rules": [RULE_DEMENTIA_STD]}

# 42-48, 49-51, 52-54, 55-57: 個人行動輔具 (甲類)
for i in range(42, 58):
    DEVICES[str(i)] = {"name": f"個人行動輔具項次 {i}", "eval": "甲類", "center_only": False, "rules": [RULE_PHYSICAL_STD]}

# 91: 個人衛星定位器 (不需評估, 失智症)
DEVICES["91"] = {"name": "個人衛星定位器", "eval": "甲、丁類", "center_only": False, "rules": [RULE_DEMENTIA_STD]}

# 94-100: 溝通及資訊輔具 (乙類)
for i in range(94, 101):
    DEVICES[str(i)] = {"name": f"溝通及資訊輔具項次 {i}", "eval": "乙類", "center_only": False, "rules": [{"cat": "第一/七類", "icf": ["b117", "b147", "b730", "01", "05"]}]}

# 110-113: 身體、肌力及平衡訓練輔具項次 (甲類)
for i in range(110, 114):
    DEVICES[str(i)] = {"name": f"身體、肌力及平衡訓練輔具項次 {i}", "eval": "甲類", "center_only": False, "rules": [RULE_SPEECH_STD]}

# 135-153: 住家家具及改裝組件 (甲類)
for i in range(135, 154):
    DEVICES[str(i)] = {"name": f"住家家具及改裝組件項次 {i}", "eval": "甲、丁、戊類", "center_only": False, "rules": [RULE_PHYSICAL_STD]}

# 154-162: 照顧床與床墊系列 (甲類, 關鍵跨項)
for i in range(154, 163):
    DEVICES[str(i)] = {"name": f"照顧床/墊項次 {i}", "eval": "甲、丁、戊類，163&164僅甲、丁", "center_only": False, "rules": [RULE_DEMENTIA_STD, RULE_PHYSICAL_STD]}

# 163-164: 清洗槽與氣墊座
DEVICES["163"] = {"name": "移動式身體清洗槽", "eval": "不需評估", "center_only": False, "rules": [RULE_DEMENTIA_STD]}
DEVICES["164"] = {"name": "輪椅氣墊座-A款", "eval": "甲類", "center_only": False, "rules": [RULE_DEMENTIA_STD, RULE_PHYSICAL_STD]}

# 165, 166-169, 170-172: 移位機與爬梯機 (甲類)
for i in range(165, 173):
    DEVICES[str(i)] = {"name": f"移位/爬梯項次 {i}", "eval": "甲類", "center_only": (i in [170, 171]), "rules": [RULE_DEMENTIA_STD, RULE_PHYSICAL_STD]}
