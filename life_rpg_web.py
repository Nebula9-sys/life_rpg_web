"""
╔══════════════════════════════════════════╗
║     🎮  Life-RPG  网页版                 ║
║     云存档 · 密码保护 · 手机可用          ║
╚══════════════════════════════════════════╝
"""

import streamlit as st
import requests
import json
import os
from datetime import datetime

# ═══════════════════════════════════════════════════
#  ⚙️ 配置区 —— 必须修改以下 3 项
# ═══════════════════════════════════════════════════

APP_PASSWORD     = ""       # 🔐 你的登录密码
JSONBIN_API_KEY  = ""                # 🔑 JSONBin API Key
JSONBIN_BIN_ID   = ""                # 📦 JSONBin Bin ID
TIMEZONE_OFFSET = 8

# ═══════════════════════════════════════════════════
#  以下代码不需要修改
# ═══════════════════════════════════════════════════

# ---------- 时间工具 ----------
from datetime import timedelta

def now_str():
    """返回带时区偏移的当前时间字符串"""
    utc_now = datetime.utcnow()
    local_now = utc_now + timedelta(hours=TIMEZONE_OFFSET)
    return local_now.strftime("%Y-%m-%d %H:%M")

# ---------- 页面配置 ----------
st.set_page_config(
    page_title="Life-RPG",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------- 读取 Streamlit Secrets（部署时用） ----------
def get_secret(key, fallback):
    try:
        return st.secrets[key]
    except Exception:
        return fallback

PASSWORD = get_secret("PASSWORD", APP_PASSWORD)
API_KEY  = get_secret("JSONBIN_API_KEY", JSONBIN_API_KEY)
BIN_ID   = get_secret("JSONBIN_BIN_ID", JSONBIN_BIN_ID)

# ---------- Session State 初始化 ----------
for k, v in {"authed": False, "data": None, "theme": "🌌 莫兰迪蓝", "pending_toasts": []}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------- 默认数据 ----------
def new_data():
    return {
        "stats": {
            "Productivity": 0,
            "Creativity": 0,
            "Willpower": 0,
            "Vitality": 0,
        },
        "action_log": [],
        "resistance_log": [],
        "rewards": [
            {"name": "☕ 一杯好咖啡",     "cost": 30},
            {"name": "🎬 看一部电影",     "cost": 80},
            {"name": "🍣 一顿大餐",      "cost": 150},
            {"name": "🎮 游戏时间2小时",   "cost": 200},
            {"name": "🛌 睡到自然醒的一天", "cost": 500},
        ],
        "redemption_log": [],   # 兑换历史
        "total_earned": 0,
    }


# ---------- 云存档 ----------
LOCAL_FILE = "life_rpg_save.json"


def cloud_load():
    if not API_KEY or not BIN_ID:
        return None
    try:
        r = requests.get(
            "https://api.jsonbin.io/v3/b/" + BIN_ID + "/latest",
            headers={"X-Master-Key": API_KEY},
            timeout=10,
        )
        if r.status_code == 200:
            return r.json()["record"]
    except Exception:
        pass
    return None


def cloud_save(data):
    if not API_KEY or not BIN_ID:
        return False
    try:
        r = requests.put(
            "https://api.jsonbin.io/v3/b/" + BIN_ID,
            headers={"X-Master-Key": API_KEY, "Content-Type": "application/json"},
            json=data,
            timeout=10,
        )
        return r.status_code == 200
    except Exception:
        return False


def local_load():
    if os.path.exists(LOCAL_FILE):
        try:
            with open(LOCAL_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return None


def local_save(data):
    try:
        with open(LOCAL_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def load_data():
    data = cloud_load() or local_load() or new_data()
    base = new_data()
    for k in base:
        if k not in data:
            data[k] = base[k]
    for k in base["stats"]:
        if k not in data["stats"]:
            data["stats"][k] = base["stats"][k]
    # 兼容旧版：去掉旧的 claimed 字段
    for r in data.get("rewards", []):
        r.pop("claimed", None)
    return data


def save_data(data):
    cloud_ok = cloud_save(data)
    local_save(data)
    if cloud_ok:
        queue_toast("☁️ 云存档已同步", icon="✅")
    elif API_KEY and BIN_ID:
        queue_toast("⚠️ 云端同步失败，已存本地", icon="💾")

# ---------- 自定义样式 ----------

def on_theme_change():
    """主题切换回调：在页面重绘前更新 session_state"""
    st.session_state["theme"] = st.session_state.get("theme_select", "🌌 莫兰迪蓝")


def queue_toast(msg, icon="✅"):
    """把气泡消息存进队列，等页面刷新后再弹出"""
    st.session_state.pending_toasts.append({"msg": msg, "icon": icon})


def show_pending_toasts():
    """渲染队列里的气泡，然后清空"""
    if st.session_state.pending_toasts:
        for t in st.session_state.pending_toasts:
            queue_toast(t["msg"], icon=t["icon"])
        st.session_state.pending_toasts = []


def get_theme_css(theme_name):
    """根据主题名称返回对应 CSS"""
    themes = {
        "🌌 莫兰迪蓝": {
            "bg1": "#f2f5f8", "bg2": "#e8edf2", "bg3": "#ecf0f5",
            "sb1": "#e5eaf0", "sb2": "#dce3ea",
            "inp": "#ffffff", "btn": "#cdd8e2", "btn_h": "#bfccda",
            "tx_h": "#2a3a4a", "tx_m": "#3a4d5e", "tx_s": "#6a8295",
            "tx_p": "#9aafc0",
            "ac": "#7a9eb0", "ac_l": "#9ab8c8", "ac_d": "#5a8092",
            "bd": "#c0d0da",
            "p1": "#5a8092", "p2": "#7a9eb0",
            "ok_b": "#d4edda", "ok_t": "#2d5a2d", "ok_d": "#8fd49a",
            "in_b": "#d6eaf5", "in_t": "#2a5570", "in_d": "#8ac0d8",
            "wa_b": "#fef3cd", "wa_t": "#6a5200", "wa_d": "#d4be60",
            "er_b": "#f8d7da", "er_t": "#6a2530", "er_d": "#d48090",
            "ex_d": "#b8c8d5", "tb_b": "#5a8092", "tb_a": "#e4eaf0",
        },
        "🌸 莫兰迪粉": {
            "bg1": "#faf3f2", "bg2": "#f5eae8", "bg3": "#f7efed",
            "sb1": "#f3e8e6", "sb2": "#efe0dd",
            "inp": "#ffffff", "btn": "#e8d5d0", "btn_h": "#ddc8c2",
            "tx_h": "#4a3540", "tx_m": "#5c4a50", "tx_s": "#8a7580",
            "tx_p": "#b8a0aa",
            "ac": "#c7958d", "ac_l": "#d4a8a0", "ac_d": "#a07570",
            "bd": "#ddd0cc",
            "p1": "#a07570", "p2": "#c7958d",
            "ok_b": "#d4edda", "ok_t": "#2d5a2d", "ok_d": "#8fd49a",
            "in_b": "#d6eaf5", "in_t": "#2a5570", "in_d": "#8ac0d8",
            "wa_b": "#fef3cd", "wa_t": "#6a5200", "wa_d": "#d4be60",
            "er_b": "#f8d7da", "er_t": "#6a2530", "er_d": "#d48090",
            "ex_d": "#e0d0d0", "tb_b": "#c7958d", "tb_a": "#f0e2e0",
        },
        "🍫 薄荷巧克力": {
            "bg1": "#f0faf8", "bg2": "#e6f4f0", "bg3": "#ebf7f4",
            "sb1": "#e4f2ee", "sb2": "#dcede8",
            "inp": "#ffffff", "btn": "#c8ede5", "btn_h": "#b8e2d8",
            "tx_h": "#3a2828", "tx_m": "#503838", "tx_s": "#7a6868",
            "tx_p": "#a89898",
            "ac": "#7fc5ca", "ac_l": "#9fe6dc", "ac_d": "#5a9ea5",
            "bd": "#c0d5d0",
            "p1": "#5a3839", "p2": "#764f51",
            "ok_b": "#d4edda", "ok_t": "#2d5a2d", "ok_d": "#8fd49a",
            "in_b": "#d6eaf5", "in_t": "#2a5570", "in_d": "#8ac0d8",
            "wa_b": "#fef3cd", "wa_t": "#6a5200", "wa_d": "#d4be60",
            "er_b": "#f8d7da", "er_t": "#6a2530", "er_d": "#d48090",
            "ex_d": "#c0d5d0", "tb_b": "#764f51", "tb_a": "#e6f4f0",
        },
    }
    t = themes.get(theme_name, themes["🌌 莫兰迪蓝"])

    tpl = """
<style>
/* === [THEME_NAME] === */
.stApp {
    background: linear-gradient(160deg, [bg1] 0%, [bg2] 50%, [bg3] 100%);
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, [sb1], [sb2]);
}
[data-testid="stSidebar"] * {
    color: [tx_m] !important;
}
.stMarkdown, .stMarkdown *, p, span, label,
.stCaption, .stCaption * {
    color: [tx_m] !important;
}
h1, h2, h3 { color: [tx_h] !important; }
h4, h5, h6 { color: [tx_s] !important; }
[data-testid="stMetricValue"] {
    font-size: 2.2rem !important;
    font-weight: 800;
    color: [tx_h] !important;
}
[data-testid="stMetricLabel"] {
    font-size: 1rem !important;
    color: [tx_s] !important;
}
[data-testid="stMetricDelta"] {
    color: [ac] !important;
}
.stProgress > div > div > div {
    background: linear-gradient(90deg, [ac], [ac_l]);
}
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background-color: [inp];
    color: [tx_m] !important;
    border-color: [bd];
}
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {
    color: [tx_p] !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: [ac];
    box-shadow: 0 0 0 1px [ac];
}
.stSelectbox [data-baseweb="select"] {
    color: [tx_m] !important;
}
.stButton > button {
    border-radius: 10px;
    color: [tx_m];
    border-color: [bd];
    background-color: [btn];
    transition: all 0.2s;
}
.stButton > button:hover {
    background-color: [btn_h];
    border-color: [ac];
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, [p1], [p2]);
    border-color: [ac];
    color: [tx_h];
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, [p2], [ac_l]);
}
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background-color: transparent;
}
.stTabs [data-baseweb="tab"] {
    color: [tx_s] !important;
    border-radius: 8px 8px 0 0;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: [tx_m] !important;
    background-color: [tb_a];
    border-bottom: 2px solid [tb_b];
}
.stAlert { border-radius: 8px; }
.stSuccess {
    background-color: [ok_b];
    color: [ok_t] !important;
    border-color: [ok_d];
}
.stInfo {
    background-color: [in_b];
    color: [in_t] !important;
    border-color: [in_d];
}
.stWarning {
    background-color: [wa_b];
    color: [wa_t] !important;
    border-color: [wa_d];
}
.stError {
    background-color: [er_b];
    color: [er_t] !important;
    border-color: [er_d];
}
.streamlit-expanderHeader {
    color: [tx_s] !important;
    background-color: transparent;
}
[data-testid="stExpander"] {
    border-color: [ex_d];
}
.stDownloadButton > button {
    border-radius: 10px;
    color: [tx_m];
    background-color: [btn];
    border-color: [bd];
}
[data-testid="stNumberInput"] input {
    background-color: [inp];
    color: [tx_m] !important;
    border-color: [bd];
}
.stCheckbox label { color: [tx_m] !important; }
code {
    color: [ac_l] !important;
    background-color: [inp];
}
.block-container {
    padding-top: 4.5rem !important;
}
@media (max-width: 768px) {
    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-top: 4.5rem !important;
    }

/* ═══════════════════════════════════
   移动端适配
   ═══════════════════════════════════ */
@media (max-width: 768px) {
    /* 标题小一点 */
    h1 { font-size: 1.6rem !important; }
    h2 { font-size: 1.4rem !important; }
    h3 { font-size: 1.2rem !important; }
    /* 数值面板数字小一点 */
    [data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
    }
    /* Tab 标签字小一点，不换行 */
    .stTabs [data-baseweb="tab"] {
        font-size: 0.8rem !important;
        padding: 0.4rem 0.6rem !important;
        white-space: nowrap;
    }
    /* 按钮不要太肥 */
    .stButton > button {
        padding: 0.4rem 0.8rem !important;
        font-size: 0.9rem !important;
    }
    /* 表格缩小 */
    .stTable {
        font-size: 0.8rem !important;
    }
}
</style>

"""
    css = tpl.replace("[THEME_NAME]", theme_name)
    for key, val in t.items():
        css = css.replace("[" + key + "]", val)
    return css


st.markdown(
    get_theme_css(st.session_state.get("theme", "🌌 莫兰迪蓝")),
    unsafe_allow_html=True,
)

# ═══════════════════════════════════════════════════
#  登录界面
# ═══════════════════════════════════════════════════

if not st.session_state.authed:
    _, col_mid, _ = st.columns([1.5, 1, 1.5])
    with col_mid:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="text-align: center;">
                <h1 style="font-size: 3rem;">🎮 Life-RPG</h1>
                <p style="font-size: 1.1rem; color: #999;">个人经验值管理系统 · 云存档</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)
        pwd = st.text_input("🔑 输入密码", type="password", key="login_pwd")
        if st.button("⚔️ 进入系统", use_container_width=True):
            if pwd == PASSWORD:
                st.session_state.authed = True
                with st.spinner("读取存档中..."):
                    st.session_state.data = load_data()
                st.rerun()
            else:
                st.error("❌ 密码错误")
    st.stop()

# ═══════════════════════════════════════════════════
#  主界面（登录后）
# ═══════════════════════════════════════════════════

data = st.session_state.data

# -------- 侧边栏 --------
with st.sidebar:
    st.markdown("### 🎮 Life-RPG")
    st.markdown("---")
    st.markdown("**存档状态**")
    if API_KEY and BIN_ID:
        st.success("☁️ 云存档已连接")
        st.caption("Bin: ..." + BIN_ID[-6:])
        if st.button("🔄 同步云端", use_container_width=True):
            with st.spinner("同步中..."):
                cloud_data = cloud_load()
                if cloud_data:
                    st.session_state.data = cloud_data
                    data = cloud_data
                    queue_toast("✅ 已拉取云端最新数据")
                    st.rerun()
                else:
                    queue_toast("⚠️ 同步失败")
    else:
        st.warning("💾 仅本地存档")
        st.caption("配置 JSONBin 后可手机同步")

# --- 主题切换 ---
    st.markdown("---")
    st.markdown("**🎨 配色主题**")
    theme_options = ["🌌 莫兰迪蓝", "🌸 莫兰迪粉", "🍫 薄荷巧克力"]
    current_theme = st.session_state.get("theme", "🌌 莫兰迪蓝")
    st.selectbox(
        "选择配色",
        theme_options,
        index=theme_options.index(current_theme),
        key="theme_select",
        on_change=on_theme_change,
        label_visibility="collapsed",
    )
    
    st.markdown("---")
    if st.button("💾 保存并退出", use_container_width=True):
        save_data(data)
        st.session_state.authed = False
        st.session_state.data = None
        st.rerun()

# -------- 属性面板 --------
stats = data["stats"]
total = sum(stats.values())

# -------- 弹出待显示的气泡 --------
show_pending_toasts()

# -------- 属性面板 --------
stats = data["stats"]
total = sum(stats.values())

st.markdown("## ⚔️ 属性面板")

attr_display = [
    ("⚡ 生产力", "Productivity", "工作产出 · 任务完成 · 效率"),
    ("💡 创造力", "Creativity",  "新想法 · 创作表达 · 创意解题"),
    ("🔥 意志力", "Willpower",   "克服阻力 · 坚持习惯 · 自律"),
    ("💚 精力",   "Vitality",    "运动 · 休息 · 健康管理"),
]

cols = st.columns(4)
for i, (label, key, desc) in enumerate(attr_display):
    with cols[i]:
        val = stats[key]
        level = val // 50
        next_lv = 50 - (val % 50)
        st.metric(label, str(val), delta="Lv." + str(level))
        st.progress(min((val % 50) / 50, 1.0))
        st.caption(desc)
        st.caption("距 Lv." + str(level + 1) + " 还需 " + str(next_lv))

col_info1, col_info2 = st.columns(2)
with col_info1:
    st.markdown("💰 **当前积分: " + str(total) + "**")
with col_info2:
    st.markdown("📈 **累计获得: " + str(data["total_earned"]) + "**")
with st.expander("📖 属性说明 & 加分举例"):
    st.markdown("""
| 属性 | 是什么 | 怎么加分 | 举例 |
|:---:|:---|:---|:---|
| ⚡ 生产力 | 做事产出的能力和效率 | 完成工作任务、交付成果 | 写完报告 ✅、回复积压邮件 ✅、整理项目文档 ✅、按时交付功能 ✅ |
| 💡 创造力 | 产生新想法、新表达的能力 | 任何创造性活动 | 写作/写诗 ✅、画画/设计 ✅、头脑风暴 ✅、找到更好的解决方案 ✅、学新技能 ✅ |
| 🔥 意志力 | 克服阻力、坚持做该做的事 | 克服困难、坚持习惯 | 闹钟响了就起 ✅、拒绝刷手机 ✅、做完不想做的事 ✅、**记录阻力复盘 +1** ✅ |
| 💚 精力 | 身体和心理的能量储备 | 照顾自己的身体 | 运动30分钟 ✅、健康饮食 ✅、早睡 ✅、冥想 ✅、散步 ✅、体检 ✅ |

> 💡 **小贴士**：同一件事可能同时提升多个属性！比如「早起去跑步」= 意志力 + 精力，选你觉得最主要的那个就好。
""")

st.markdown("---")

# -------- 功能标签页 --------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📝 记录任务", "🚧 阻力复盘", "🏆 奖励商店", "📋 历史日志", "⚙️ 设置"]
)


# ════════ Tab 1：记录任务 ════════
with tab1:
    st.markdown("### 📝 记录完成的任务")
    st.caption("每完成一件事，就赚一点经验值。积少成多。")

    c1, c2 = st.columns(2)
    with c1:
        attr_choice = st.selectbox(
            "提升哪个属性？",
            [
                "⚡ 生产力 (Productivity)",
                "💡 创造力 (Creativity)",
                "🔥 意志力 (Willpower)",
                "💚 精力 (Vitality)",
            ],
            key="task_attr",
        )
    with c2:
        diff_choice = st.selectbox(
            "任务难度",
            ["🟢 小事 → +5", "🟡 普通 → +10", "🔴 突破 → +20"],
            key="task_diff",
        )

    task_desc = st.text_input(
        "做了什么？", placeholder="比如：完成了项目报告", key="task_desc"
    )

    if st.button("✅ 提交记录", use_container_width=True, type="primary"):
        attr_map = {
            "⚡ 生产力 (Productivity)": "Productivity",
            "💡 创造力 (Creativity)": "Creativity",
            "🔥 意志力 (Willpower)": "Willpower",
            "💚 精力 (Vitality)": "Vitality",
        }
        diff_map = {"🟢 小事 → +5": 5, "🟡 普通 → +10": 10, "🔴 突破 → +20": 20}

        attr_key = attr_map[attr_choice]
        points = diff_map[diff_choice]

        data["stats"][attr_key] += points
        data["total_earned"] += points
        data["action_log"].append(
            {
                "time": now_str(),
                "task": task_desc or "(未填写)",
                "attribute": attr_key,
                "points": points,
            }
        )
        save_data(data)
        st.session_state.data = data

        new_val = data["stats"][attr_key]
        new_lv = new_val // 50
        queue_toast(
            "🎉 +" + str(points) + " " + attr_key + "！当前 " + str(new_val),
            icon="✅"
        )
        if points >= 20:
            st.balloons()

        st.rerun()

# ════════ Tab 2：阻力复盘 ════════
with tab2:
    st.markdown("### 🚧 阻力复盘")
    st.info(
        "💪 记录一次启动困难 → **+1 Willpower**\n\n面对问题本身就是勇气。写下来，下次就不怕了。"
    )

    reason = st.selectbox(
        "这次为什么启动困难？",
        [
            "🐌 拖延 — 就是想逃避",
            "😴 疲劳 — 身体或精神累",
            "📱 干扰 — 手机/环境分心",
            "😰 恐惧 — 怕做不好",
            "🤷 迷茫 — 不知道从哪开始",
            "🧠 其他",
        ],
        key="resist_reason",
    )

    c3, c4 = st.columns(2)
    with c3:
        detail = st.text_area(
            "发生了什么？", placeholder="越具体越好", key="resist_detail"
        )
    with c4:
        strategy = st.text_area(
            "💡 明天怎么做？", placeholder="改进策略", key="resist_strategy"
        )

    if st.button("📝 记录复盘", use_container_width=True, type="primary"):
        data["stats"]["Willpower"] += 1
        data["total_earned"] += 1
        data["resistance_log"].append(
            {
                "time": now_str(),
                "reason": reason,
                "detail": detail or "(未填写)",
                "strategy": strategy or "(未填写)",
            }
        )
        save_data(data)
        st.session_state.data = data

        count = len(data["resistance_log"])
        queue_toast(
            "🔥 +1 Willpower | 直面阻力 " + str(count) + " 次",
            icon="💪"
        )

        st.rerun()
        
# ════════ Tab 3：奖励商店 ════════
with tab3:
    st.markdown("### 🏆 奖励商店")
    st.markdown(
        "💰 **当前积分: "
        + str(total)
        + "** — 同一个奖励可以反复兑换，每次都会扣积分"
    )
    st.markdown("---")

    rewards = data.get("rewards", [])
    redemption_log = data.get("redemption_log", [])

    # 统计每个奖励的兑换次数
    def count_redeemed(name):
        return sum(1 for r in redemption_log if r.get("reward_name") == name)

    if not rewards:
        st.warning("商店空空如也 → 去「设置」添加奖励")
    else:
        for i, reward in enumerate(rewards):
            cost = reward["cost"]
            can_buy = total >= cost
            times = count_redeemed(reward["name"])

            col_name, col_cost, col_times, col_btn = st.columns([2.5, 1, 0.8, 1.2])

            with col_name:
                st.markdown("🎁 **" + reward["name"] + "**")

            with col_cost:
                if can_buy:
                    st.caption("✅ " + str(cost) + " pts")
                else:
                    st.caption("❌ " + str(cost) + " pts (差 " + str(cost - total) + ")")

            with col_times:
                if times > 0:
                    st.caption("已兑 " + str(times) + " 次")
                else:
                    st.caption("—")

            with col_btn:
                if can_buy:
                    if st.button("兑换", key="r_" + str(i), type="primary"):
                        # 扣积分
                        to_pay = cost
                        for attr in ["Productivity", "Creativity", "Willpower", "Vitality"]:
                            if to_pay <= 0:
                                break
                            take = min(data["stats"][attr], to_pay)
                            data["stats"][attr] -= take
                            to_pay -= take
                        # 记录兑换历史
                        data["redemption_log"].append(
                            {
                                "time": now_str(),
                                "reward_name": reward["name"],
                                "cost": cost,
                            }
                        )
                        save_data(data)
                        st.session_state.data = data
                        st.success(
                            "🎉🎉🎉 **兑换成功！** "
                            + reward["name"]
                            + " — 好好享受！"
                        )
                        st.balloons()
                        st.rerun()
                else:
                    st.button("积分不够", disabled=True, key="r_" + str(i))

    # 兑换历史摘要
    if redemption_log:
        st.markdown("---")
        st.markdown("#### 📜 兑换历史")
        total_spent = sum(r.get("cost", 0) for r in redemption_log)
        st.caption(
            "累计兑换 "
            + str(len(redemption_log))
            + " 次，共花费 "
            + str(total_spent)
            + " pts"
        )
        for entry in reversed(redemption_log[-20:]):
            st.markdown(
                "- 🕐 "
                + entry.get("time", "")
                + " | "
                + entry.get("reward_name", "")
                + " | -"
                + str(entry.get("cost", 0))
                + " pts"
            )


# ════════ Tab 4：历史日志 ════════
with tab4:
    st.markdown("### 📋 历史日志")

    log1, log2, log3 = st.tabs(["📝 行为日志", "🚧 阻力记录", "📜 兑换记录"])

    # --- 行为日志 ---
    with log1:
        action_logs = data.get("action_log", [])
        if not action_logs:
            st.info("还没有记录 → 去完成任务吧！")
        else:
            st.caption("共 " + str(len(action_logs)) + " 条记录")
            if len(action_logs) > 10:
                show_count_action = st.slider(
                    "显示条数", 
                    min_value=10, 
                    max_value=min(len(action_logs), 200), 
                    value=min(30, len(action_logs)),
                    key="show_count_action"
                )
            else:
                show_count_action = len(action_logs)
            st.markdown("---")
            for entry in reversed(action_logs[-show_count_action:]):             
                attr_emoji = {
                    "Productivity": "⚡",
                    "Creativity": "💡",
                    "Willpower": "🔥",
                    "Vitality": "💚",
                }.get(entry.get("attribute", ""), "•")
                header = (
                    attr_emoji
                    + " +"
                    + str(entry.get("points", "?"))
                    + " — "
                    + str(entry.get("task", "?"))
                    + " ("
                    + str(entry.get("time", ""))
                    + ")"
                )
                with st.expander(header):
                    st.markdown("**属性**: " + str(entry.get("attribute", "?")))
                    st.markdown("**得分**: +" + str(entry.get("points", "?")))

    # --- 阻力记录 ---
    with log2:
        resist_logs = data.get("resistance_log", [])
        if not resist_logs:
            st.info("还没有复盘记录")
        else:
            st.caption("共 " + str(len(resist_logs)) + " 次直面阻力 💪")
            if len(resist_logs) > 10:
                show_count_resist = st.slider(
                    "显示条数", 
                    min_value=10, 
                    max_value=min(len(resist_logs), 200), 
                    value=min(30, len(resist_logs)),
                    key="show_count_resist"
                )
            else:
                show_count_resist = len(resist_logs)
            st.markdown("---")
            for entry in reversed(resist_logs[-show_count_resist:]):
                header = (
                    str(entry.get("reason", "?"))
                    + " — "
                    + str(entry.get("time", ""))
                )
                with st.expander(header):
                    st.markdown("**详情**: " + str(entry.get("detail", "?")))
                    st.markdown(
                        "💡 **改进策略**: " + str(entry.get("strategy", "?"))
                    )

    # --- 兑换记录 ---
    with log3:
        redemption_logs = data.get("redemption_log", [])
        if not redemption_logs:
            st.info("还没有兑换记录")
        else:
            total_spent = sum(r.get("cost", 0) for r in redemption_logs)
            st.caption(
                "共 "
                + str(len(redemption_logs))
                + " 次兑换，花费 "
                + str(total_spent)
                + " pts"
            )
            st.markdown("---")
            for entry in reversed(redemption_logs[-30:]):
                st.markdown(
                    "- 🕐 "
                    + str(entry.get("time", ""))
                    + " | "
                    + str(entry.get("reward_name", ""))
                    + " | -"
                    + str(entry.get("cost", 0))
                    + " pts"
                )


# ════════ Tab 5：设置 ════════
with tab5:
    st.markdown("### ⚙️ 设置")

    # -- 添加奖励 --
    st.markdown("#### ➕ 添加自定义奖励")
    c5, c6 = st.columns([2, 1])
    with c5:
        new_name = st.text_input(
            "奖励名称", placeholder="比如：买一双新鞋", key="new_r_name"
        )
    with c6:
        new_cost = st.number_input(
            "所需积分", min_value=1, value=100, step=10, key="new_r_cost"
        )
    if st.button("➕ 添加奖励", use_container_width=True):
        if new_name.strip():
            data["rewards"].append({"name": new_name.strip(), "cost": int(new_cost)})
            save_data(data)
            st.session_state.data = data
            st.success("✅ 已添加: " + new_name + " (" + str(new_cost) + " pts)")
            st.rerun()
        else:
            st.error("请输入奖励名称")

    # -- 删除奖励 --
    st.markdown("---")
    st.markdown("#### 🗑️ 删除奖励")
    if data["rewards"]:
        reward_names = [
            r["name"] + " (" + str(r["cost"]) + " pts)" for r in data["rewards"]
        ]
        del_choice = st.selectbox("选择要删除的奖励", reward_names, key="del_reward")
        if st.button("🗑️ 删除选中奖励"):
            idx = reward_names.index(del_choice)
            data["rewards"].pop(idx)
            save_data(data)
            st.session_state.data = data
            st.success("✅ 已删除")
            st.rerun()
    else:
        st.caption("暂无奖励可删除")

    # -- 危险区域 --
    st.markdown("---")
    st.markdown("#### ⚠️ 危险区域")
    col_r1, col_r2 = st.columns(2)

    with col_r1:
        if st.button("🔄 重置属性为0", type="secondary"):
            for key in data["stats"]:
                data["stats"][key] = 0
            data["total_earned"] = 0
            save_data(data)
            st.session_state.data = data
            st.success("✅ 属性已清零")
            st.rerun()

    with col_r2:
        if st.button("💣 清除所有数据", type="secondary"):
            data = new_data()
            save_data(data)
            st.session_state.data = data
            st.success("✅ 已恢复初始状态")
            st.rerun()

    # -- 备份 --
    st.markdown("---")
    st.markdown("#### 📤 备份数据")
    st.download_button(
        label="下载 JSON 备份",
        data=json.dumps(data, ensure_ascii=False, indent=2),
        file_name="life_rpg_backup_" + now_str().split(" ")[0].replace("-", "") + ".json",
        mime="application/json",
        use_container_width=True,
    )
