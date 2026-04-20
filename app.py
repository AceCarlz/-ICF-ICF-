import streamlit as st
import pandas as pd
from data import (
    load_device_data, DEMENTIA_ICD, 
    RULE_DEMENTIA_STD, RULE_PHYSICAL_STD, 
    RULE_SPEECH_STD, RULE_VISION_STD, RULE_HEARING_STD
)

st.set_page_config(page_title="輔具補助智慧查詢系統", layout="wide")

# 1. 根據項次號碼分配鑑定規則 (此處為系統最核心的精準判斷邏輯)
def get_rules_for_item(item_id, item_name):
    rules = []
    # 將項次轉為整數方便比對區間
    try:
        idx = int(item_id)
    except:
        idx = 0

    # --- 1. 定義第一類(失智症)的項次範圍 ---
    # 包含：後推動力套件(13)、電輪/代步車(14-30)、移位機(55-57)、定位器(91)、爬梯機(132-134)、居改(135-162)等
    if idx == 13 or (14 <= idx <= 30) or (55 <= idx <= 57) or idx == 91 or (132 <= idx <= 162):
        rules.append(RULE_DEMENTIA_STD)

    # --- 2. 定義第七類(肢障)的項次範圍 ---
    # 絕大多數的輔具都適用第七類，這裡我們設為預設，或針對特定範圍
    # 排除掉純視覺、聽覺、語障的項次即可
    if not (63 <= idx <= 81): # 63-81 主要是視障/聽障/語障
        rules.append(RULE_PHYSICAL_STD)

    # --- 3. 定義第三類(語障) ---
    if (78 <= idx <= 81) or "語音" in item_name:
        rules.append(RULE_SPEECH_STD)

    # --- 4. 定義第二類(視/聽障) ---
    if (63 <= idx <= 77) or "視" in item_name or "放大" in item_name:
        rules.append(RULE_VISION_STD)
    if (82 <= idx <= 90) or "聽" in item_name or "助聽器" in item_name:
        rules.append(RULE_HEARING_STD)

    # 確保萬一都沒匹配到，至少給一個第七類
    if not rules:
        rules.append(RULE_PHYSICAL_STD)
        
    return rules

# 2. 介面呈現
df = load_device_data()

if df is None:
    st.error("❌ 找不到 assistive_devices.csv，請確認檔案已上傳至 GitHub 且檔名正確。")
else:
    st.title("📂 輔具補助全功能查詢系統")
    
    with st.sidebar:
        st.header("🔍 搜尋")
        search_query = st.text_input("輸入項次或名稱 (如: 13, 輪椅)", "")

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
                        f"* **類別：** {item['評估類別']}")
                if item['備註']:
                    st.warning(f"💡 **備註：** {item['備註']}")

            with c2:
                st.subheader("🧪 資格試算")
                u_icf = st.text_input("1. 輸入 ICF 代碼 (多個請用逗號隔開)", placeholder="b117, 10")
                u_icd = st.text_input("2. 輸入 ICD 診斷碼 (第一類失智症必填)", placeholder="F03")
                
                if st.button("執行判定", type="primary"):
                    dev_rules = get_rules_for_item(item['項次'], item['名稱'])
                    u_icfs = [x.strip().lower() for x in u_icf.split(",")]
                    u_icd_clean = u_icd.strip().upper()
                    
                    match = False
                    match_cat = ""
                    error_msg = ""

                    for r in dev_rules:
                        # 檢查 ICF 是否命中
                        if any(i in u_icfs for i in [c.lower() for c in r["icf"]]):
                            # 檢查是否需要同時符合 ICD
                            if r.get("and_icd"):
                                if u_icd_clean in [c.upper() for c in DEMENTIA_ICD]:
                                    match = True; match_cat = r["cat"]; break
                                else:
                                    error_msg = f"符合 ICF {r['cat']}，但 ICD 診斷碼不符。"
                            else:
                                match = True; match_cat = r["cat"]; break
                    
                    if match:
                        st.success(f"🎯 **判定符合：{match_cat}**")
                    elif error_msg:
                        st.error(f"❌ **判定不符合**\n\n{error_msg}")
                    else:
                        st.error("❌ **判定不符合：鑑定代碼未符合該項次標準。**")
        else:
            st.warning("查無此項次。")
    else:
        st.info("💡 請在左側搜尋框輸入內容。")
