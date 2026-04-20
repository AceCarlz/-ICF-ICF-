import streamlit as st
import pandas as pd
from data import (
    load_device_data, SPECIAL_RULES_MAP, get_rule_key,
    RULE_SPEECH_STD, RULE_VISION_STD, RULE_HEARING_STD
)

# 網頁基礎配置
st.set_page_config(page_title="輔助器具補助查詢系統", layout="wide")

# 讀取資料
df = load_device_data()

if df is None:
    st.error("❌ 找不到資料庫檔案 (assistive_devices.csv)，請確認檔案路徑與檔名。")
else:
    st.title("📂 輔助器具補助智慧查詢系統")
    st.caption("根據最新 data.py 邏輯執行：滿足此項即可補助 > 組合(1) > 組合(2) > 組合(3) > 通用標準")

    # 側邊欄搜尋
    with st.sidebar:
        st.header("🔍 查詢與檢索")
        search_query = st.text_input("輸入『項次』或『輔具名稱』", placeholder="例如: 91 或 輪椅")

    if search_query:
        # --- 雙軌搜尋邏輯 ---
        # 同時搜尋項次欄位與名稱欄位
        mask = (
            df['項次'].astype(str).str.contains(search_query, case=False, na=False) | 
            df['名稱'].astype(str).str.contains(search_query, case=False, na=False)
        )
        res = df[mask]
        
        if not res.empty:
            # 下拉選單顯示「項次 + 名稱」
            selected_idx = st.selectbox(
                "請確認具體輔具項目：(一般戶補助50%、中低收入戶補助75%、低收入戶補助100%)",
                options=res.index,
                format_func=lambda i: f"項次 {res.loc[i, '項次']}: {res.loc[i, '名稱']}"
            )
            
            # 取得選定項次的完整資料列
            item = res.loc[selected_idx]
            
            st.divider()
            col1, col2 = st.columns([1, 1])

            # --- 左側：完整資訊呈現 (從 CSV 讀取) ---
            with col1:
                st.subheader("📋 補助基準詳細資訊")
                st.info(f"**【輔具品項名稱】**：{item['名稱']}")
                
                st.markdown(f"""
                * 💰 **最高補助金額**：{item.get('最高補助金額', '未列出')}
                * ⏳ **最低使用年限**：{item.get('最低使用年限', '未列出')} 年
                * 🏥 **評估地點**：{item.get('評估地點', '未列出')}
                * 👤 **評估人員類別**：{item.get('評估類別', '未列出')}
                """)
                
                if item.get('備註'):
                    st.warning(f"💡 **備註說明**：\n\n{item['備註']}")

            # --- 右側：資格符合判定 (嚴格執行 data.py 邏輯) ---
            with col2:
                st.subheader("🧪 資格符合自動判定")
                u_icf_raw = st.text_input("1. 輸入鑑定 ICF 代碼 (多個請用逗號隔開)", placeholder="例如: b117, b110.4")
                u_icd_raw = st.text_input("2. 輸入 ICD 診斷碼", placeholder="例如: F03")
                
                if st.button("執行自動判定", type="primary"):
                    # 清理輸入資料
                    u_icfs = [x.strip().lower() for x in u_icf_raw.split(",") if x.strip()]
                    u_icd = u_icd_raw.strip().upper()
                    
                    is_match = False
                    reason = ""
                    
                    # 獲取 data.py 中的規則對應 Key
                    rule_key = get_rule_key(item['項次'])
                    
                    if rule_key and rule_key in SPECIAL_RULES_MAP:
                        rule = SPECIAL_RULES_MAP[rule_key]
                        
                        # 【第一步】滿足此項即可補助 (Direct match)
                        hits = [i for i in u_icfs if i in [c.lower() for c in rule["direct"]]]
                        if hits:
                            is_match = True
                            reason = f"🎯 符合『滿足此項即可補助』(命中代碼: {', '.join(hits)})"
                        
                        # 【第二步】若未中，依序檢查隔離儲存格組合 (Groups)
                        if not is_match:
                            for g in rule["groups"]:
                                # 嚴格限制：ICF 與 ICD 必須在同一組合內同時滿足
                                icf_ok = any(i in u_icfs for i in [c.lower() for c in g["icf"]])
                                icd_ok = u_icd in [c.upper() for c in g["icd"]]
                                
                                if icf_ok and icd_ok:
                                    is_match = True
                                    group_label = g.get("name", "儲存格組合")
                                    reason = f"✅ 符合 {group_label} 判定標準 (ICF與ICD於同一儲存格配對成功)"
                                    break # 只要符合其中一個組別就停止判定

                    # 【第三步】若上述皆未中，檢查通用類別 (視聽語障)
                    if not is_match:
                        for r in [RULE_SPEECH_STD, RULE_VISION_STD, RULE_HEARING_STD]:
                            if any(i in u_icfs for i in [c.lower() for c in r["icf"]]):
                                is_match = True
                                reason = f"符合 {r['cat']} 通用判定標準"
                                break

                    # --- 判定結果呈現 ---
                    if is_match:
                        st.success(f"🎯 **判定結果：符合補助條件**\n\n判定依據：{reason}")
                    else:
                        st.error("❌ **判定結果：不符合補助條件**\n\n原因：輸入之代碼組合未命中該項次之法定補助標準。")
        else:
            st.warning("查無符合的項次或輔具名稱，請重新輸入關鍵字。")
