import streamlit as st
import pandas as pd
from data import (
    load_device_data, SPECIAL_RULES_MAP, get_rule_key,
    RULE_SPEECH_STD, RULE_VISION_STD, RULE_HEARING_STD
)

# 網頁基礎配置
st.set_page_config(page_title="輔助器具補助查詢系統", layout="wide")

# --- 【新增】清除快取與資料讀取機制 ---
@st.cache_data(ttl=600)  # 每 10 分鐘自動重整，防止轉圈圈
def get_cached_data():
    return load_device_data()

df = get_cached_data()

if df is None:
    st.error("❌ 找不到資料庫檔案 (assistive_devices.csv)，請確認檔案路徑與檔名。")
else:
    st.title("📂 輔助器具補助智慧查詢系統")
    st.caption("根據最新 data.py 邏輯執行：滿足此項即可補助 > 組合(1) > 組合(2) > 組合(3) > 通用標準")

    # --- 【側邊欄】搜尋與功能開關 ---
    with st.sidebar:
        st.header("🔍 查詢與檢索")
        search_query = st.text_input("輸入『項次』或『輔具名稱』", placeholder="例如: 91 或 輪椅")
        
        st.divider()
        # 【新增】顯示開關：預設關閉
        show_codes = st.toggle("📂 顯示本項核可代碼 (電話對照用)", value=False)
        
        # 【新增】手動重新整理按鈕 (解決轉圈圈)
        if st.button("🔄 重新整理資料"):
            st.cache_data.clear()
            st.rerun()

    if search_query:
        mask = (
            df['項次'].astype(str).str.contains(search_query, case=False, na=False) | 
            df['名稱'].astype(str).str.contains(search_query, case=False, na=False)
        )
        res = df[mask]
        
        if not res.empty:
            selected_idx = st.selectbox(
                "請確認具體輔具項目：(一般戶補助50%、中低收入戶補助75%、低收入戶補助100%)",
                options=res.index,
                format_func=lambda i: f"項次 {res.loc[i, '項次']}: {res.loc[i, '名稱']}"
            )
            
            item = res.loc[selected_idx]
            
            st.divider()
            col1, col2 = st.columns([1, 1])

            # --- 左側：基準資訊與【新增】代碼對照 ---
            with col1:
                st.subheader("📋 補助基準詳細資訊")
                st.info(f"**【輔具品項名稱】**：{item['名稱']}")
                
                st.markdown(f"""
                * 💰 **最高補助金額**：{item.get('最高補助金額', '未列出')}
                * ⏳ **最低使用年限**：{item.get('最低使用年限', '未列出')} 年
                * 🏥 **評估地點**：{item.get('評估地點', '未列出')}
                * 👤 **評估人員類別**：{item.get('評估類別', '未列出')}
                """)
                
                # 【新增】開關觸發後的代碼顯示區
                if show_codes:
                    st.markdown("---")
                    st.markdown("### 👁️ 本項次法定核可代碼")
                    
                    rule_key = get_rule_key(item['項次'])
                    if rule_key and rule_key in SPECIAL_RULES_MAP:
                        rule = SPECIAL_RULES_MAP[rule_key]
                        
                        # 顯示滿足此項即可補助
                        if rule["direct"]:
                            st.write("**📌 滿足此項即可補助：**")
                            st.code(", ".join(rule["direct"]), language="text")
                        
                        # 顯示隔離組合
                        for g in rule["groups"]:
                            st.write(f"**📌 {g['name']}：**")
                            st.write(f"- ICF: `{', '.join(g['icf'])}`")
                            # ICD 為了簡潔，顯示前 5 個並隱藏其餘
                            icd_display = ", ".join(g['icd'][:5]) + ( "..." if len(g['icd']) > 5 else "" )
                            st.write(f"- ICD: `{icd_display}`")
                    else:
                        st.write("💡 本項次採通用標準（視、聽、語障）判定。")

                if item.get('備註'):
                    st.warning(f"💡 **備註說明**：\n\n{item['備註']}")

            # --- 右側：判定引擎 (保持你喜歡的編排) ---
            with col2:
                st.subheader("🧪 資格符合自動判定")
                u_icf_raw = st.text_input("1. 輸入鑑定 ICF 代碼 (多個請用逗號隔開)", placeholder="例如: b117, b110.4")
                u_icd_raw = st.text_input("2. 輸入 ICD 診斷碼", placeholder="例如: F03")
                
                if st.button("執行自動判定", type="primary"):
                    u_icfs = [x.strip().lower() for x in u_icf_raw.split(",") if x.strip()]
                    u_icd = u_icd_raw.strip().upper()
                    
                    is_match = False
                    reason = ""
                    
                    rule_key = get_rule_key(item['項次'])
                    
                    if rule_key and rule_key in SPECIAL_RULES_MAP:
                        rule = SPECIAL_RULES_MAP[rule_key]
                        
                        # 【第一步】直接命中
                        hits = [i for i in u_icfs if i in [c.lower() for c in rule["direct"]]]
                        if hits:
                            is_match = True
                            reason = f"🎯 符合『滿足此項即可補助』(命中代碼: {', '.join(hits)})"
                        
                        # 【第二步】儲存格隔離組合
                        if not is_match:
                            for g in rule["groups"]:
                                icf_ok = any(i in u_icfs for i in [c.lower() for c in g["icf"]])
                                icd_ok = u_icd in [c.upper() for c in g["icd"]]
                                if icf_ok and icd_ok:
                                    is_match = True
                                    group_label = g.get("name", "儲存格組合")
                                    reason = f"✅ 符合 {group_label} 判定標準"
                                    break

                    # 【第三步】通用類別
                    if not is_match:
                        for r in [RULE_SPEECH_STD, RULE_VISION_STD, RULE_HEARING_STD]:
                            if any(i in u_icfs for i in [c.lower() for c in r["icf"]]):
                                is_match = True
                                reason = f"符合 {r['cat']} 通用判定標準"
                                break

                    if is_match:
                        st.success(f"🎯 **判定結果：符合補助條件**\n\n判定依據：{reason}")
                    else:
                        st.error("❌ **判定結果：不符合補助條件**")
        else:
            st.warning("查無符合的項次或輔具名稱。")
