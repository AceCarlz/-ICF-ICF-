import streamlit as st
import pandas as pd
from data import (
    load_device_data, DEMENTIA_ICD, INTELLECTUAL_ICD,
    SPECIAL_RULES_MAP, get_rule_key,
    RULE_SPEECH_STD, RULE_VISION_STD, RULE_HEARING_STD
)

st.set_page_config(page_title="輔具補助智慧查詢系統", layout="wide")

# 1. 介面呈現
df = load_device_data()

if df is None:
    st.error("❌ 找不到 assistive_devices.csv，請確認檔案已上傳至 GitHub。")
else:
    st.title("📂 輔具補助全功能查詢系統")
    
    with st.sidebar:
        st.header("🔍 搜尋")
        search_query = st.text_input("輸入項次或名稱 (如: 13, 170, 輪椅)", "")

    if search_query:
        mask = df['項次'].str.contains(search_query) | df['名稱'].str.contains(search_query)
        filtered_df = df[mask]
        
        if not filtered_df.empty:
            selected_id = st.selectbox("請確認項次", options=filtered_df['項次'].tolist(),
                                       format_func=lambda x: f"項次 {x}: {filtered_df[filtered_df['項次']==x]['名稱'].values[0]}")
            
            item = filtered_df[filtered_df['項次'] == selected_id].iloc[0]
            
            st.divider()
            c1, c2 = st.columns([1, 1])

            with c1:
                st.info(f"### 📋 基準資訊\n"
                        f"* **項次名稱：** {item['名稱']}\n"
                        f"* **最高補助：** ${int(item['最高補助金額']):,}\n"
                        f"* **最低年限：** {item['最低使用年限']} 年\n"
                        f"* **評估地點：** {item['評估地點']}\n"
                        f"* **原表類別：** {item['評估類別']}")
                if item['備註']:
                    st.warning(f"💡 **備註：** {item['備註']}")

            with c2:
                st.subheader("🧪 資格試算")
                u_icf = st.text_input("1. 輸入 ICF 代碼 (多個請用逗號隔開)", placeholder="b117, b110.4")
                u_icd = st.text_input("2. 輸入 ICD 診斷碼 (第一類必填)", placeholder="F03, F70")
                
                if st.button("執行判定", type="primary"):
                    u_icfs = [x.strip().lower() for x in u_icf.split(",")]
                    u_icd_clean = u_icd.strip().upper()
                    
                    # --- 核心判定邏輯開始 ---
                    match = False
                    match_reason = ""
                    
                    # A. 優先檢查 SPECIAL_RULES_MAP (16大類特殊項次)
                    rule_key = get_rule_key(item['項次'])
                    if rule_key:
                        rule_detail = SPECIAL_RULES_MAP[rule_key]
                        # 1. 檢查單獨命中 (direct)
                        direct_hits = [i for i in u_icfs if i in [c.lower() for c in rule_detail["direct"]]]
                        if direct_hits:
                            match = True
                            match_reason = f"符合單獨補助代碼: {', '.join(direct_hits)}"
                        
                        # 2. 檢查交叉命中 (pairs)
                        if not match:
                            for p in rule_detail["pairs"]:
                                icf_match = any(i in u_icfs for i in [c.lower() for c in p["icf"]])
                                icd_match = u_icd_clean in [c.upper() for c in p["icd"]]
                                if icf_match and icd_match:
                                    match = True
                                    match_reason = "符合 ICF + ICD 交叉補助標準"
                                    break
                    
                    # B. 如果沒有特殊規則，檢查通用規則 (視聽語障)
                    if not match:
                        for r in [RULE_SPEECH_STD, RULE_VISION_STD, RULE_HEARING_STD]:
                            if any(i in u_icfs for i in [c.lower() for c in r["icf"]]):
                                match = True
                                match_reason = f"符合 {r['cat']} 標準"
                                break

                    # C. 預設第七類 (肢障) 通用判定 (如果都沒有命中)
                    if not match:
                        physical_icfs = ["b710a", "b710b", "b730a", "b730b", "b735", "b765", "s730", "s750", "s760", "05"]
                        if any(i in u_icfs for i in physical_icfs):
                            match = True
                            match_reason = "符合 第七類(肢障) 標準"

                    # 顯示結果
                    if match:
                        st.success(f"🎯 **判定符合**\n\n原因：{match_reason}")
                    else:
                        st.error("❌ **判定不符合**\n\n鑑定代碼未符合該項次之補助標準。")
        else:
            st.warning("查無此項次內容。")
