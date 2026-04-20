import streamlit as st
import pandas as pd
from data import (
    load_device_data, SPECIAL_RULES_MAP, get_rule_key,
    RULE_SPEECH_STD, RULE_VISION_STD, RULE_HEARING_STD
)

st.set_page_config(page_title="輔助器具補助查詢系統", layout="wide")

df = load_device_data()

if df is None:
    st.error("❌ 無法載入輔具資料庫，請檢查檔案。")
else:
    st.title("📂 輔助器具補助判定系統")
    
    with st.sidebar:
        st.header("🔍 檢索輔具")
        search_query = st.text_input("輸入項次或輔具名稱", placeholder="例如: 170 或 輪椅")

    if search_query:
        # 雙軌搜尋：支援名稱與項次
        mask = (df['項次'].astype(str).str.contains(search_query)) | (df['名稱'].str.contains(search_query))
        res = df[mask]
        
        if not res.empty:
            sel_idx = st.selectbox("確認查詢品項", res.index, 
                                   format_func=lambda i: f"項次 {res.loc[i, '項次']}: {res.loc[i, '名稱']}")
            item = res.loc[sel_idx]
            
            st.divider()
            c1, c2 = st.columns([1, 1])

            with c1:
                st.subheader("📋 輔具基準資訊")
                st.info(f"**【品項名稱】**：{item['名稱']}")
                st.write(f"💰 **最高補助金額**：{item['最高補助金額']}")
                st.write(f"⏳ **最低使用年限**：{item['最低使用年限']} 年")
                st.write(f"🏥 **評估地點**：{item['評估地點']}")
                st.write(f"👤 **評估人員類別**：{item['評估類別']}")
                if item['備註']:
                    st.warning(f"💡 **備註說明**：\n\n{item['備註']}")

            with c2:
                st.subheader("🧪 資格判定流程")
                u_icf_raw = st.text_input("1. 輸入鑑定 ICF 代碼 (逗號隔開)", placeholder="例如: b117, b110.4")
                u_icd_raw = st.text_input("2. 輸入 ICD 診斷碼", placeholder="例如: F03")
                
                if st.button("執行自動判定", type="primary"):
                    u_icfs = [x.strip().lower() for x in u_icf_raw.split(",")]
                    u_icd = u_icd_raw.strip().upper()
                    
                    is_match = False
                    reason = ""
                    
                    # --- 判定次序 1: 16 大類專屬規則 ---
                    rule_key = get_rule_key(item['項次'])
                    if rule_key:
                        rule = SPECIAL_RULES_MAP[rule_key]
                        
                        # 關卡 A: 滿足此項即可補助
                        hits = [i for i in u_icfs if i in [c.lower() for c in rule["direct"]]]
                        if hits:
                            is_match = True
                            reason = f"符合『滿足此項即可補助』(命中: {', '.join(hits)})"
                        
                        # 關卡 B: 隔離組合 (1) -> (2) -> (3)
                        if not is_match:
                            for idx, g in enumerate(rule["groups"], 1):
                                # 嚴格隔離：必須在同一個 group 內 ICF 與 ICD 同時成立
                                icf_match = any(i in u_icfs for i in [c.lower() for c in g["icf"]])
                                icd_match = u_icd in [c.upper() for c in g["icd"]]
                                if icf_match and icd_match:
                                    is_match = True
                                    g_name = g.get("name", f"組合({idx})")
                                    reason = f"符合『{g_name}』判定標準"
                                    break
                    
                    # --- 判定次序 2: 通用標準 (視、聽、語障) ---
                    if not is_match:
                        for r in [RULE_SPEECH_STD, RULE_VISION_STD, RULE_HEARING_STD]:
                            if any(i in u_icfs for i in [c.lower() for c in r["icf"]]):
                                is_match = True
                                reason = f"符合 {r['cat']} 通用判定標準"
                                break

                    # --- 輸出判定結果 ---
                    if is_match:
                        st.success(f"🎯 **判定結果：符合補助條件**\n\n判定依據：{reason}")
                    else:
                        st.error("❌ **判定結果：不符合補助條件**")
        else:
            st.warning("查無品項，請更換關鍵字。")
