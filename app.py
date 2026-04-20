import streamlit as st
import pandas as pd
from data import (
    load_device_data, SPECIAL_RULES_MAP, get_rule_key,
    RULE_SPEECH_STD, RULE_VISION_STD, RULE_HEARING_STD
)

st.set_page_config(page_title="輔具補助智慧查詢系統", layout="wide")

# 讀取 CSV
df = load_device_data()

if df is None:
    st.error("❌ 讀取 CSV 失敗，請確認 assistive_devices.csv 是否已上傳。")
else:
    st.title("📂 輔具補助全功能查詢系統")
    
    with st.sidebar:
        st.header("🔍 查詢與檢索")
        # 支援雙軌搜尋：輸入項次數字 或 中文名稱
        search_query = st.text_input("輸入『項次』或『輔具名稱』", placeholder="例如: 170 或 輪椅")

    if search_query:
        # --- 雙軌搜尋邏輯 ---
        # 將項次與名稱都轉為字串並搜尋關鍵字
        mask = (
            df['項次'].astype(str).str.contains(search_query, case=False, na=False) | 
            df['名稱'].astype(str).str.contains(search_query, case=False, na=False)
        )
        res = df[mask]
        
        if not res.empty:
            # 下拉選單顯示「項次 + 名稱」，讓使用者更直覺
            # format_func 確保選單內看到的是 "項次 XX: 名稱"
            selected_item_str = st.selectbox(
                "請選擇具體輔具項目：",
                options=res.index,
                format_func=lambda i: f"項次 {res.loc[i, '項次']}: {res.loc[i, '名稱']}"
            )
            
            # 取得選定項次的整列資料
            item = res.loc[selected_item_str]
            
            st.divider()
            col1, col2 = st.columns([1, 1])

            # --- 左側：完整資訊呈現 (絕不刪減) ---
            with col1:
                st.subheader("📋 補助基準詳細資訊")
                st.info(f"**【輔具品項名稱】**：{item['名稱']}")
                
                # 建立資訊表單
                st.markdown(f"""
                * 💰 **最高補助金額**：{item['最高補助金額']}
                * ⏳ **最低使用年限**：{item['最低使用年限']} 年
                * 🏥 **評估地點**：{item['評估地點']}
                * 👤 **評估人員類別**：{item['評估類別']}
                """)
                
                if item['備註']:
                    st.warning(f"💡 **備註說明**：\n\n{item['備註']}")

            # --- 右側：資格符合判定 (隔離儲存格邏輯) ---
            with col2:
                st.subheader("🧪 資格符合自動判定")
                u_icf_raw = st.text_input("1. 輸入鑑定 ICF 代碼 (多個請用逗號隔開)", placeholder="例如: b117, b110.4")
                u_icd_raw = st.text_input("2. 輸入 ICD 診斷碼", placeholder="例如: F03")
                
                if st.button("執行自動判定", type="primary"):
                    u_icfs = [x.strip().lower() for x in u_icf_raw.split(",")]
                    u_icd = u_icd_raw.strip().upper()
                    
                    is_match = False
                    reason = ""
                    
                    # 抓取 data.py 中的規則地圖
                    rule_key = get_rule_key(item['項次'])
                    
                    if rule_key and rule_key in SPECIAL_RULES_MAP:
                        rule = SPECIAL_RULES_MAP[rule_key]
                        
                        # A. 優先權 1：滿足此項即可補助 (Direct)
                        hits = [i for i in u_icfs if i in [c.lower() for c in rule["direct"]]]
                        if hits:
                            is_match = True
                            reason = f"🎯 符合『直接補助』標準 (命中代碼: {', '.join(hits)})"
                        
                        # B. 優先權 2：隔離儲存格組合判定 (Groups)
                        if not is_match:
                            for g in rule["groups"]:
                                # 嚴格限制：ICF 與 ICD 必須在同一個組合內同時成立
                                icf_ok = any(i in u_icfs for i in [c.lower() for c in g["icf"]])
                                icd_ok = u_icd in [c.upper() for c in g["icd"]]
                                if icf_ok and icd_ok:
                                    is_match = True
                                    group_name = g.get("name", "儲存格組合")
                                    reason = f"✅ 符合 {group_name} 判定標準 (ICF與ICD匹配成功)"
                                    break

                    # C. 優先權 3：通用類別規則 (視聽語障)
                    if not is_match:
                        for r in [RULE_SPEECH_STD, RULE_VISION_STD, RULE_HEARING_STD]:
                            if any(i in u_icfs for i in [c.lower() for c in r["icf"]]):
                                is_match = True
                                reason = f"符合 {r['cat']} 通用判定標準"
                                break

                    # 判定結果呈現
                    if is_match:
                        st.success(f"🎯 **判定結果：符合補助資格**\n\n判定依據：{reason}")
                    else:
                        st.error("❌ **判定結果：不符合資格**\n\n原因：鑑定代碼未命中該項次之法定補助組合。")
        else:
            st.warning("查無符合的項次或輔具名稱，請重新輸入關鍵字。")
