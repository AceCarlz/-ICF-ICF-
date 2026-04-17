import streamlit as st
import pandas as pd
from data import load_device_data, DEMENTIA_ICD, RULE_DEMENTIA_STD, RULE_PHYSICAL_STD, RULE_SPEECH_STD, RULE_VISION_STD, RULE_HEARING_STD

st.set_page_config(page_title="輔具補助電子查詢系統", layout="wide")

# 讀取資料
df = load_device_data()

if df is None:
    st.error("找不到 assistive_devices.csv 檔案，請確保檔案已上傳至正確目錄。")
else:
    st.title("📂 輔具補助基準與資格判別系統")
    st.caption("查詢項次資訊，並可於下方輸入鑑定代碼進行資格試算")

    # 側邊欄：搜尋功能
    with st.sidebar:
        st.header("🔍 搜尋輔具")
        search_query = st.text_input("請輸入項次 (例如: 6) 或 關鍵字", "")
        
    # 過濾資料
    if search_query:
        result = df[df['項次'].str.contains(search_query) | df['名稱'].str.contains(search_query)]
    else:
        result = pd.DataFrame()

    if not result.empty:
        for index, row in result.iterrows():
            # --- 第一部分：顯示金額與年限 (你要求先看到的資訊) ---
            with st.container():
                st.subheader(f"【項次 {row['項次']}】{row['名稱']}")
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("最高補助金額，中低75%，一般50%", f"${int(row['最高補助金額']):,}" if str(row['最高補助金額']).isdigit() else "依規定")
                with c2:
                    st.metric("最低使用年限", f"{row['最低使用年限']} 年")
                with c3:
                    st.info(f"📍 評估地點：{row['評估地點']}")
                
                if row['備註']:
                    st.warning(f"💡 備註：{row['備註']}")
            
            st.divider()

            # --- 第二部分：手動輸入 ICF/ICD 判別資格 ---
            st.subheader("🧪 資格即時判別")
            st.write("請輸入手冊上的鑑定代碼，系統將比對是否符合該項次之類別標準：")
            
            col_input1, col_input2 = st.columns(2)
            with col_input1:
                user_icf = st.text_input("輸入 ICF 代碼 (例如: b710a)", key=f"icf_{row['項次']}")
            with col_input2:
                user_icd = st.text_input("輸入 ICD 代碼 (例如: F03)", key=f"icd_{row['項次']}")

            # 判定邏輯啟動
            if user_icf:
                # 找出目前項次應該對應哪一條規則
                current_rule = None
                eval_text = str(row['評估類別'])
                
                if "第一類" in eval_text or "失智" in eval_text:
                    current_rule = RULE_DEMENTIA_STD
                elif "第七類" in eval_text or "甲類" in eval_text:
                    current_rule = RULE_PHYSICAL_STD
                elif "第三類" in eval_text:
                    current_rule = RULE_SPEECH_STD
                elif "第二類" in eval_text and "視" in row['名稱']:
                    current_rule = RULE_VISION_STD
                elif "第二類" in eval_text and "聽" in row['名稱']:
                    current_rule = RULE_HEARING_STD

                if current_rule:
                    # 1. ICF 判別
                    icf_match = user_icf.lower() in [i.lower() for i in current_rule['icf']]
                    
                    # 2. ICD 判別 (如果規則要求 ICD)
                    icd_match = True
                    if current_rule.get('and_icd'):
                        icd_match = user_icd.upper() in [i.upper() for i in DEMENTIA_ICD]
                    
                    # 3. 顯示結果
                    if icf_match and icd_match:
                        st.success(f"✅ 判定符合！此人鑑定代碼符合 {current_rule['cat']} 之補助標準。")
                    else:
                        error_msg = "❌ 判定不符合。"
                        if not icf_match:
                            error_msg += f" ICF 代碼 {user_icf} 不在標準清單內。"
                        if not icd_match:
                            error_msg += " ICD 代碼不符合失智症特定清單。"
                        st.error(error_msg)
                    
                    # 顯示標準清單供參考
                    with st.expander("查看此項次之標準對照表"):
                        st.write(f"**符合之 ICF 清單：** {', '.join(current_rule['icf'])}")
                        if current_rule.get('and_icd'):
                            st.write(f"**符合之 ICD 清單：** {', '.join(DEMENTIA_ICD[:10])}...")
                else:
                    st.info("ℹ️ 此項次之評估類別尚未定義自動判別規則，請參考備註說明。")

    elif search_query:
        st.warning("找不到符合的輔具，請嘗試更改關鍵字。")
    else:
        st.info("💡 請在左側搜尋框輸入輔具項次或名稱。")
