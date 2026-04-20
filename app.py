import streamlit as st
from data import (
    load_device_data, SPECIAL_RULES_MAP, get_rule_key,
    RULE_SPEECH_STD, RULE_VISION_STD, RULE_HEARING_STD
)

st.set_page_config(page_title="輔助器具補助查詢系統", layout="wide")

df = load_device_data()

if df is None:
    st.error("❌ 找不到資料庫檔案(assistive_devices.csv)。")
else:
    st.title("📂 輔助器具補助判定系統")
    
    with st.sidebar:
        st.header("🔍 查詢與檢索")
        search_query = st.text_input("輸入項次或輔具名稱", placeholder="例如: 91 或 傳訊輔具")

    if search_query:
        mask = (df['項次'].astype(str).str.contains(search_query)) | (df['名稱'].str.contains(search_query))
        res = df[mask]
        
        if not res.empty:
            sel_idx = st.selectbox("確認查詢品項", res.index, 
                                   format_func=lambda i: f"項次 {res.loc[i, '項次']}: {res.loc[i, '名稱']}")
            item = res.loc[sel_idx]
            
            st.divider()
            c1, c2 = st.columns([1, 1])

            # --- 左側：基準資訊 ---
            with c1:
                st.subheader("📋 補助基準資訊")
                st.info(f"**【品項名稱】**：{item['名稱']}")
                st.write(f"💰 **最高補助金額**：{item['最高補助金額']}")
                st.write(f"⏳ **最低使用年限**：{item['最低使用年限']} 年")
                st.write(f"🏥 **評估地點**：{item['評估地點']}")
                st.write(f"👤 **評估人員類別**：{item['評估類別']}")
                if item['備註']:
                    st.warning(f"💡 **備註說明**：\n\n{item['備註']}")

            # --- 右側：嚴格判定流程 ---
            with c2:
                st.subheader("🧪 資格符合判定")
                u_icf_raw = st.text_input("1. 輸入鑑定 ICF 代碼 (逗號隔開)", placeholder="例如: b110, b117")
                u_icd_raw = st.text_input("2. 輸入 ICD 診斷碼", placeholder="例如: F03")
                
                if st.button("執行自動判定", type="primary"):
                    u_icfs = [x.strip().lower() for x in u_icf_raw.split(",")]
                    u_icd = u_icd_raw.strip().upper()
                    
                    is_match = False
                    reason = ""
                    
                    # 抓取 16 大類規則
                    rule_key = get_rule_key(item['項次'])
                    if rule_key:
                        rule = SPECIAL_RULES_MAP[rule_key]
                        
                        # 關卡 1: 直接命中
                        hits = [i for i in u_icfs if i in [c.lower() for c in rule["direct"]]]
                        if hits:
                            is_match = True
                            reason = f"符合『滿足此項即可補助』(命中代碼: {', '.join(hits)})"
                        
                        # 關卡 2: 隔離組合 (1) -> (2) -> (3)
                        if not is_match:
                            for idx, g in enumerate(rule["groups"], 1):
                                icf_match = any(i in u_icfs for i in [c.lower() for c in g["icf"]])
                                icd_match = u_icd in [c.upper() for c in g["icd"]]
                                if icf_match and icd_match:
                                    is_match = True
                                    reason = f"符合『同時滿足以下ICF、ICD才可補助({idx})』- {g['name']}"
                                    break
                    
                    # 關卡 3: 通用標準
                    if not is_match:
                        for r in [RULE_SPEECH_STD, RULE_VISION_STD, RULE_HEARING_STD]:
                            if any(i in u_icfs for i in [c.lower() for c in r["icf"]]):
                                is_match = True
                                reason = f"符合 {r['cat']} 通用判定標準"
                                break

                    # 輸出
                    if is_match:
                        st.success(f"🎯 **判定符合**\n\n依據：{reason}")
                    else:
                        st.error("❌ **判定不符合補助條件**")
        else:
            st.warning("查無品項。")
