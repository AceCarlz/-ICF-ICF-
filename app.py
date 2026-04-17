import streamlit as st
from data import load_device_data, DEMENTIA_ICD, RULE_DEMENTIA_STD, RULE_PHYSICAL_STD

st.set_page_config(page_title="輔具補助電子查詢系統", layout="wide")

# 讀取資料
df = load_device_data()

if df is None:
    st.error("找不到 assistive_devices.csv 檔案，請確保檔案已上傳至正確目錄。")
else:
    st.title("📂 輔具補助基準電子查詢系統")
    st.caption("輸入項次或名稱即可快速查詢最高補助額、使用年限與評估規定")

    # 側邊欄：查詢功能
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
            with st.expander(f"【項次 {row['項次']}】{row['名稱']}", expanded=True):
                # 第一排：核心數據
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("最高補助金額", f"${int(row['最高補助金額']):,}" if row['最高補助金額'] != "" else "未定")
                with c2:
                    st.metric("最低使用年限", f"{row['最低使用年限']} 年")
                with c3:
                    st.write(f"🟢 **評估類別**：\n{row['評估類別']}")
                
                st.divider()

                # 第二排：規定與地點
                c4, c5 = st.columns(2)
                with c4:
                    st.info(f"📍 **建議評估地點**：\n{row['評估地點']}")
                with c5:
                    if row['備註']:
                        st.warning(f"💡 **備註說明**：\n{row['備註']}")
                    else:
                        st.write("💡 **備註說明**：無")

                # 特別判定邏輯 (例如失智症)
                if "第一類" in str(row['評估類別']):
                    with st.success("📝 失智症判定提示"):
                        st.write(f"此項次需同時符合 ICF 代碼：`{', '.join(RULE_DEMENTIA_STD['icf'])}`")
                        st.write(f"且 ICD 代碼須為：`{', '.join(DEMENTIA_ICD[:5])}...` (等 35 項)")

    elif search_query:
        st.warning("找不到符合的輔具，請嘗試更改關鍵字。")
    else:
        st.info("💡 請在左側搜尋框輸入輔具項次或名稱開始查詢。")
