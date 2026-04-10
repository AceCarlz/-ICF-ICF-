import streamlit as st
from data import DEVICES, DEMENTIA_ICD

st.set_page_config(page_title="輔具補助智慧查詢系統", layout="wide")

st.title("🔍 輔具費用補助全功能查詢")
st.caption("輸入項次、名稱或關鍵字即可快速鎖定規則")

# --- 搜尋功能區 ---
search_query = st.text_input("搜尋輔具名稱或項次 (例如: 輪椅, 154, 照顧床)", "")

# 根據搜尋關鍵字過濾項次
filtered_items = {
    k: v for k, v in DEVICES.items() 
    if search_query.lower() in v['name'].lower() or search_query in k
}

if not filtered_items:
    st.warning("找不到符合關鍵字的輔具，請重新輸入。")
    st.stop()

# 選擇過濾後的項次
item_id = st.selectbox("請選擇確切輔具項次", options=list(filtered_items.keys()), 
                        format_func=lambda x: f"項次 {x}: {DEVICES[x]['name']}")

dev = DEVICES[item_id]

# --- 判定邏輯區 ---
st.markdown("---")
col_input, col_info = st.columns([1, 1])

with col_info:
    st.info(f"### 📋 基準資訊\n"
            f"* **項次名稱：** {dev['name']}\n"
            f"* **評估級別：** {dev['eval']}\n"
            f"* **評估處所：** {'🚨 限輔具中心' if dev['center_only'] else '✅ 醫院、中心均可'}")

with col_input:
    st.subheader("🧪 資格判定")
    icf_in = st.text_input("1. 輸入 ICF 代碼 (逗號隔開)", placeholder="b117, 10")
    icd_in = st.text_input("2. 輸入 ICD 診斷碼 (失智症才需填寫)", placeholder="F03")
    
    if st.button("執行判定", type="primary"):
        u_icfs = [x.strip().lower() for x in icf_in.split(",")]
        u_icd = icd_raw = icd_in.strip().upper()
        
        match = False
        match_cat = ""
        for r in dev["rules"]:
            if any(i in u_icfs for i in r["icf"]):
                if r.get("and_icd"):
                    if u_icd in DEMENTIA_ICD:
                        match = True; match_cat = r["cat"]; break
                    else:
                        st.error(f"❌ 診斷不符：符合 ICF {r['cat']}，但 ICD {u_icd} 不在失智症補助清單。")
                        st.stop()
                else:
                    match = True; match_cat = r["cat"]; break
        
        if match:
            st.success(f"🎯 **判定符合：{match_cat}**")
        else:
            st.error("❌ **判定不符合：代碼未命中規則**")
