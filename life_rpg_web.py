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
import random
import plotly.graph_objects as go
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


def encouragement_for(attr_key):
    """根据属性随机返回一句鼓励语"""
    messages = {
        "Productivity": [
            "⚡ 你推进了现实世界的一小格。",
            "⚡ 世界上的待办少了一点点。",
            "⚡ 有一块拼图被你放回了位置。",
            "⚡ 你把想法变成了行动。",
            "⚡ 今天的进度条动了。",
            "⚡ 你没有只是想，你真的做了。",
            "⚡ 混乱被你整理出了一点秩序。",
            "⚡ 一个任务被你从脑内搬到了现实。",
            "⚡ 很好，现实被你撬动了一点。",
            "⚡ 你的行动正在累计成结果。",
            "⚡ 小小推进，也是推进。",
            "⚡ 你完成的不只是任务，是对自己的承诺。",
            "⚡ 你给未来的自己减轻了一点负担。",
            "⚡ 这一分不是数字，是你动手的证据。",
            "⚡ 你把今天往前推了一步。",
        ],
        "Creativity": [
            "💡 一个想法被你带到了世界上。",
            "💡 你给世界添了一点自己的颜色。",
            "💡 灵感没有被浪费，它被你接住了。",
            "💡 今天有一点新的东西诞生了。",
            "💡 你不是在空想，你在创造。",
            "💡 一个模糊的念头变清楚了一点。",
            "💡 你让内心的东西有了形状。",
            "💡 创造不是等状态完美，是先留下痕迹。",
            "💡 这一点表达，会在未来发光。",
            "💡 你把不可见的东西变得可见了。",
            "💡 你的脑海宇宙又开了一盏灯。",
            "💡 不需要伟大，出现就已经很好。",
            "💡 你今天也在练习把自己说出来。",
            "💡 灵感喜欢拜访正在行动的人。",
            "💡 你种下了一个可能性。",
        ],
        "Willpower": [
            "🔥 你不是没有阻力，你是带着阻力也动了。",
            "🔥 阻力出现了，但它没有赢。",
            "🔥 你今天没有被惯性完全带走。",
            "🔥 能开始，就已经很了不起。",
            "🔥 你把自己从卡住里拉出来了一点。",
            "🔥 这不是硬撑，是你在练习选择。",
            "🔥 你没有等状态完美才行动。",
            "🔥 今天的你，往前挪了一小步。",
            "🔥 你证明了：困难可以被看见，也可以被穿过。",
            "🔥 直面阻力，本身就是经验值。",
            "🔥 你在和惯性谈判，而且赢回了一点主动权。",
            "🔥 就算很难，你也没有完全放弃自己。",
            "🔥 这一步很小，但方向是对的。",
            "🔥 你没有靠情绪行动，你靠选择行动。",
            "🔥 带着不情愿也能前进，这很强。",
        ],
        "Vitality": [
            "💚 照顾自己也是主线任务。",
            "💚 你的身体收到了一个友善信号。",
            "💚 你不是机器，你值得被维护。",
            "💚 能量不是凭空来的，你正在补回来。",
            "💚 今天你没有忽略自己的身体。",
            "💚 休息、喝水、吃饭，都不是小事。",
            "💚 你在给未来的自己充电。",
            "💚 温柔对待身体，也是长期主义。",
            "💚 你把自己放回了优先级里。",
            "💚 这不是偷懒，是维护生命系统。",
            "💚 你今天也在学习照顾这个身体。",
            "💚 好好活着，本身就是重要任务。",
            "💚 你给自己加了一点续航。",
            "💚 慢下来不是失败，是恢复。",
            "💚 主线角色需要回血，你做得对。",
        ],
    }
    return random.choice(messages.get(attr_key, ["✅ 你又向前走了一点。"]))


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
for k, v in {"authed": False, "data": None, "theme": "🌌 莫兰迪蓝"}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------- 默认数据 ----------
def rebuild_stats_from_logs(data):
    """从历史日志重建真实属性值，修复被错扣的分数"""
    new_stats = {"Productivity": 0, "Creativity": 0, "Willpower": 0, "Vitality": 0}
    # 任务记录
    for a in data.get("action_log", []):
        attr = a.get("attribute")
        pts = a.get("points", 0)
        if attr in new_stats:
            new_stats[attr] += pts
    # 阻力复盘：每条 +1 意志力
    for _ in data.get("resistance_log", []):
        new_stats["Willpower"] += 1
    data["stats"] = new_stats
    return data


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
        "quick_actions": [
            {"name": "🌅 起床", "attribute": "Willpower", "points": 1},
            {"name": "💻 开始工作", "attribute": "Productivity", "points": 5},
            {"name": "✍️ 写 25 分钟", "attribute": "Creativity", "points": 5},
            {"name": "🚶 出门散步", "attribute": "Vitality", "points": 5},
            {"name": "💧 喝水", "attribute": "Vitality", "points": 1},
        ],
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
    cloud_save(data)
    local_save(data)

# ---------- 自定义样式 ----------

def on_theme_change():
    """主题切换回调：在页面重绘前更新 session_state"""
    st.session_state["theme"] = st.session_state.get("theme_select", "🌌 莫兰迪蓝")

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

# ---------- 登录后移动端布局修复 ----------
st.markdown(
    """
    <style>
    /* PC 端属性面板间距 */
    .attr-row-spacer {
        height: 2.2rem !important;
    }

    .attr-summary-spacer {
        height: 0.8rem !important;
    }

    @media (max-width: 768px) {
    
        /* 只在登录后生效：强制 columns 在手机端保持横排 */
        [data-testid="stHorizontalBlock"] {
            flex-direction: row !important;
            flex-wrap: nowrap !important;
        }
        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
            min-width: 0 !important;
            width: auto !important;
            flex: 1 1 0 !important;
        }

        /* 属性面板专用小字 */
        .attr-desc {
            font-size: 0.72rem !important;
            line-height: 1.35 !important;
            opacity: 0.72 !important;
            margin-top: 0.35rem !important;
            margin-bottom: 0.08rem !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }

        .attr-next {
            font-size: 0.70rem !important;
            line-height: 1.35 !important;
            opacity: 0.65 !important;
            margin-bottom: 0.45rem !important;
            white-space: nowrap !important;
        }

        .attr-row-spacer {
            height: 0.85rem !important;
        }

        .attr-summary-spacer {
            height: 0.35rem !important;
        }

        /* 属性面板数字稍微控制一下大小 */
        [data-testid="stMetricValue"] {
            font-size: 1.45rem !important;
        }

        [data-testid="stMetricLabel"] {
            font-size: 0.82rem !important;
        }

        /* 按钮文字略微缩小，但不要太小 */
        .stButton > button {
            font-size: 0.82rem !important;
            line-height: 1.2 !important;
            padding: 0.45rem 0.45rem !important;
        }

        .stButton > button p {
            font-size: 0.82rem !important;
            line-height: 1.2 !important;
            margin-bottom: 0 !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

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
                    st.success("✅ 已拉取云端最新数据")
                    st.rerun()
                else:
                    st.success("⚠️ 同步失败")
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

# -------- 属性面板（占位：实际渲染在文件末尾，确保即时刷新）--------
stats_placeholder = st.container()

# 供下方各 Tab 使用的积分（进入本次脚本时的值）
stats = data["stats"]
# ✅ 积分 = 累计赚的 - 累计花的（属性不再参与，永不被扣）
total_spent = sum(r.get("cost", 0) for r in data.get("redemption_log", []))
total = data.get("total_earned", 0) - total_spent

st.markdown("---")

# -------- 功能标签页 --------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["📝 记录任务", "🚧 阻力复盘", "🏆 奖励商店", "📋 历史日志", "📊 统计", "⚙️ 设置"]
)


# ════════ Tab 1：记录任务 ════════
with tab1:
    st.markdown("### 📝 记录完成的任务")
    st.caption("每完成一件事，就赚一点经验值。积少成多。")

    # ---------- 快捷记录 ----------
    st.markdown("#### 🐾 我动了一下")
    st.caption("低能量时，点一下也算数。不想写也可以，这就是一次微小启动。")

    quick_actions = data.get("quick_actions", [])

    attr_icon_map = {
        "Productivity": "⚡",
        "Creativity": "💡",
        "Willpower": "🔥",
        "Vitality": "💚",
    }

    if not quick_actions:
        st.info("还没有快捷按钮。可以去「设置」里添加常用动作。")
    else:
        # 每行 2 个按钮：手机端更稳定、更好按
        for row_start in range(0, len(quick_actions), 2):
            cols = st.columns(2)
            for j, action in enumerate(quick_actions[row_start:row_start + 2]):
                idx = row_start + j
                name = action.get("name", "未命名动作")
                attr_key = action.get("attribute", "Productivity")
                points = int(action.get("points", 1))
                icon = attr_icon_map.get(attr_key, "✨")

                with cols[j]:
                    btn_label = f"{name}\n{icon}+{points}"
                    if st.button(btn_label, key="quick_action_" + str(idx), use_container_width=True):
                        # 更新属性与积分
                        data["stats"][attr_key] += points
                        data["total_earned"] += points

                        # 写入历史日志
                        data["action_log"].append(
                            {
                                "time": now_str(),
                                "task": "快捷记录：" + name,
                                "attribute": attr_key,
                                "points": points,
                            }
                        )

                        save_data(data)
                        st.session_state.data = data

                        new_val = data["stats"][attr_key]
                        msg = encouragement_for(attr_key)
                        st.success(
                            f"✅ {name} | +{points} {attr_key}，当前 {new_val}\n\n{msg}",
                            icon="🐾"
                        )

                        if points >= 10:
                            st.balloons()

    st.markdown("---")

    # ---------- 详细记录 ----------
    with st.expander("✍️ 想写详细一点？展开详细记录", expanded=False):
        st.caption("如果你有余力，可以把这次行动记录得更具体。没有余力也没关系，快捷记录已经算数。")

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
            "做了什么？",
            placeholder="可以不写，点提交也算数。比如：完成了项目报告",
            key="task_desc",
        )

        task_date = st.date_input(
            "📅 这是哪天做的？",
            value=(datetime.utcnow() + timedelta(hours=TIMEZONE_OFFSET)).date(),
            key="task_date",
        )
        st.caption("默认是今天。如果是补记之前的事，可以改日期。")

        if st.button("✅ 提交详细记录", use_container_width=True, type="primary"):
            attr_map = {
                "⚡ 生产力 (Productivity)": "Productivity",
                "💡 创造力 (Creativity)": "Creativity",
                "🔥 意志力 (Willpower)": "Willpower",
                "💚 精力 (Vitality)": "Vitality",
            }
            diff_map = {
                "🟢 小事 → +5": 5,
                "🟡 普通 → +10": 10,
                "🔴 突破 → +20": 20,
            }

            attr_key = attr_map[attr_choice]
            points = diff_map[diff_choice]

            # 确定记录时间：补记日期用当天12:00，今天用当前时间
            today_local = (datetime.utcnow() + timedelta(hours=TIMEZONE_OFFSET)).date()
            if task_date == today_local:
                task_time = now_str()
            else:
                task_time = task_date.strftime("%Y-%m-%d") + " 12:00"

            data["stats"][attr_key] += points
            data["total_earned"] += points
            data["action_log"].append(
                {
                    "time": task_time,
                    "task": task_desc or "(未填写)",
                    "attribute": attr_key,
                    "points": points,
                }
            )
            save_data(data)
            st.session_state.data = data

            new_val = data["stats"][attr_key]
            msg = encouragement_for(attr_key)
            st.success(
                f"🎉 +{points} {attr_key}！当前 {new_val}\n\n{msg}",
                icon="✅"
            )

            if points >= 20:
                st.balloons()


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
        st.success(f"🔥 +1 Willpower | 直面阻力 {count} 次", icon="💪")
        
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

            col_info, col_btn = st.columns([3, 1])

            with col_info:
                st.markdown("🎁 **" + reward["name"] + "**")

                if can_buy:
                    cost_text = "✅ " + str(cost) + " pts"
                else:
                    cost_text = "❌ " + str(cost) + " pts（差 " + str(cost - total) + "）"

                if times > 0:
                    times_text = "已兑 " + str(times) + " 次"
                else:
                    times_text = "尚未兑换"

                st.caption(cost_text + " ｜ " + times_text)

            with col_btn:
                if can_buy:
                    if st.button("兑换", key="r_" + str(i), type="primary", use_container_width=True):
                        # ✅ 不再扣属性！只记录兑换历史
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
                else:
                    st.button("积分不够", disabled=True, key="r_" + str(i), use_container_width=True)

            st.markdown("---")


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
                
                
# ════════ Tab 5：统计 ════════
with tab5:
    st.markdown("### 📊 统计")

    # ---------- 汇总每日数据 ----------
    daily = {}
    for entry in data.get("action_log", []):
        ds = entry.get("time", "")[:10]
        if not ds:
            continue
        pts = entry.get("points", 0)
        attr = entry.get("attribute", "")
        if ds not in daily:
            daily[ds] = {"Productivity": 0, "Creativity": 0, "Willpower": 0, "Vitality": 0, "total": 0}
        if attr in daily[ds]:
            daily[ds][attr] += pts
        daily[ds]["total"] += pts

    for entry in data.get("resistance_log", []):
        ds = entry.get("time", "")[:10]
        if not ds:
            continue
        if ds not in daily:
            daily[ds] = {"Productivity": 0, "Creativity": 0, "Willpower": 0, "Vitality": 0, "total": 0}
        daily[ds]["Willpower"] += 1
        daily[ds]["total"] += 1

    today_date = (datetime.utcnow() + timedelta(hours=TIMEZONE_OFFSET)).date()

    # ---- 数据摘要 ----
    st.markdown("#### 📈 总览")

    total_days = len(daily)
    total_points = data.get("total_earned", 0)
    avg_daily = round(total_points / max(total_days, 1), 1)

    # 连续记录天数
    streak = 0
    check_date = today_date
    while True:
        ds = check_date.strftime("%Y-%m-%d")
        if ds in daily:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break

    s1, s2, s3 = st.columns(3)
    with s1:
        st.metric("📅 活跃天数", str(total_days))
    with s2:
        st.metric("📈 累计积分", str(total_points))
    with s3:
        st.metric("🔥 连续记录", str(streak) + " 天")

    s4, s5 = st.columns(2)
    with s4:
        st.metric("📊 日均积分", str(avg_daily))
    with s5:
        total_records = len(data.get("action_log", [])) + len(data.get("resistance_log", []))
        st.metric("📝 总记录数", str(total_records))

    st.markdown("---")

    # ---- 属性分布环形图 ----
    st.markdown("#### 🍩 属性分布")

    stats_total = data["stats"]
    pie_labels = ["⚡ 生产力", "💡 创造力", "🔥 意志力", "💚 精力"]
    pie_values = [
        stats_total.get("Productivity", 0),
        stats_total.get("Creativity", 0),
        stats_total.get("Willpower",  0),
        stats_total.get("Vitality",   0),
    ]
    pie_colors = ["#7a9eb0", "#c7958d", "#d48090", "#7fc5ca"]

    if sum(pie_values) > 0:
        fig_donut = go.Figure(data=[go.Pie(
            labels=pie_labels,
            values=pie_values,
            hole=0.55,
            marker=dict(colors=pie_colors),
            textinfo="label+percent",
            textposition="outside",
        )])
        fig_donut.update_layout(
            showlegend=False,
            margin=dict(t=20, b=20, l=20, r=20),
            height=280,
        )
        st.plotly_chart(fig_donut, use_container_width=True)
    else:
        st.info("还没有数据，记录一些任务后就能看到分布图了！")

    st.markdown("---")

    # ---- 每日加分柱状图 ----
    st.markdown("#### 📊 每日加分（近 14 天）")

    bar_range_choice = st.selectbox(
        "📅 查看范围",
        [7, 14, 30, 60, 90],
        index=1,
        format_func=lambda x: f"近 {x} 天",
        key="bar_range",
    )
    days_range = bar_range_choice
    bar_dates = []
    for i in range(days_range - 1, -1, -1):
        d = today_date - timedelta(days=i)
        bar_dates.append(d.strftime("%Y-%m-%d"))

    prod_vals = [daily.get(d, {}).get("Productivity", 0) for d in bar_dates]
    crea_vals = [daily.get(d, {}).get("Creativity", 0) for d in bar_dates]
    will_vals = [daily.get(d, {}).get("Willpower", 0) for d in bar_dates]
    vitl_vals = [daily.get(d, {}).get("Vitality", 0) for d in bar_dates]

    bar_labels = [d[5:] for d in bar_dates]
    bar_labels = [str(x) for x in bar_labels]  # 强制转为文本，防止 Plotly 自动解析日期

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(name="⚡ 生产力", x=bar_labels, y=prod_vals, marker_color="#7a9eb0"))
    fig_bar.add_trace(go.Bar(name="💡 创造力", x=bar_labels, y=crea_vals, marker_color="#c7958d"))
    fig_bar.add_trace(go.Bar(name="🔥 意志力", x=bar_labels, y=will_vals, marker_color="#d48090"))
    fig_bar.add_trace(go.Bar(name="💚 精力", x=bar_labels, y=vitl_vals, marker_color="#7fc5ca"))
    fig_bar.update_layout(
        barmode="stack",
        height=300,
        margin=dict(t=10, b=30, l=30, r=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        xaxis_title=None,
        yaxis_title="积分",
        xaxis=dict(type="category"),  # 当作分类轴，不自动解析日期
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

    # ---- 活动热力图 ----
    st.markdown("#### 🔥 活动热力图（近 12 周）")
    st.caption("颜色越深 = 当天获得积分越多。空白 = 没有记录。")

    heat_range_choice = st.selectbox(
        "🗓️ 热力图范围",
        [4, 8, 12, 24, 52, 104],
        index=2,
        format_func=lambda x: f"近 {x} 周",
        key="heat_range",
    )
    weeks_back = heat_range_choice
    start_monday = today_date - timedelta(days=today_date.weekday() + 7 * (weeks_back - 1))

    week_starts = []
    current = start_monday
    while current <= today_date:
        week_starts.append(current)
        current += timedelta(days=7)

    dow_labels = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    n_weeks = len(week_starts)

    z_data = [[0] * n_weeks for _ in range(7)]
    hover_text = [[""] * n_weeks for _ in range(7)]

    for wi, monday in enumerate(week_starts):
        for dow in range(7):
            d = monday + timedelta(days=dow)
            if d > today_date:
                z_data[dow][wi] = -1  # 未来日期标记
                hover_text[dow][wi] = ""
            else:
                ds = d.strftime("%Y-%m-%d")
                pts = daily.get(ds, {}).get("total", 0)
                z_data[dow][wi] = pts
                weekday_cn = ["一", "二", "三", "四", "五", "六", "日"][dow]
                hover_text[dow][wi] = f"{ds} 周{weekday_cn}<br>{int(pts)} 积分"

    x_labels = [w.strftime("%m/%d") for w in week_starts]

    fig_heat = go.Figure(data=go.Heatmap(
        z=z_data,
        x=x_labels,
        y=dow_labels,
        text=hover_text,
        hovertemplate="%{text}<extra></extra>",
        colorscale=[
            [0, "#e8e8e8"],
            [0.01, "#d4edda"],
            [0.2, "#7dcc7d"],
            [0.5, "#3da63d"],
            [1, "#1a6b1a"],
        ],
        showscale=False,
        xgap=3,
        ygap=3,
        zmin=0,
    ))
    fig_heat.update_layout(
        height=220,
        margin=dict(t=10, b=30, l=50, r=20),
    )
    st.plotly_chart(fig_heat, use_container_width=True)


# ════════ Tab 6：设置 ════════
with tab6:
    st.markdown("### ⚙️ 设置")

    # -- 快捷按钮设置 --
    st.markdown("#### 🐾 快捷按钮设置")
    st.caption("这些按钮会出现在「记录任务」里的「🐾 我动了一下」区域。适合常用动作、微启动、低能量记录。")

    attr_options = {
        "⚡ 生产力 Productivity": "Productivity",
        "💡 创造力 Creativity": "Creativity",
        "🔥 意志力 Willpower": "Willpower",
        "💚 精力 Vitality": "Vitality",
    }

    qa1, qa2, qa3 = st.columns([2, 1.4, 1])
    with qa1:
        new_q_name = st.text_input(
            "按钮名称",
            placeholder="比如：🌙 睡前收尾",
            key="new_q_name",
        )
    with qa2:
        new_q_attr_label = st.selectbox(
            "提升属性",
            list(attr_options.keys()),
            key="new_q_attr",
        )
    with qa3:
        new_q_points = st.selectbox(
            "加分",
            [1, 5, 10],
            index=1,
            key="new_q_points",
        )

    if st.button("➕ 添加快捷按钮", use_container_width=True):
        if new_q_name.strip():
            data.setdefault("quick_actions", [])
            data["quick_actions"].append(
                {
                    "name": new_q_name.strip(),
                    "attribute": attr_options[new_q_attr_label],
                    "points": int(new_q_points),
                }
            )
            save_data(data)
            st.session_state.data = data
            st.success(
                "✅ 已添加快捷按钮: "
                + new_q_name.strip()
                + " (+"
                + str(new_q_points)
                + ")"
            )
        else:
            st.error("请输入按钮名称")

    st.markdown("##### 当前快捷按钮")

    quick_actions = data.get("quick_actions", [])

    if quick_actions:
        quick_names = [
            q.get("name", "未命名动作")
            + " | "
            + q.get("attribute", "Productivity")
            + " +"
            + str(q.get("points", 1))
            for q in quick_actions
        ]

        del_q_choice = st.selectbox(
            "选择要删除的快捷按钮",
            quick_names,
            key="del_quick_action",
        )

        if st.button("🗑️ 删除选中快捷按钮"):
            idx = quick_names.index(del_q_choice)
            removed = data["quick_actions"].pop(idx)
            save_data(data)
            st.session_state.data = data
            st.success("✅ 已删除快捷按钮: " + removed.get("name", "未命名动作"))
    else:
        st.caption("暂无快捷按钮。添加几个常用动作吧。")

    st.markdown("---")
    

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
    col_r1, col_r2, col_r3 = st.columns(3)

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

    with col_r3:
        if st.button("🩹 修复属性(找回错扣分)", type="primary"):
            data = rebuild_stats_from_logs(data)
            save_data(data)
            st.session_state.data = data
            s = data["stats"]
            st.success(
                f"✅ 已从历史重建属性！\n\n"
                f"⚡{s['Productivity']} 💡{s['Creativity']} "
                f"🔥{s['Willpower']} 💚{s['Vitality']}"
            )
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

    

# ════════════════════════════════════════════════════════
#  ⚔️ 属性面板（回填到页面顶部占位，读取最新 data → 即时刷新）
# ════════════════════════════════════════════════════════
with stats_placeholder:
    _stats = data["stats"]
    _spent = sum(r.get("cost", 0) for r in data.get("redemption_log", []))
    _total = data.get("total_earned", 0) - _spent

    st.markdown("## ⚔️ 属性面板")

    _attr_display = [
        ("⚡ 生产力", "Productivity", "工作产出 · 任务完成 · 效率"),
        ("💡 创造力", "Creativity",  "新想法 · 创作表达 · 创意解题"),
        ("🔥 意志力", "Willpower",   "克服阻力 · 坚持习惯 · 自律"),
        ("💚 精力",   "Vitality",    "运动 · 休息 · 健康管理"),
    ]

    # 两行两列：手机端 2 个一行，电脑端也好看
    for _row_start in range(0, len(_attr_display), 2):
        _cols = st.columns(2)
        for _j, (_label, _key, _desc) in enumerate(_attr_display[_row_start:_row_start + 2]):
            with _cols[_j]:
                _val = _stats[_key]
                _level = _val // 50
                _next_lv = 50 - (_val % 50)
                st.metric(_label, str(_val), delta="Lv." + str(_level))
                st.progress(min((_val % 50) / 50, 1.0))

                st.markdown(
                    '<div class="attr-desc">' + _desc + '</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    '<div class="attr-next">距 Lv.'
                    + str(_level + 1)
                    + " 还需 "
                    + str(_next_lv)
                    + "</div>",
                    unsafe_allow_html=True,
                )

        # 每一行属性后加一点呼吸空间
        st.markdown('<div class="attr-row-spacer"></div>', unsafe_allow_html=True)

    # 属性面板和积分区之间再加一点空间
    st.markdown('<div class="attr-summary-spacer"></div>', unsafe_allow_html=True)

    _ci1, _ci2 = st.columns(2)

    with _ci1:
        st.markdown("💰 **当前积分: " + str(_total) + "**")
    with _ci2:
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
        
