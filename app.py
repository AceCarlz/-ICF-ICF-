import streamlit as st
import pandas as pd
import data  # 確保與你的 data.py 同目錄

# 1. 頁面配置 (必須放在第一行)
st.set_page_config(page_title="輔助器具補助查詢系統", layout="wide")

# 2. 強制清除快取的函數 (防止轉圈圈)
@st.cache_data(ttl=3600)  # 每小時自動刷新一次
def get_clean_data():
    return data.load_device_data()

df = get_clean_data()

if df is None:
    st.error("❌ 找不到 CSV 檔案，請確認檔案名稱是否為 assistive_devices.csv 並已上傳至 GitHub。")
else:
    st.title("📂 輔助器具補助查詢系統")

    # 搜尋邏輯
    search_query = st.sidebar.text_input("🔍 輸入項次或名稱搜尋", placeholder="例如: 91")

    if search_query:
        # 雙軌搜尋：支援項次(字串)與名稱
        mask = (df['項次'].astype(str).str.contains(search_query)) | (df['名稱'].str.contains(search_query))
        res = df[mask]

        if not res.empty:
            sel_idx = st.selectbox("請選擇品項", res.index, format_func=lambda i: f"{res.loc[i, '項次']} {res.loc[i, '名稱']}")
            item = res.loc[sel_idx]

            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📋 補助基準")
                st.write(f"**金額：** {item['最高補助金額']}")
                st.write(f"**年限：** {item['最低使用年限']}")
                st.write(f"**評估：** {item['評估類別']} / {item['評估地點']}")

            with col2:
                st.subheader("🧪 資格判定")
                u_icf = st.text_input("輸入 ICF (多筆請用逗號)")
                u_icd = st.text_input("輸入 ICD")

                if st.button("執行判定", type="primary"):
                    # --- 核心判定邏輯開始 ---
                    u_icfs = [x.strip().lower() for x in u_icf.split(",") if x.strip()]
                    u_icd_clean = u_icd.strip().upper()
                    
                    is_match = False
                    reason = ""

                    # 1. 抓取 data.py 規則
                    rule_key = data.get_rule_key(item['項次'])
                    
                    if rule_key and rule_key in data.SPECIAL_RULES_MAP:
                        rule = data.SPECIAL_RULES_MAP[rule_key]
                        
                        # A. 滿足此項即可 (Direct)
                        hits = [i for i in u_icfs if i in [c.lower() for c in rule["direct"]]]
                        if hits:
                            is_match = True
                            reason = f"命中直接補助代碼: {', '.join(hits)}"
                        
                        # B. 儲存格隔離組合 (Groups)
                        if not is_match:
                            for g in rule["groups"]:
                                # 嚴格檢查：同一個 {} 裡的 ICF 與 ICD 同時成立
                                icf_match = any(i in u_icfs for i in [c.lower() for c in g["icf"]])
                                icd_match = u_icd_clean in [c.upper() for c in g["icd"]]
                                if icf_match and icd_match:
                                    is_match = True
                                    reason = f"命中組合：{g['name']}"
                                    break
                    
                    # 2. 通用類別
                    if not is_match:
                        for r in [data.RULE_SPEECH_STD, data.RULE_VISION_STD, data.RULE_HEARING_STD]:
                            if any(i in u_icfs for i in [c.lower() for c in r["icf"]]):
                                is_match = True
                                reason = f"命中 {r['cat']} 通用標準"
                                break

                    # 3. 顯示結果
                    if is_match:
                        st.success(f"🎯 符合補助！\n依據：{reason}")
                    else:
                        st.error("❌ 不符合補助條件")
