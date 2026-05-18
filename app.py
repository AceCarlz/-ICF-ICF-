import streamlit as st
import pandas as pd
from data import (
    load_device_data, SPECIAL_RULES_MAP, get_rule_key,
    RULE_SPEECH_STD, RULE_VISION_STD, RULE_HEARING_STD
)

# 1. 網頁基礎配置
st.set_page_config(page_title="輔助器具補助智慧查詢系統", layout="wide")

# 2. 清除快取與讀取機制
@st.cache_data(ttl=600)
def get_cached_data():
    return load_device_data()

df = get_cached_data()

if df is None:
    st.error("❌ 找不到資料庫檔案 (assistive_devices.csv)，請確認檔案已上傳至 GitHub。")
else:
    st.title("📂 輔助器具補助智慧查詢系統")
    st.caption("🚀 判定邏輯已優化：複雜特定規則（獨立判定）/ 一般品項（CSV 登記 ICF > 通用標準）")

    # 3. 側邊欄：搜尋、顯示開關、手動刷新
    with st.sidebar:
        st.header("🔍 查詢與檢索")
        search_query = st.text_input("輸入『項次』或『輔具名稱』", placeholder="例如: 91 或 輪椅")
        
        st.divider()
        show_codes = st.toggle("📂 顯示本項核可代碼 (電話對照用)", value=False)
        
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
            selected_idx = st.selectbox(
                "請確認具體輔具項目：(一般戶補助50%、中低收入戶補助75%、低收入戶補助100%；※代表不分身分別統一補助額)",
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
                
                if show_codes:
                    st.markdown("---")
                    st.markdown("### 👁️ 本項次法定核可代碼")
                    st.markdown("""
                        <style>
                        div[data-testid="stCodeBlock"] pre, 
                        div[data-testid="stCodeBlock"] code,
                        code {
                            white-space: pre-wrap !important;
                            word-wrap: break-word !important;
                            word-break: break-all !important;
                        }
                        div[data-testid="stCodeBlock"] {
                            overflow-x: hidden !important;
                        }
                        </style>
                    """, unsafe_allow_html=True)

                    rule_key = get_rule_key(item['項次'])
                    if rule_key and rule_key in SPECIAL_RULES_MAP:
                        rule = SPECIAL_RULES_MAP[rule_key]
                        if rule["direct"]:
                            st.write("**📌 直接補助 ICF：**")
                            st.code(", ".join(rule["direct"]), language="text")
                        
                        for g in rule["groups"]:
                            st.write(f"**📌 {g['name']}：**")
                            st.caption(f"需同時滿足以下 ICF 與任一 ICD：")
                            st.write("**核可 ICF：**")
                            st.code(", ".join(g['icf']), language="text")
                            st.write("**核可 ICD：**")
                            st.code(", ".join(g['icd']), language="text")
                    
                    csv_icf_str = str(item.get('核可ICF', '')).strip()
                    if csv_icf_str:
                        st.write("**📌 CSV 登記核可 ICF：**")
                        st.code(csv_icf_str, language="text")
                
                if item.get('備註'):
                    st.warning(f"💡 **備註說明**：\n\n{item['備註']}")

            # --- 右側：判定引擎 ---
            with col2:
                st.subheader("🧪 資格符合自動判定")
                
                rule_key = get_rule_key(item['項次'])
                is_special_rule = rule_key and rule_key in SPECIAL_RULES_MAP
                
                if not is_special_rule:
                    st.caption("✅ 此品項採單一標準判定，通常僅需輸入 ICF 代碼。")
                else:
                    st.caption("⚠️ 此品項為複雜判定，請【同時輸入】ICF 與 ICD 代碼進行交叉比對。")

                u_icf_raw = st.text_input(
                    "1. 輸入鑑定 ICF 代碼 (多個請用逗號隔開)", 
                    placeholder="例如: b117, b110",
                    key=f"icf_in_{item['項次']}"
                )
                u_icd_raw = st.text_input(
                    "2. 輸入 ICD 診斷碼 (複雜判定品項必填)", 
                    placeholder="例如: F03",
                    key=f"icd_in_{item['項次']}"
                )
                
                submit_button = st.button(
                    "執行自動判定", 
                    type="primary", 
                    key=f"btn_run_{item['項次']}"
                )

                # 智慧型觸發判斷：有按按鈕，或是使用者打完字引發頁面刷新
                # 如果是複雜規則項目，按 Enter 觸發必須確保使用者兩個框框都注意到了（ICF有值即可觸發，由後面防呆邏輯接手）
                if submit_button or u_icf_raw:
                    if not u_icf_raw:
                        if submit_button:
                            st.warning("請至少輸入 ICF 代碼再進行判定。")
                    else:
                        # 資料標準化整理
                        u_icfs = [x.strip().lower() for x in u_icf_raw.split(",") if x.strip()]
                        u_icd = u_icd_raw.strip().upper()
                        
                        is_match = False
                        reason = ""
                        has_checked = False # 用來標記是否已經由特定規則判定完畢

                        # ==================== 軌道 A：複雜特定規則判定 ====================
                        if is_special_rule:
                            has_checked = True # 只要屬於特殊規則，就不允許流向一般品項判定
                            rule = SPECIAL_RULES_MAP[rule_key]
                            
                            # A-1. 優先檢查是否命中「免 ICD 直通車」的特定 ICF
                            hits = [i for i in u_icfs if i in [c.lower() for c in rule["direct"]]]
                            if hits:
                                is_match = True
                                reason = f"符合特定直通核可代碼 (命中: {', '.join(hits)})"
                            
                            # A-2. 若未直通，嚴格執行「ICF + ICD 組合判定」
                            if not is_match:
                                if not u_icd:
                                    # 防呆：如果是複雜項目，只打了 ICF 按 Enter 卻沒打 ICD 時，給予友善提示，不直接給不符合
                                    st.info("💡 此品項需搭配 ICD 診斷碼進行組合判定，請輸入 ICD 診斷碼。")
                                    has_checked = False # 阻斷本次結果呈現，等待使用者輸入 ICD
                                else:
                                    for g in rule["groups"]:
                                        icf_ok = any(i in u_icfs for i in [c.lower() for c in g["icf"]])
                                        icd_ok = u_icd in [c.upper() for c in g["icd"]]
                                        if icf_ok and icd_ok:
                                            is_match = True
                                            reason = f"符合 {g['name']} 組合條件判定"
                                            break

                        # ==================== 一般品項判定 (非複雜規則才執行) ====================
                        if not has_checked:
                            # 只有當不屬於特殊複雜規則，或者複雜規則內未被阻斷時，才進行一般判定
                            if not is_special_rule: 
                                # 軌道 B：CSV 包含判定
                                csv_icf_raw = str(item.get('核可ICF', '')).lower()
                                if csv_icf_raw:
                                    found_hits = [i for i in u_icfs if i in csv_icf_raw]
                                    if found_hits:
                                        is_match = True
                                        reason = f"符合手冊登記之核可 ICF 代碼 (命中: {', '.join(found_hits)})"

                                # 軌道 C：通用標準
                                if not is_match:
                                    for r in [RULE_SPEECH_STD, RULE_VISION_STD, RULE_HEARING_STD]:
                                        if any(i in u_icfs for i in [c.lower() for c in r["icf"]]):
                                            is_match = True
                                            reason = f"符合 {r['cat']} 通用判定標準"
                                            break
                                            
                                has_checked = True # 標記一般品項也判定完成

                        # ==================== 結果呈現 ====================
                        if has_checked:
                            if is_match:
                                st.success(f"🎯 **判定結果：符合補助條件**\n\n判定依據：{reason}")
                                if "18歲" in str(item.get('核可ICF', '')):
                                    st.info("⚠️ 注意：此項次於手冊中有標註年齡限制，請手動確認申請人年齡。")
                            else:
                                if is_special_rule:
                                    st.error("❌ **判定結果：不符合補助條件**\n\n原因：輸入之 ICF 與 ICD 組合未命中該項次的法定配對標準。")
                                else:
                                    st.error("❌ **判定結果：不符合補助條件**\n\n原因：輸入之代碼組合未命中該項次之法定標準。")
        else:
            st.warning("查無符合的項次或輔具名稱，請重新輸入關鍵字。")
