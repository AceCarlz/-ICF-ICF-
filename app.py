import streamlit as st
import pandas as pd
from data import (
    load_device_data, DEMENTIA_ICD, INTELLECTUAL_ICD,
    SPECIAL_RULES_MAP, get_rule_key,
    RULE_SPEECH_STD, RULE_VISION_STD, RULE_HEARING_STD
)

st.set_page_config(page_title="輔具補助智慧查詢系統", layout="wide")

# 讀取資料庫
df = load_device_data()

if df is None:
    st.error("❌ 找不到資料庫檔案，請確認 assistive_devices.csv 是否在正確位置。")
else:
    st.title("📂 輔具補助全功能查詢系統")
    
    # 側邊欄搜尋
    with st.sidebar:
        st.header("🔍 搜尋條件")
        search_query = st.text_input("輸入項次或名稱 (如: 13, 170, 輪椅)", "")

    if search_query:
        # 搜尋邏輯
        mask = df['項次'].str.contains(search_query) | df['名稱'].str.contains(search_query)
        filtered_df = df[mask]
        
        if not filtered_df.empty:
            # 下拉選單確認具體項次
            selected_id = st.selectbox(
                "請確認欲查詢的項次：一般戶補助50%、中低收入戶補助75%、低收入戶補助100%", 
                options=filtered_df['項次'].tolist(),
                format_func=lambda x: f"項次 {x}: {filtered_df[filtered_df['項次']==x]['名稱'].values[0]}"
            )
            
            # 取得選定項次的詳細資料
            item = filtered_df[filtered_df['項次'] == selected_id].iloc[0]
            
            st.divider()
            
            # 建立兩欄式介面
            col1, col2 = st.columns([1, 1])

            # --- 左側：還原詳細資訊介面 ---
            with col1:
                st.subheader("📋 補助基準詳情")
                st.info(f"**【項次名稱】**：{item['名稱']}")
                
                # 詳細欄位清單
                st.write(f"💰 **最高補助金額**：${int(float(item['最高補助金額'])):,}")
                st.write(f"⏳ **最低使用年限**：{item['最低使用年限']} 年")
                st.write(f"🏥 **評估地點**：{item['評估地點']}")
                st.write(f"👤 **評估人員類別**：{item['評估類別']}")
                
                if item['備註']:
                    st.warning(f"💡 **備註說明**：\n\n{item['備註']}")

            # --- 右側：資格試算判定 ---
            with col2:
                st.subheader("🧪 資格符合判定")
                u_icf = st.text_input("1. 輸入鑑定 ICF 代碼 (多個請用逗號隔開)", placeholder="例如: b117, b110.4")
                u_icd = st.text_input("2. 輸入 ICD 診斷碼 (第一類必填)", placeholder="例如: F03, F70")
                
                if st.button("執行自動判定", type="primary"):
                    # 格式清理
                    u_icfs = [x.strip().lower() for x in u_icf.split(",")]
                    u_icd_clean = u_icd.strip().upper()
                    
                    match = False
                    match_reason = ""
                    
                    # 1. 優先檢查 data.py 中的 16 大類特殊地圖
                    rule_key = get_rule_key(item['項次'])
                    if rule_key:
                        rule_detail = SPECIAL_RULES_MAP[rule_key]
                        
                        # 檢查單獨命中 (direct)
                        direct_hits = [i for i in u_icfs if i in [c.lower() for c in rule_detail["direct"]]]
                        if direct_hits:
                            match = True
                            match_reason = f"符合該項次之『單獨補助代碼』: {', '.join(direct_hits)}"
                        
                        # 檢查交叉命中 (pairs)
                        if not match:
                            for p in rule_detail["pairs"]:
                                icf_match = any(i in u_icfs for i in [c.lower() for c in p["icf"]])
                                icd_match = u_icd_clean in [c.upper() for c in p["icd"]]
                                if icf_match and icd_match:
                                    match = True
                                    match_reason = "符合 ICF 與 ICD 交叉比對判定標準"
                                    break
                    
                    # 2. 通用規則判定 (視、聽、語障)
                    if not match:
                        for r in [RULE_SPEECH_STD, RULE_VISION_STD, RULE_HEARING_STD]:
                            if any(i in u_icfs for i in [c.lower() for c in r["icf"]]):
                                match = True
                                match_reason = f"符合 {r['cat']} 通用判定標準"
                                break

                    # 3. 第七類 (肢障) 預設判定
                    if not match:
                        physical_icfs = ["b710a", "b710b", "b730a", "b730b", "b735", "b765", "s730", "s750", "s760", "05"]
                        if any(i in u_icfs for i in physical_icfs):
                            match = True
                            match_reason = "符合 第七類(肢障) 通用判定標準"

                    # 顯示判定結果
                    if match:
                        st.success(f"🎯 **判定結果：符合補助資格**\n\n判定依據：{match_reason}")
                    else:
                        st.error("❌ **判定結果：不符合資格**\n\n輸入之代碼未命中該項次之法定補助標準。")
        else:
            st.warning("查無相關項次，請重新輸入關鍵字。")
