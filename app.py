import streamlit as st
import pandas as pd
from data import (
    load_device_data, SPECIAL_RULES_MAP, get_rule_key,
    RULE_SPEECH_STD, RULE_VISION_STD, RULE_HEARING_STD
)

st.set_page_config(page_title="輔具補助智慧查詢系統", layout="wide")

df = load_device_data()

if df is None:
    st.error("❌ 讀取 CSV 失敗，請確認檔案已上傳至 GitHub 並命名正確。")
else:
    st.title("📂 輔具補助全功能查詢系統")
    
    with st.sidebar:
        st.header("🔍 快速搜尋")
        search_query = st.text_input("輸入項次或關鍵字", "")

    if search_query:
        mask = df['項次'].str.contains(search_query) | df['名稱'].str.contains(search_query)
        res = df[mask]
        
        if not res.empty:
            sel_id = st.selectbox("確認項次", res['項次'].tolist())
            item = res[res['項次'] == sel_id].iloc[0]
            
            st.divider()
            col1, col2 = st.columns([1, 1])

            with col1:
                st.subheader("📋 補助基準資訊")
                # 這裡嚴格保留所有原始欄位
                st.info(f"**【輔具名稱】**：{item['名稱']}")
                st.write(f"💰 **最高補助金額**：{item['最高補助金額']}")
                st.write(f"⏳ **最低使用年限**：{item['最低使用年限']} 年")
                st.write(f"🏥 **評估地點**：{item['評估地點']}")
                st.write(f"👤 **評估人員類別**：{item['評估類別']}")
                if item['備註']:
                    st.warning(f"💡 **備註說明**：\n\n{item['備註']}")

            with col2:
                st.subheader("🧪 資格符合判定")
                u_icf_raw = st.text_input("1. 輸入 ICF 代碼 (逗號隔開)", placeholder="b117, b110.4")
                u_icd_raw = st.text_input("2. 輸入 ICD 診斷碼", placeholder="F03")
                
                if st.button("執行自動判定", type="primary"):
                    u_icfs = [x.strip().lower() for x in u_icf_raw.split(",")]
                    u_icd = u_icd_raw.strip().upper()
                    
                    is_match = False
                    reason = ""
                    
                    rule_key = get_rule_key(item['項次'])
                    if rule_key:
                        rule = SPECIAL_RULES_MAP[rule_key]
                        
                        # A. 優先檢查：滿足此項即可補助 (Direct)
                        hits = [i for i in u_icfs if i in [c.lower() for c in rule["direct"]]]
                        if hits:
                            is_match = True
                            reason = f"符合『直接補助』標準 (命中: {', '.join(hits)})"
                        
                        # B. 若未中，檢查隔離儲存格組合 (Groups/Pairs)
                        if not is_match:
                            for g in rule["groups"]:
                                icf_ok = any(i in u_icfs for i in [c.lower() for c in g["icf"]])
                                icd_ok = u_icd in [c.upper() for c in g["icd"]]
                                if icf_ok and icd_ok:
                                    is_match = True
                                    grp_name = g.get("name", "交叉比對")
                                    reason = f"符合 {grp_name} 組合判定標準"
                                    break

                    # C. 通用規則
                    if not is_match:
                        for r in [RULE_SPEECH_STD, RULE_VISION_STD, RULE_HEARING_STD]:
                            if any(i in u_icfs for i in [c.lower() for c in r["icf"]]):
                                is_match = True
                                reason = f"符合 {r['cat']} 通用標準"
                                break

                    # 判定顯示
                    if is_match:
                        st.success(f"🎯 **判定符合**\n\n依據：{reason}")
                    else:
                        st.error("❌ **判定不符合**")
        else:
            st.warning("查無資料。")
