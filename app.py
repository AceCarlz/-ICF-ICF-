import streamlit as st
import pandas as pd
from data import (
    load_device_data, DEMENTIA_ICD, 
    RULE_DEMENTIA_STD, RULE_PHYSICAL_STD, 
    RULE_SPEECH_STD, RULE_VISION_STD, RULE_HEARING_STD
)

st.set_page_config(page_title="輔具補助智慧查詢系統", layout="wide")

# 1. 讀取 CSV 資料
df = load_device_data()

# 定義一個對照表，用來根據 Excel 的評估類別文字，給予對應的鑑定規則清單
# 這樣能確保搜尋到該項次時，背後帶有正確的 ICF/ICD 標準
def get_rules_for_item(category_text, item_name):
    rules = []
    cat_str = str(category_text)
    name_str = str(item_name)
    
    # 精準匹配：根據評估類別或名稱關鍵字分配規則
    if "第一類" in cat_str or "失智" in cat_str:
        rules.append(RULE_DEMENTIA_STD)
    if "第七類" in cat_str or any(kw in cat_str for kw in ["甲類", "乙類", "丁類"]):
        rules.append(RULE_PHYSICAL_STD)
    if "第三類" in cat_str or "語" in name_str:
        rules.append(RULE_SPEECH_STD)
    if "第二類" in cat_str:
        if "視" in name_str or "眼" in name_str or "放大" in name_str:
            rules.append(RULE_VISION_STD)
        if "聽" in name_str or "耳" in name_str:
            rules.append(RULE_HEARING_STD)
    
    # 如果完全沒匹配到，預設給予最通用的第七類標準
    if not rules:
        rules.append(RULE_PHYSICAL_STD)
    return rules

if df is None:
    st.error("找不到 assistive_devices.csv 檔案。")
else:
    st.title("🔍 輔具補助全功能查詢系統")
    st.caption("結合 CSV 資料庫與精準 ICF/ICD 判別邏輯")

    # --- 搜尋功能區 ---
    with st.sidebar:
        search_query = st.text_input("搜尋項次、名稱或關鍵字", "")

    if search_query:
        # 過濾符合的項次
        mask = df['項次'].str.contains(search_query) | df['名稱'].str.contains(search_query)
        filtered_df = df[mask]
    else:
        filtered_df = pd.DataFrame()

    if not filtered_df.empty:
        # 讓使用者選擇確切項次
        options = filtered_df['項次'].tolist()
        selected_id = st.selectbox(
            "請選擇確切輔具項次", 
            options=options,
            format_func=lambda x: f"項次 {x}: {filtered_df[filtered_df['項次']==x]['名稱'].values[0]}"
        )
        
        # 取得該項次的完整資料
        item_data = filtered_df[filtered_df['項次'] == selected_id].iloc[0]
        
        # --- 基準資訊顯示 ---
        st.markdown("---")
        col_info, col_calc = st.columns([1, 1])

        with col_info:
            st.info(f"### 📋 基準資訊\n"
                    f"* **項次名稱：** {item_data['名稱']}\n"
                    f"* **最高補助：** ${int(item_data['最高補助金額']):,}\n"
                    f"* **最低年限：** {item_data['最低使用年限']} 年\n"
                    f"* **評估地點：** {item_data['評估地點']}\n"
                    f"* **評估級別：** {item_data['評估類別']}")
            if item_data['備註']:
                st.warning(f"💡 **備註：** {item_data['備註']}")

        # --- 資格判定區 (回歸原始邏輯) ---
        with col_calc:
            st.subheader("🧪 資格判定")
            icf_in = st.text_input("1. 輸入 ICF 代碼 (多個請用逗號隔開)", placeholder="b710a, s730")
            icd_in = st.text_input("2. 輸入 ICD 診斷碼 (僅第一類失智症需填寫)", placeholder="F03")
            
            if st.button("執行判定", type="primary"):
                # 取得該項次對應的規則清單
                dev_rules = get_rules_for_item(item_data['評估類別'], item_data['名稱'])
                
                u_icfs = [x.strip().lower() for x in icf_in.split(",")]
                u_icd = icd_in.strip().upper()
                
                match = False
                match_cat = ""
                error_detail = ""

                # 遍歷該項次適用的所有規則 (例如失智症輔具會同時跑失智規則與物理規則)
                for r in dev_rules:
                    # 檢查 ICF 是否命中
                    if any(i in u_icfs for i in r["icf"]):
                        # 檢查是否需要 ICD (失智症)
                        if r.get("and_icd"):
                            if u_icd in DEMENTIA_ICD:
                                match = True; match_cat = r["cat"]; break
                            else:
                                error_detail = f"符合 ICF {r['cat']} 標準，但 ICD 代碼 {u_icd} 不在失智症清單內。"
                        else:
                            # 一般類別只要 ICF 命中即可
                            match = True; match_cat = r["cat"]; break
                
                if match:
                    st.success(f"🎯 **判定符合：{match_cat}**")
                elif error_detail:
                    st.error(f"❌ **判定不符合**\n\n{error_detail}")
                else:
                    st.error("❌ **判定不符合：鑑定代碼未命中任何規則清單**")
                    with st.expander("查看應具備之代碼標準"):
                        for r in dev_rules:
                            st.write(f"**{r['cat']}標準：** {', '.join(r['icf'])}")

    elif search_query:
        st.warning("找不到符合的輔具。")
    else:
        st.info("💡 請在側邊欄搜尋框輸入項次或名稱。")
