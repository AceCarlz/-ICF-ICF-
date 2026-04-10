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

# 1-3. 推車
for i in range(1, 4):
    DEVICES[str(i)] = {"name": f"推車項次 {i}", "eval": "甲類", "center_only": False, "rules": [RULE_PHYSICAL_STD]}

# 4-9. 輪椅及其功能 (含 6 為 ◇)
for i in range(4, 10):
    DEVICES[str(i)] = {"name": f"輪椅及功能項次 {i}", "eval": "甲類 (4&5免評)", "center_only": (i == 6), "rules": [RULE_DEMENTIA_STD, RULE_PHYSICAL_STD]}

# 13. 輪椅配件 (單獨項次，規則已包含失智與肢障)
DEVICES["13"] = {"name": "輪椅配件-後推式動力套件", "eval": "甲類", "center_only": False, "rules": [RULE_DEMENTIA_STD, RULE_PHYSICAL_STD]}

# 42-48. 個人行動輔具 (切割點 1)
for i in range(42, 49):
    DEVICES[str(i)] = {"name": f"個人行動輔具項次 {i}", "eval": "甲類，42.44.45免評", "center_only": False, "rules": [RULE_DEMENTIA_STD, RULE_PHYSICAL_STD]}

# 49-51. 個人行動輔具 (切割點 2)
for i in range(49, 52):
    DEVICES[str(i)] = {"name": f"個人行動輔具項次 {i}", "eval": "甲、丁類", "center_only": False, "rules": [RULE_DEMENTIA_STD, RULE_PHYSICAL_STD]}

# 52-54. 個人行動輔具 (切割點 3)
for i in range(52, 55):
    DEVICES[str(i)] = {"name": f"個人行動輔具項次 {i}", "eval": "甲、丁類", "center_only": False, "rules": [RULE_DEMENTIA_STD, RULE_PHYSICAL_STD]}

# 55-57. 個人行動輔具 (切割點 4)
for i in range(55, 58):
    DEVICES[str(i)] = {"name": f"個人行動輔具項次 {i}", "eval": "甲、丁類，項次57免評", "center_only": False, "rules": [RULE_DEMENTIA_STD, RULE_PHYSICAL_STD]}

# 91. 個人衛星定位器
DEVICES["91"] = {"name": "個人衛星定位器", "eval": "甲、丁類", "center_only": False, "rules": [RULE_DEMENTIA_STD]}

# 94-100. 溝通及資訊輔具 (乙類)
for i in range(94, 101):
    DEVICES[str(i)] = {"name": f"溝通及資訊輔具項次 {i}", "eval": "乙類", "center_only": False, "rules": [{"cat": "第一/三/七類", "icf": ["b117", "b147", "b310", "b730", "01", "04", "05"]}]}

# 110-113. 訓練輔具 (甲類)
for i in range(110, 114):
    DEVICES[str(i)] = {"name": f"訓練輔具項次 {i}", "eval": "甲類", "center_only": False, "rules": [RULE_DEMENTIA_STD, RULE_PHYSICAL_STD, RULE_SPEECH_STD]}

# 135-153. 住家家具及改裝組件 (甲、丁、戊類)
for i in range(135, 154):
    DEVICES[str(i)] = {"name": f"住家家具及改裝組件項次 {i}", "eval": "甲、丁、戊類", "center_only": False, "rules": [RULE_PHYSICAL_STD]}

# 154-162. 住家家具及改裝組件 (甲、丁、戊類)
for i in range(154, 163):
    DEVICES[str(i)] = {"name": f"住家家具及改裝組件項次 {i}", "eval": "甲、丁、戊類", "center_only": False, "rules": [RULE_DEMENTIA_STD, RULE_PHYSICAL_STD]}

# 163-164. 清洗槽與氣墊座
DEVICES["163"] = {"name": "移動式身體清洗槽-局部型", "eval": "甲、丁類", "center_only": False, "rules": [RULE_DEMENTIA_STD]}
DEVICES["164"] = {"name": "移動式身體清洗槽-全身型", "eval": "甲、丁類", "center_only": False, "rules": [RULE_DEMENTIA_STD, RULE_PHYSICAL_STD]}

# 165-172. 移位/沐浴輔具 (已修正：醫院、中心均可)
for i in range(165, 173):
    DEVICES[str(i)] = {"name": f"個人照顧及保護輔具項次 {i}", "eval": "免評，項次170-172必甲類評", "center_only": False, "rules": [RULE_DEMENTIA_STD, RULE_PHYSICAL_STD]}
