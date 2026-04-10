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
RULE_HEARING_STD = {"cat": "第二類(聽障)", "icf": ["b230", "03"]}

DEVICES = {}

# 自動化函數 (結束項次已含 +1 邏輯，直接輸入正確項次即可)
def add_range(start, end, name_prefix, eval_type, center_only, rules):
    for i in range(start, end + 1):
        # 針對特定項次處理限中心判斷 (如原本的項次 6)
        co = center_only(i) if callable(center_only) else center_only
        DEVICES[str(i)] = {
            "name": f"{name_prefix} (項次 {i})",
            "eval": eval_type,
            "center_only": co,
            "rules": rules
        }

# --- 1-9. 基礎行動輔具 ---
add_range(1, 3, "推車", "甲類", False, [RULE_PHYSICAL_STD])
add_range(4, 9, "輪椅及功能", "甲類 (4&5免評)", lambda i: i == 6, [RULE_DEMENTIA_STD, RULE_PHYSICAL_STD])

# --- 10-41. 個人行動輔具斷點 ---
add_range(10, 12, "個人行動輔具", "甲類", lambda i: i == 10, [RULE_PHYSICAL_STD])
DEVICES["13"] = {"name": "輪椅配件-後推式動力套件 (項次 13)", "eval": "甲類", "center_only": False, "rules": [RULE_DEMENTIA_STD, RULE_PHYSICAL_STD]}
add_range(14, 25, "個人行動輔具-電動輪椅", "甲類", False, [RULE_PHYSICAL_STD])
add_range(26, 29, "擺位系統", "甲類", False, [RULE_PHYSICAL_STD])
add_range(30, 30, "電動代步車", "甲類", False, [RULE_PHYSICAL_STD])
add_range(31, 31, "行動輔具附加功能-完成搭配機動車輛使用之衝擊測試", "甲類", False, [RULE_PHYSICAL_STD])
add_range(32, 41, "個人行動輔具-汽機車改裝", "丁類", False, [RULE_PHYSICAL_STD])

# --- 42-57. 個人行動輔具 (原本的切割點) ---
add_range(42, 48, "個人行動輔具", "甲類，42.44.45免評", False, [RULE_DEMENTIA_STD, RULE_PHYSICAL_STD])
add_range(49, 51, "個人行動輔具", "甲、丁類", False, [RULE_DEMENTIA_STD, RULE_PHYSICAL_STD])
add_range(52, 54, "個人行動輔具", "甲、丁類", False, [RULE_DEMENTIA_STD, RULE_PHYSICAL_STD])
add_range(55, 57, "個人行動輔具", "甲、丁類，項次57免評", False, [RULE_DEMENTIA_STD, RULE_PHYSICAL_STD])

# --- 58-90. 視覺/聽覺/溝通斷點 ---
add_range(58, 62, "視覺相關輔具", "乙類", False, [RULE_VISION_STD])
add_range(63, 63, "特製眼鏡(含特製隱形眼鏡)", "乙類", False, [RULE_VISION_STD])
add_range(64, 64, "角膜疾病類隱形眼鏡", "乙類", False, [RULE_VISION_STD])
add_range(65, 70, "溝通及資訊輔具-視覺相關輔具", "乙類", False, [RULE_VISION_STD])
add_range(71, 76, "溝通及資訊輔具-視覺相關輔具", "乙類", False, [RULE_VISION_STD])
add_range(77, 77, "語音手機-簡易型", "不需評估", False, [RULE_VISION_STD])
add_range(78, 78, "語音手機智慧型或平板", "不需評估", False, [RULE_VISION_STD])
add_range(79, 79, "傳真機", "不需評估", False, [RULE_SPEECH_STD])
add_range(80, 80, "行動手機簡易型", "不需評估", False, [RULE_SPEECH_STD])
add_range(81, 81, "行動手機具雙項即時影像傳輸功能型", "不需評估", False, [RULE_SPEECH_STD])
add_range(82, 85, "溝通及資訊輔具-聽覺相關輔具", "丙類", False, [RULE_HEARING_STD])
add_range(86, 86, "溝通及資訊輔具-視覺相關輔具", "乙類", False, [RULE_VISION_STD])
add_range(87, 90, "溝通及資訊輔具-警示指示及信號輔具", "不需評估", False, [RULE_VISION_STD, RULE_DEMENTIA_STD])

# --- 91-113. 定位/發聲/電腦/血壓計 ---
DEVICES["91"] = {"name": "個人衛星定位器 (項次 91)", "eval": "甲、丁類", "center_only": False, "rules": [RULE_DEMENTIA_STD]}
add_range(92, 92, "溝通及資訊輔具-發聲輔具", "乙類", False, [RULE_SPEECH_STD])
add_range(93, 100, "溝通及資訊輔具-發聲輔具", "乙類", False, [RULE_SPEECH_STD])
add_range(101, 108, "溝通及資訊輔具-電腦輔具", "乙類", False, [RULE_PHYSICAL_STD, RULE_SPEECH_STD])
add_range(109, 109, "語音血壓計", "不需評估", False, [RULE_VISION_STD])
add_range(110, 113, "訓練輔具", "甲類", False, [RULE_DEMENTIA_STD, RULE_PHYSICAL_STD, RULE_SPEECH_STD])

# --- 114-134. 壓瘡/床/改裝相關 ---
add_range(114, 120, "預防壓瘡輔具-座墊", "甲類", False, [RULE_PHYSICAL_STD])
add_range(121, 122, "預防壓瘡輔具-氣墊床", "甲類", False, [RULE_PHYSICAL_STD])
add_range(123, 127, "電動床相關項次", "甲、丁、戊類", False, [RULE_PHYSICAL_STD])
add_range(128, 130, "擺位椅相關", "甲類", False, [RULE_PHYSICAL_STD])
add_range(131, 131, "升降桌", "甲、丁、戊類", False, [RULE_PHYSICAL_STD])
add_range(132, 134, "居改爬梯機相關", "甲類", False, [RULE_PHYSICAL_STD])

# --- 135-172. 舊有項次 (已併入新分類名稱) ---
add_range(135, 153, "住家家具及改裝組件", "甲、丁、戊類", False, [RULE_PHYSICAL_STD])
add_range(154, 162, "住家家具及改裝組件", "甲、丁、戊類", False, [RULE_DEMENTIA_STD, RULE_PHYSICAL_STD])
DEVICES["163"] = {"name": "移動式身體清洗槽-局部型 (項次 163)", "eval": "甲、丁類", "center_only": False, "rules": [RULE_DEMENTIA_STD]}
DEVICES["164"] = {"name": "移動式身體清洗槽-全身型 (項次 164)", "eval": "甲、丁類", "center_only": False, "rules": [RULE_DEMENTIA_STD, RULE_PHYSICAL_STD]}
add_range(165, 172, "個人照顧及保護輔具", "免評，項次170-172必甲類評", False, [RULE_DEMENTIA_STD, RULE_PHYSICAL_STD])

# --- 173-242. 最後補全斷點 ---
add_range(173, 179, "個人照顧及保護輔具", "免評", False, [RULE_PHYSICAL_STD, RULE_DEMENTIA_STD])
add_range(180, 239, "矯具及義具", "丁類", False, [RULE_PHYSICAL_STD])
add_range(240, 242, "人工電子耳相關", "丙類", False, [RULE_HEARING_STD])
