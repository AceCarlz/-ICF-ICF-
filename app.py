import streamlit as st
import pandas as pd
from data import (
    load_device_data, SPECIAL_RULES_MAP, get_rule_key,
    RULE_SPEECH_STD, RULE_VISION_STD, RULE_HEARING_STD
)

# 1. 網頁基礎配置
st.set_page_config(page_title="輔助器具補助查詢系統", layout="wide")

# 2. 清除快取與讀取機制 (確保轉圈圈問題解決)
@st.cache_data(ttl=600)  # 每 10 分鐘自動重整
def get_cached_data():
    return load_device_data()

df = get_cached_data()

if df is None:
    st.error("❌ 找不到資料庫檔案 (assistive_devices.csv)，請確認檔案已上傳至 GitHub。")
else:
    st.title("📂 輔助器具補助智慧查詢系統")
    st.caption("判定邏輯：data.py 特定規則 > CSV 登記之 ICF > 通用標準判定")

    # 3. 側邊欄：搜尋、顯示開關、手動刷新
    with st.sidebar:
        st.header("🔍 查詢與檢索")
        search_query = st.text_input("輸入『項次』或『輔具名稱』", placeholder="例如: 91 或 輪椅")
        
        st.divider()
        # 功能：一鍵切換顯示/隱藏
        show_codes = st.toggle("📂 顯示本項核可代碼 (電話對照用)", value=False)
        
        # 功能：手動強制刷新 (解決數據同步或轉圈圈問題)
        if st.button("🔄 重新整理資料庫"):
            st.cache_data.clear()
            st.rerun()

    if search_query:
        # 雙軌搜尋 (項次或名稱)
        mask = (
            df['項次'].astype(str).str.contains(search_query, case=False, na=False) | 
            df['名稱'].astype(str).str.contains(search_query, case=False, na=False)
        )
        res = df[mask]
        
        if not res.empty:
            # 你喜歡的下拉選單編排
            selected_idx = st.selectbox(
                "請確認具體輔具項目：(一般戶補助50%、中低收入戶補助75%、低收入戶補助100%)",
                options=res.index,
                format_func=lambda i: f"項次 {res.loc[i, '項次']}: {res.loc[i, '名稱']}"
            )
            item = res.loc[selected_idx]
            
            st.divider()
            col1, col2 = st.columns([1, 1])

            # --- 左側：基準資訊與代碼一覽 ---
            with col1:
                st.subheader("📋 補助基準詳細資訊")
                st.info(f"**【輔具品項名稱】**：{item['名稱']}")
                
                st.markdown(f"""
                * 💰 **最高補助金額**：{item.get('最高補助金額', '未列出')}
                * ⏳ **最低使用年限**：{item.get('最低使用年限', '未列出')} 年
                * 🏥 **評估地點**：{item.get('評估地點', '未列出')}
                * 👤 **評估人員類別**：{item.get('評估類別', '未列出')}
                """)
                
                # --- 開關觸發：代碼對照顯示 ---
                if show_codes:
                    st.markdown("---")
                    st.markdown("### 👁️ 本項次法定核可代碼")
                    
                    # 💡 強化版 CSS：全面覆蓋所有可能的代碼容器
                    st.markdown("""
                        <style>
                        /* 針對所有代碼區塊的 pre 和 code 標籤 */
                        div[data-testid="stCodeBlock"] pre, 
                        div[data-testid="stCodeBlock"] code,
                        code {
                            white-space: pre-wrap !important;       /* 強制換行 */
                            word-wrap: break-word !important;      /* 長單字斷行 */
                            word-break: break-all !important;      /* 暴力斷行，確保不超出邊界 */
                        }
                        /* 移除可能產生的水平捲軸外殼 */
                        div[data-testid="stCodeBlock"] {
                            overflow-x: hidden !important;
                        }
                        </style>
                    """, unsafe_allow_html=True)

                    rule_key = get_rule_key(item['項次'])
                    
                    # A. 優先顯示 data.py 的規則
                    if rule_key and rule_key in SPECIAL_RULES_MAP:
                        rule = SPECIAL_RULES_MAP[rule_key]
                        
                        # 1. 直接補助
                        if rule["direct"]:
                            st.write("**📌 直接補助 ICF：**")
                            st.code(", ".join(rule["direct"]), language="text")
                        
                        # 2. 組合判定
                        for g in rule["groups"]:
                            st.write(f"**📌 {g['name']}：**")
                            st.caption(f"需同時滿足以下 ICF 與任一 ICD：")
                            
                            st.write("**核可 ICF：**")
                            st.code(", ".join(g['icf']), language="text")
                            
                            st.write("**核可 ICD：**")
                            # 這裡確保 ICD 字串合併後也能被 CSS 抓到
                            st.code(", ".join(g['icd']), language="text")
                    
                    # B. 顯示 CSV 中的「核可ICF」欄位
                    csv_icf_str = str(item.get('核可ICF', '')).strip()
                    if csv_icf_str:
                        st.write("**📌 CSV 登記核可 ICF：**")
                        st.code(csv_icf_str, language="text")
                    
                    if not (rule_key and rule_key in SPECIAL_RULES_MAP) and not csv_icf_str:
                        st.write("💡 本項次目前依據通用標準（視、聽、語障）判定。")
                        
                if item.get('備註'):
                    st.warning(f"💡 **備註說明**：\n\n{item['備註']}")

            # --- 右側：判定引擎 (嚴格執行你提供的正確邏輯) ---
            with col2:
                st.subheader("🧪 資格符合自動判定")
                u_icf_raw = st.text_input("1. 輸入鑑定 ICF 代碼 (多個請用逗號隔開)", placeholder="例如: b117, b110")
                u_icd_raw = st.text_input("2. 輸入 ICD 診斷碼 (僅部分品項需要)", placeholder="例如: F03")
                
                if st.button("執行自動判定", type="primary"):
                    # 資料清理
                    u_icfs = [x.strip().lower() for x in u_icf_raw.split(",") if x.strip()]
                    u_icd = u_icd_raw.strip().upper()
                    
                    is_match = False
                    reason = ""
                    
                    # A. 軌道 1：檢查 data.py 規則地圖
                    rule_key = get_rule_key(item['項次'])
                    if rule_key and rule_key in SPECIAL_RULES_MAP:
                        rule = SPECIAL_RULES_MAP[rule_key]
                        
                        # 1. 滿足此項即可補助
                        hits = [i for i in u_icfs if i in [c.lower() for c in rule["direct"]]]
                        if hits:
                            is_match, reason = True, f"符合『滿足此項即可補助』(命中代碼: {', '.join(hits)})"
                        
                        # 2. 儲存格隔離判定 (ICF + ICD 同時成立)
                        if not is_match:
                            for g in rule["groups"]:
                                icf_ok = any(i in u_icfs for i in [c.lower() for c in g["icf"]])
                                icd_ok = u_icd in [c.upper() for c in g["icd"]]
                                if icf_ok and icd_ok:
                                    is_match, reason = True, f"符合 {g['name']} 判定標準"
                                    break
                    
                    # B. 軌道 2：檢查 CSV 核可ICF (data.py 找不到或未命中時)
                    if not is_match:
                        csv_icf_str = str(item.get('核可ICF', '')).strip()
                        if csv_icf_str:
                            csv_icf_list = [x.strip().lower() for x in csv_icf_str.split(",") if x.strip()]
                            hits = [i for i in u_icfs if i in csv_icf_list]
                            if hits:
                                is_match, reason = True, f"符合手冊登記之核可 ICF 代碼 ({', '.join(hits)})"

                    # C. 軌道 3：通用標準 (視聽語)
                    if not is_match:
                        for r in [RULE_SPEECH_STD, RULE_VISION_STD, RULE_HEARING_STD]:
                            if any(i in u_icfs for i in [c.lower() for c in r["icf"]]):
                                is_match, reason = True, f"符合 {r['cat']} 通用判定標準"
                                break

                    # 結果呈現
                    if is_match:
                        st.success(f"🎯 **判定結果：符合補助條件**\n\n判定依據：{reason}")
                    else:
                        st.error("❌ **判定結果：不符合補助條件**\n\n原因：輸入代碼組合未命中該項次之法定標準。")
        else:
            st.warning("查無符合的項次或輔具名稱，請重新輸入關鍵字。")
