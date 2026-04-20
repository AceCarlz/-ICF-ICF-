import streamlit as st
import pandas as pd
from data import (
    load_device_data, DEMENTIA_ICD, INTELLECTUAL_ICD,
    SPECIAL_RULES_MAP, get_rule_key,
    RULE_SPEECH_STD, RULE_VISION_STD, RULE_HEARING_STD
)

st.set_page_config(page_title="輔具補助智慧查詢系統", layout="wide")

df = load_device_data()

if df is None:
    st.error("❌ 找不到檔案，請確認 CSV 是否上傳。")
else:
    st.title("📂 輔具補助全功能查詢系統")
    search_query = st.sidebar.text_input("輸入項次或名稱", "")

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
                st.info(f"### 📋 基準資訊\n* **名稱：** {item['名稱']}\n* **補助：** ${item['最高補助金額']}\n* **年限：** {item['最低使用年限']} 年")
            
            with c2:
                st.subheader("🧪 資格試算")
                u_icf = st.text_input("輸入 ICF 代碼 (逗號隔開)", placeholder="b117, b110.4")
                u_icd = st.text_input("輸入 ICD 診斷碼", placeholder="F03")
                
                if st.button("執行判定", type="primary"):
                    u_icfs = [x.strip().lower() for x in u_icf.split(",")]
                    u_icd_clean = u_icd.strip().upper()
                    match = False
                    match_reason = ""
                    
                    rule_key = get_rule_key(item['項次'])
                    if rule_key:
                        rule_detail = SPECIAL_RULES_MAP[rule_key]
                        direct_hits = [i for i in u_icfs if i in [c.lower() for c in rule_detail["direct"]]]
                        if direct_hits:
                            match = True
                            match_reason = f"符合單獨補助代碼: {', '.join(direct_hits)}"
                        if not match:
                            for p in rule_detail["pairs"]:
                                if any(i in u_icfs for i in [c.lower() for c in p["icf"]]) and (u_icd_clean in [c.upper() for c in p["icd"]]):
                                    match = True; match_reason = "符合 ICF + ICD 交叉補助標準"; break
                    
                    if not match:
                        for r in [RULE_SPEECH_STD, RULE_VISION_STD, RULE_HEARING_STD]:
                            if any(i in u_icfs for i in [c.lower() for c in r["icf"]]):
                                match = True; match_reason = f"符合 {r['cat']} 標準"; break

                    if match: st.success(f"🎯 **判定符合**\n\n原因：{match_reason}")
                    else: st.error("❌ **判定不符合**")
