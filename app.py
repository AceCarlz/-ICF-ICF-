import streamlit as st
from data import DEVICES, DEMENTIA_ICD

st.set_page_config(page_title="輔具審查助手 V3", layout="wide")

st.title("♿ 輔具費用補助判定系統 (2026 完整版)")
st.markdown("---")

# 介面佈局
col_in, col_res = st.columns([4, 6], gap="large")

with col_in:
    st.subheader("📥 資料輸入")
    item_id = st.selectbox("1. 選擇項次編號", options=list(DEVICES.keys()), 
                          format_func=lambda x: f"項次 {x}: {DEVICES[x]['name']}")
    
    dev = DEVICES[item_id]
    
    # 針對您發現的跨項區域顯示警告
    item_num = int(item_id)
    if (154 <= item_num <= 162) or (14 <= item_num <= 15) or (164 <= item_num <= 168):
        st.warning(f"⚠️ 跨項規定提醒：項次 {item_id} 若為失智症，必須嚴格檢查 ICD 代碼。")

    icf_raw = st.text_input("2. 輸入病人 ICF 代碼 (逗號隔開)", placeholder="如: b117, 10")
    icd_raw = st.text_input("3. 輸入診斷 ICD 代碼 (失智症必填)", placeholder="如: F03")
    
    check_btn = st.button("啟動判定分析", type="primary")

with col_res:
    st.subheader("🔍 判定報告")
    if check_btn:
        if not icf_raw:
            st.error("請輸入 ICF 代碼。")
        else:
            u_icfs = [x.strip().lower() for x in icf_raw.split(",")]
            u_icd = icd_raw.strip().upper()
            
            is_ok = False
            match_cat = ""
            
            for rule in dev["rules"]:
                # 檢查 ICF
                if any(code in u_icfs for code in rule["icf"]):
                    # 檢查交集邏輯
                    if rule.get("and_icd"):
                        if u_icd in DEMENTIA_ICD:
                            is_ok = True
                            match_cat = rule["cat"]
                            break
                        else:
                            st.error(f"❌ 診斷不符：ICF 符合 {rule['cat']}，但 ICD {u_icd} 不在補助名單內。")
                            st.stop()
                    else:
                        is_ok = True
                        match_cat = rule["cat"]
                        break
            
            if is_ok:
                st.success(f"✅ **判定結果：符合資格** ({match_cat})")
                st.markdown(f"""
                ---
                **📋 審核重點：**
                * **評估人員級別：** {dev['eval']}
                * **開立處所限制：** {'🚨 **限由輔具中心開立報告**' if dev['center_only'] else '✅ 醫院或輔具中心均可'}
                """)
            else:
                st.error("❌ **判定結果：不符合資格** (ICF 代碼未命中規則)")

st.sidebar.markdown("""
### 系統資訊
- **資料庫範圍：** 涵蓋 1-172 項次
- **邏輯檢核：** 包含跨項次合併規定
- **更新日期：** 2026-04-10
""")