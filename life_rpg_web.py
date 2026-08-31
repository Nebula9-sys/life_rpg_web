"""
╔══════════════════════════════════════════╗
║     🎮  Life-RPG  网页版                 ║
║     Supabase 云存档 · 账号登录 · 手机可用  ║
╚══════════════════════════════════════════╝
"""

import streamlit as st
import requests
import json
import os
import random
import hashlib
from uuid import uuid4
import plotly.graph_objects as go
from datetime import datetime

try:
    from supabase import create_client as _sb_create_client
except ImportError:
    _sb_create_client = None


# ═══════════════════════════════════════════════════
#  ⚙️ 配置区 —— 必须修改以下 2 项
# ═══════════════════════════════════════════════════

SUPABASE_URL     = ""       # 🔗 Supabase 项目 URL（与清单程序相同）
SUPABASE_ANON_KEY = ""      # 🔑 Supabase 可发布密钥（与清单程序相同）

# —— 旧存档迁移用（JSONBin → Supabase 首次登录时自动迁移，迁移成功后可删）——
JSONBIN_API_KEY  = ""                # 🔑 JSONBin API Key
JSONBIN_BIN_ID   = ""                # 📦 JSONBin Bin ID

TIMEZONE_OFFSET = 8

# ═══════════════════════════════════════════════════
#  以下代码不需要修改
# ═══════════════════════════════════════════════════

# ---------- 时间工具 ----------
from datetime import timedelta, timezone

def now_local():
    """返回当前本地时间 datetime（带时区）"""
    return datetime.now(timezone(timedelta(hours=TIMEZONE_OFFSET)))

def now_str():
    """返回带时区偏移的当前时间字符串。与 now_local() 同源，时区一致。"""
    return now_local().strftime("%Y-%m-%d %H:%M")

MOOD_OPTIONS = ["🙂", "😴", "😐", "😄", "🚀"]
VALID_MOODS = set(MOOD_OPTIONS)


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
    return random.choice(messages.get(attr_key, ["✨ 你又向前走了一点。"]))


def flash_success(message, icon="✅", position="top", balloons=False):
    """暂存成功消息，rerun 后在指定位置显示。position: top/record/checkin/redeem/settings"""
    st.session_state["flash_msg"] = {
        "type": "success", "message": message, "icon": icon,
        "position": position, "balloons": balloons,
    }


def show_flash_message(position="top"):
    """在指定位置显示暂存的消息（显示后自动清除；balloons 也在此时触发，避免被 rerun 冲掉）"""
    flash = st.session_state.get("flash_msg")
    if not flash or flash.get("position", "top") != position:
        return
    st.session_state.pop("flash_msg", None)
    if flash.get("balloons"):
        st.balloons()
    if flash["type"] == "success":
        st.success(flash["message"], icon=flash.get("icon", "✅"))
    elif flash["type"] == "info":
        st.info(flash["message"], icon=flash.get("icon", "ℹ️"))


VALID_ATTRS = {"Productivity", "Creativity", "Willpower", "Vitality"}

# ---------- 记录来源常量（字符串值与旧存档保持一致） ----------
SOURCE_TASK    = "任务"
SOURCE_ACH     = "成就"
SOURCE_CHECKIN = "签到"


def calc_streak(date_set, today=None):
    """从今天（或昨天）往回数连续出现在 date_set 中的天数"""
    today = today or now_local().date()
    check = today
    if today.strftime("%Y-%m-%d") not in date_set:
        check = today - timedelta(days=1)
    streak = 0
    while True:
        if check.strftime("%Y-%m-%d") in date_set:
            streak += 1
            check -= timedelta(days=1)
        else:
            break
    return streak


# ---------- 记录唯一 ID（云存档合并去重用） ----------
def new_entry_id():
    return uuid4().hex[:12]


def _stable_entry_id(entry):
    """按内容哈希生成确定性 ID：同一条旧记录在任何设备上算出相同值"""
    payload = {k: v for k, v in entry.items() if k != "id"}
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.md5(raw).hexdigest()[:12]


def _ensure_ids(entries):
    """给没有 id 的旧记录补 ID；内容完全相同的重复条目按出现次序编号区分"""
    seen = {}
    for e in entries:
        if not isinstance(e, dict) or e.get("id"):
            continue
        base = _stable_entry_id(e)
        n = seen.get(base, 0)
        seen[base] = n + 1
        e["id"] = base if n == 0 else f"{base}-{n}"


# ---------- 统一加分 / 删除回收 ----------
def add_points(data, attr_key, points, task, source=SOURCE_TASK, mood=None, backdated=None, time_str=None):
    """统一加分入口：更新属性/累计积分并写入行为日志，返回新日志条目"""
    if attr_key in data.get("stats", {}):
        data["stats"][attr_key] += points
    data["total_earned"] = data.get("total_earned", 0) + points
    entry = {
        "id": new_entry_id(),
        "time": time_str or now_str(),
        "task": task,
        "attribute": attr_key if attr_key in VALID_ATTRS else "",
        "points": points,
        "source": source,
    }
    if mood is not None:
        entry["mood"] = mood
    if backdated is not None:
        entry["backdated"] = backdated
    data.setdefault("action_log", []).append(entry)
    return entry


def remove_action_entry(data, idx):
    """删除一条行为日志并回收属性/积分；签到条目同时移除当天签到记录"""
    entry = data["action_log"].pop(idx)
    pts = entry.get("points", 0)
    attr = entry.get("attribute", "")
    if attr in data.get("stats", {}):
        data["stats"][attr] -= pts
    data["total_earned"] = max(data.get("total_earned", 0) - pts, 0)
    if entry.get("source", SOURCE_TASK) == SOURCE_CHECKIN:
        ds = entry.get("time", "")[:10]
        if ds in data.get("checkin_log", []):
            data["checkin_log"].remove(ds)
        if ds in data.get("repaired_checkins", []):
            data["repaired_checkins"].remove(ds)


def remove_resistance_entry(data, idx):
    """删除一条阻力复盘并回收意志力/积分"""
    data["resistance_log"].pop(idx)
    data["stats"]["Willpower"] = max(data["stats"].get("Willpower", 0) - 1, 0)
    data["total_earned"] = max(data.get("total_earned", 0) - 1, 0)


# ---------- 成就系统 ----------
ACHIEVEMENT_DEFS = [
    # 累积型
    {"id": "hundred_pts",      "name": "💯 百分起步",  "desc": "总积分突破 100",       "category": "cumulative", "bonus": 20},
    {"id": "five_hundred_pts", "name": "🏆 五百达成",  "desc": "总积分突破 500",       "category": "cumulative", "bonus": 30},
    {"id": "thousand_pts",     "name": "🌟 千分玩家",  "desc": "总积分突破 1000",      "category": "cumulative", "bonus": 50},
    {"id": "five_thousand_pts","name": "💎 万分之路",  "desc": "总积分突破 5000",      "category": "cumulative", "bonus": 60},
    {"id": "week_active",      "name": "🗓️ 一周坚持",  "desc": "活跃天数满 7 天",      "category": "cumulative", "bonus": 20},
    {"id": "month_active",     "name": "📅 月度达人",  "desc": "活跃天数满 30 天",     "category": "cumulative", "bonus": 40},
    {"id": "hundred_active",   "name": "💯 百日筑基",  "desc": "活跃天数满 100 天",    "category": "cumulative", "bonus": 60},
    {"id": "resistance_10",    "name": "🧠 直面者",    "desc": "阻力复盘满 10 次",     "category": "cumulative", "bonus": 20},
    {"id": "resistance_30",    "name": "💪 阻力克星",  "desc": "阻力复盘满 30 次",     "category": "cumulative", "bonus": 40},
    {"id": "redeem_5",         "name": "🎁 懂得犒赏",  "desc": "奖励兑换满 5 次",      "category": "cumulative", "bonus": 15},
    {"id": "redeem_10",        "name": "🏆 生活达人",  "desc": "奖励兑换满 10 次",     "category": "cumulative", "bonus": 30},
    # 单日型
    {"id": "daily_30",         "name": "⚡ 小有产出",  "desc": "单日得分突破 30",      "category": "daily",      "bonus": 20},
    {"id": "daily_50",         "name": "🔥 产出爆发",  "desc": "单日得分突破 50",      "category": "daily",      "bonus": 40},
    {"id": "daily_100",        "name": "💥 超级加倍",  "desc": "单日得分突破 100",     "category": "daily",      "bonus": 50},
    {"id": "daily_balanced",   "name": "⚖️ 均衡发展",  "desc": "单日四维属性全部有得分","category": "daily",      "bonus": 30},
    {"id": "daily_5_records",  "name": "📝 忙碌一天",  "desc": "单日记录 5 条以上",    "category": "daily",      "bonus": 25},
    # 特殊行为型
    {"id": "first_task",       "name": "🎮 启程",      "desc": "第一次记录任务",       "category": "special",    "bonus": 20},
    {"id": "first_resistance", "name": "🧠 勇敢直面",  "desc": "第一次阻力复盘",       "category": "special",    "bonus": 20},
    {"id": "first_redeem",     "name": "🎁 首次犒赏",  "desc": "第一次兑换奖励",       "category": "special",    "bonus": 20},
    {"id": "first_backdate",   "name": "📅 时光回溯",  "desc": "第一次补记过去日期的任务","category": "special",  "bonus": 20},
    {"id": "streak_7",         "name": "🔥 一周不断",  "desc": "连续记录 7 天",        "category": "special",    "bonus": 40},
    {"id": "streak_30",        "name": "💎 月度连击",  "desc": "连续记录 30 天",       "category": "special",    "bonus": 60},
    {"id": "stat_100",         "name": "⭐ 百分属性",  "desc": "任一属性突破 100",     "category": "special",    "bonus": 25},
    {"id": "stat_500",         "name": "🌟 属性大师",  "desc": "任一属性突破 500",     "category": "special",    "bonus": 50},
    # —— 心情系列 ——
    {"id": "mood_10",           "name": "📝 心情记录员",  "desc": "记录 10 次心情",       "category": "mood",      "bonus": 15},
    {"id": "mood_50",           "name": "🎭 心情达人",    "desc": "记录 50 次心情",       "category": "mood",      "bonus": 30},
    {"id": "mood_streak_7",     "name": "📅 心情连续",    "desc": "连续 7 天记录心情",     "category": "mood",      "bonus": 20},
    # —— 全属性里程碑 ——
    {"id": "all_attr_lv10",     "name": "🎯 全属性Lv10",  "desc": "四项属性均达 Lv10",     "category": "milestone", "bonus": 50},
    {"id": "all_attr_lv15",     "name": "🎯 全属性Lv15",  "desc": "四项属性均达 Lv15",     "category": "milestone", "bonus": 80},
    {"id": "all_attr_lv20",     "name": "🎯 全属性Lv20",  "desc": "四项属性均达 Lv20",     "category": "milestone", "bonus": 120},
    {"id": "all_attr_lv30",     "name": "🎯 全属性Lv30",  "desc": "四项属性均达 Lv30",     "category": "milestone", "bonus": 200},
    {"id": "all_attr_lv40",     "name": "🎯 全属性Lv40",  "desc": "四项属性均达 Lv40",     "category": "milestone", "bonus": 400},
    # —— 活跃里程碑 ——
    {"id": "active_50",         "name": "📆 活跃50天",    "desc": "累计活跃 50 天",       "category": "cumulative","bonus": 30},
    {"id": "active_150",        "name": "📆 活跃150天",   "desc": "累计活跃 150 天",      "category": "cumulative","bonus": 60},
    {"id": "active_299",        "name": "📆 活跃299天",   "desc": "累计活跃 299 天",      "category": "cumulative","bonus": 80},
    {"id": "active_365",        "name": "🗓️ 活跃365天",   "desc": "累计活跃 365 天",      "category": "cumulative","bonus": 100},
    # —— 阻力复盘进阶 ——
    {"id": "resistance_50",     "name": "🛡️ 阻力五十",   "desc": "阻力复盘满 50 次",     "category": "cumulative","bonus": 25},
    {"id": "resistance_100",    "name": "🛡️ 阻力百条",   "desc": "阻力复盘满 100 次",    "category": "cumulative","bonus": 40},
    {"id": "resistance_streak_7","name": "📋 连续阻力7天","desc": "连续 7 天做阻力复盘",   "category": "daily",     "bonus": 20},
    # —— 积分里程碑 ——
    {"id": "two_thousand_pts",  "name": "💰 两千分",      "desc": "总积分突破 2000",      "category": "cumulative","bonus": 30},
    {"id": "ten_thousand_pts",  "name": "🏦 万分大佬",    "desc": "总积分突破 10000",     "category": "cumulative","bonus": 150},
    # —— 兑换消耗 ——
    {"id": "consumed_500",      "name": "🛒 消耗500分",   "desc": "兑换累计消耗 500",     "category": "cumulative","bonus": 25},
    {"id": "consumed_1000",     "name": "🛒 消耗1000分",  "desc": "兑换累计消耗 1000",    "category": "cumulative","bonus": 40},
    {"id": "consumed_2000",     "name": "🛒 消耗2000分",  "desc": "兑换累计消耗 2000",    "category": "cumulative","bonus": 60},
    {"id": "consumed_5000",     "name": "🛒 消耗5000分",  "desc": "兑换累计消耗 5000",    "category": "cumulative","bonus": 100},
    # —— 其他 ——
    {"id": "weekly_report_4",   "name": "📊 周报连续4周","desc": "连续 4 周生成周报",     "category": "special",   "bonus": 20},
    {"id": "weekly_200",        "name": "⚡ 单周200分",   "desc": "一周内总得分超 200",    "category": "daily",     "bonus": 25},
    {"id": "monthly_20",        "name": "🌙 月度20天",    "desc": "单月活跃超 20 天",     "category": "daily",     "bonus": 30},
    {"id": "comeback_3day",     "name": "🔄 东山再起",    "desc": "断签 3 天后重新记录",   "category": "special",   "bonus": 10},
    # —— 签到系列 ——
    {"id": "checkin_30",        "name": "📅 签到30天",   "desc": "连续签到 30 天",        "category": "checkin",   "bonus": 20},
    {"id": "checkin_50",        "name": "📆 签到50天",   "desc": "连续签到 50 天",        "category": "checkin",   "bonus": 20},
    {"id": "checkin_100",       "name": "💯 签到100天",  "desc": "连续签到 100 天",       "category": "checkin",   "bonus": 20},
    {"id": "checkin_222",       "name": "🎯 签到222天",  "desc": "连续签到 222 天",       "category": "checkin",   "bonus": 20},
    {"id": "checkin_total_100", "name": "📦 累计100天",  "desc": "累计签到 100 天",       "category": "checkin",   "bonus": 20},
    {"id": "checkin_total_222", "name": "📦 累计222天",  "desc": "累计签到 222 天",       "category": "checkin",   "bonus": 20},
    {"id": "checkin_total_365", "name": "🗓️ 累计365天",  "desc": "累计签到 365 天",       "category": "checkin",   "bonus": 100},
]


def check_achievements(data, retroactive=False):
    """检查并解锁成就。retroactive=True 时标记为追溯解锁（仍发 bonus 积分）。"""
    action_log = data.get("action_log", [])
    resistance_log = data.get("resistance_log", [])
    redemption_log = data.get("redemption_log", [])

    total_earned = data.get("total_earned", 0)

    # streak 计算（含 action_log + resistance_log）
    daily_set = set(e.get("time", "")[:10] for e in action_log if e.get("time"))
    daily_set |= set(e.get("time", "")[:10] for e in resistance_log if e.get("time"))
    active_days = len(daily_set)

    today_str = now_local().strftime("%Y-%m-%d")
    today_actions = [e for e in action_log if e.get("time", "")[:10] == today_str and e.get("source", SOURCE_TASK) not in (SOURCE_ACH, SOURCE_CHECKIN)]
    today_resist = [r for r in resistance_log if r.get("time", "")[:10] == today_str]
    today_total = sum(e.get("points", 0) for e in today_actions) + len(today_resist)
    today_attrs = set(e.get("attribute", "") for e in today_actions if e.get("points", 0) > 0)
    if today_resist:
        today_attrs.add("Willpower")
    all_four = all(a in today_attrs for a in ["Productivity", "Creativity", "Willpower", "Vitality"])

    today_date = now_local().date()
    streak = calc_streak(daily_set, today_date)

    stat_vals = [v for v in data.get("stats", {}).values() if isinstance(v, (int, float))]
    max_stat = max(stat_vals) if stat_vals else 0
    min_stat = min(stat_vals) if stat_vals else 0
    has_backdated = any(e.get("backdated", False) for e in action_log)

    # —— 新成就变量 ——
    # 心情统计
    mood_entries = [e for e in action_log if e.get("mood")]
    mood_count = len(mood_entries)
    mood_dates = set(e.get("time", "")[:10] for e in mood_entries if e.get("time"))
    mood_streak = calc_streak(mood_dates, today_date)

    # 阻力复盘连续天数
    resist_dates = set(r.get("time", "")[:10] for r in resistance_log if r.get("time"))
    resistance_streak = calc_streak(resist_dates, today_date)

    # 兑换总消耗
    total_consumed = sum(r.get("cost", 0) for r in redemption_log)

    # 周报连续周数
    reports = data.get("reports", [])
    week_mondays = []
    for r in reports:
        if r.get("type") == "weekly" and r.get("period_key"):
            pk = r["period_key"]
            try:
                parts = pk.split("-W")
                if len(parts) == 2:
                    year, week = int(parts[0]), int(parts[1])
                    monday_date = datetime.strptime(f"{year}-W{week}-1", "%Y-W%W-%w").date()
                    week_mondays.append(monday_date)
            except (ValueError, IndexError):
                continue
    week_mondays = sorted(set(week_mondays), reverse=True)
    weekly_report_streak = 0
    if week_mondays:
        weekly_report_streak = 1
        for i in range(1, len(week_mondays)):
            if (week_mondays[i - 1] - week_mondays[i]).days == 7:
                weekly_report_streak += 1
            else:
                break

    # 本周总得分
    monday = today_date - timedelta(days=today_date.weekday())
    monday_str = monday.strftime("%Y-%m-%d")
    this_week_total = sum(
        e.get("points", 0) for e in action_log
        if e.get("time", "")[:10] >= monday_str
        and e.get("source", SOURCE_TASK) not in (SOURCE_ACH, SOURCE_CHECKIN)
    ) + sum(
        1 for r in resistance_log
        if r.get("time", "")[:10] >= monday_str
    )

    # 本月活跃天数
    month_prefix = today_str[:7]
    monthly_active_days = sum(1 for d in daily_set if d[:7] == month_prefix)

    # 签到统计
    checkin_streak = get_checkin_streak(data)
    total_checkin_days = len(data.get("checkin_log", []))

    # 东山再起：检查是否有 3+ 天的空档后重新记录
    has_comeback = False
    if len(daily_set) >= 2:
        sorted_dates = sorted(daily_set)
        for i in range(1, len(sorted_dates)):
            try:
                prev_d = datetime.strptime(sorted_dates[i - 1], "%Y-%m-%d").date()
                curr_d = datetime.strptime(sorted_dates[i], "%Y-%m-%d").date()
                if (curr_d - prev_d).days >= 3:
                    has_comeback = True
                    break
            except ValueError:
                continue

    def build_conditions():
        te = data.get("total_earned", 0)
        return {
            "hundred_pts":       te >= 100,
            "five_hundred_pts":  te >= 500,
            "thousand_pts":      te >= 1000,
            "five_thousand_pts": te >= 5000,
            "week_active":       active_days >= 7,
            "month_active":      active_days >= 30,
            "hundred_active":    active_days >= 100,
            "resistance_10":     len(resistance_log) >= 10,
            "resistance_30":     len(resistance_log) >= 30,
            "redeem_5":          len(redemption_log) >= 5,
            "redeem_10":         len(redemption_log) >= 10,
            "daily_30":          today_total >= 30,
            "daily_50":          today_total >= 50,
            "daily_100":         today_total >= 100,
            "daily_balanced":    all_four,
            "daily_5_records":   len(today_actions) + len(today_resist) >= 5,
            "first_task":        len([e for e in action_log if e.get("source", SOURCE_TASK) not in (SOURCE_ACH, SOURCE_CHECKIN)]) >= 1,
            "first_resistance":  len(resistance_log) >= 1,
            "first_redeem":      len(redemption_log) >= 1,
            "first_backdate":    has_backdated,
            "streak_7":          streak >= 7,
            "streak_30":         streak >= 30,
            "stat_100":          max_stat >= 100,
            "stat_500":          max_stat >= 500,
            # —— 心情系列 ——
            "mood_10":           mood_count >= 10,
            "mood_50":           mood_count >= 50,
            "mood_streak_7":     mood_streak >= 7,
            # —— 全属性里程碑 ——
            "all_attr_lv10":     min_stat >= 500,
            "all_attr_lv15":     min_stat >= 750,
            "all_attr_lv20":     min_stat >= 1000,
            "all_attr_lv30":     min_stat >= 1500,
            "all_attr_lv40":     min_stat >= 2000,
            # —— 活跃里程碑 ——
            "active_50":         active_days >= 50,
            "active_150":        active_days >= 150,
            "active_299":        active_days >= 299,
            "active_365":        active_days >= 365,
            # —— 阻力复盘进阶 ——
            "resistance_50":     len(resistance_log) >= 50,
            "resistance_100":    len(resistance_log) >= 100,
            "resistance_streak_7": resistance_streak >= 7,
            # —— 积分里程碑 ——
            "two_thousand_pts":  te >= 2000,
            "ten_thousand_pts":  te >= 10000,
            # —— 兑换消耗 ——
            "consumed_500":      total_consumed >= 500,
            "consumed_1000":     total_consumed >= 1000,
            "consumed_2000":     total_consumed >= 2000,
            "consumed_5000":     total_consumed >= 5000,
            # —— 其他 ——
            "weekly_report_4":   weekly_report_streak >= 4,
            "weekly_200":        this_week_total >= 200,
            "monthly_20":        monthly_active_days >= 20,
            "comeback_3day":     has_comeback,
            # —— 签到系列 ——
            "checkin_30":        checkin_streak >= 30,
            "checkin_50":        checkin_streak >= 50,
            "checkin_100":       checkin_streak >= 100,
            "checkin_222":       checkin_streak >= 222,
            "checkin_total_100": total_checkin_days >= 100,
            "checkin_total_222": total_checkin_days >= 222,
            "checkin_total_365": total_checkin_days >= 365,
        }

    newly_unlocked = []
    changed = True
    while changed:
        changed = False
        conditions = build_conditions()
        for ach in data.get("achievements", []):
            if ach["unlocked"]:
                continue
            if conditions.get(ach["id"], False):
                ach["unlocked"] = True
                ach["unlocked_time"] = now_str()
                entry = add_points(data, "", ach["bonus"], "🏅 成就解锁：" + ach["name"], source=SOURCE_ACH)
                entry["retroactive"] = retroactive
                newly_unlocked.append(ach)
                changed = True

    return newly_unlocked


# ---------- 每日签到系统 ----------
def get_checkin_streak(data):
    """计算签到连续天数（从今天或昨天往回数）"""
    checkin_set = set(data.get("checkin_log", []))
    if not checkin_set:
        return 0
    return calc_streak(checkin_set)


def get_checkin_reward(streak):
    """签到奖励：第1-4天 +2，第5天起 +5"""
    if streak <= 0:
        return 0
    if streak <= 4:
        return 2
    return 5


def has_checked_in_today(data):
    """检查今天是否已签到"""
    today = now_local().strftime("%Y-%m-%d")
    return today in set(data.get("checkin_log", []))


# ---------- 补签卡 ----------
def real_checkin_count(data):
    """真实签到天数（补签的日期不计入送卡进度）"""
    checkins = set(data.get("checkin_log", []))
    repaired = set(data.get("repaired_checkins", [])) & checkins
    return len(checkins) - len(repaired)


def available_checkin_cards(data):
    """当前可用补签卡 = 累计真实签到每满 30 天送 1 张 + 已购买 - 已使用"""
    cards = data.get("checkin_cards", {})
    return max(0, real_checkin_count(data) // 30 + int(cards.get("bought", 0)) - int(cards.get("used", 0)))


def find_repairable_gap(data, max_days=7):
    """返回最近一个可用补签卡修复的断签日期（YYYY-MM-DD），没有则 None。
    规则：只补"紧挨当前连续签到链的第一个缺口"（从最近端补起，每补一张连续天数立刻 +1），
    且该日期须在最近 max_days 天内；从未签到过则不可补。"""
    today = now_local().date()
    checkin_set = set(data.get("checkin_log", []))
    if not checkin_set:
        return None                     # 从未签到，无可补之说
    earliest = today - timedelta(days=max_days)
    # 从存活链顶端（今天或昨天）往回走，第一个没签到的日子就是补签目标
    d = today if today.strftime("%Y-%m-%d") in checkin_set else today - timedelta(days=1)
    while d >= earliest and d.strftime("%Y-%m-%d") in checkin_set:
        d -= timedelta(days=1)
    if d < earliest:
        return None                     # 连续签到一直延伸到窗口外，没有缺口
    ds = d.strftime("%Y-%m-%d")
    return None if ds in checkin_set else ds


# ---------- 称号系统 ----------
TITLE_DEFS = [
    # (最低总等级, 称号)  总等级 = total_earned // 100
    (0,  "🌱 新手冒险者"),
    (3,  "⚡ 行动派"),
    (8,  "🔥 自律学徒"),
    (15, "🛡️ 坚持者"),
    (25, "🌟 节奏大师"),
    (40, "👑 生活大师"),
    (60, "💎 传奇玩家"),
]
ATTR_TITLES = {
    "Productivity": "⚡ 效率先锋",
    "Creativity":   "💡 创造者",
    "Willpower":    "🔥 意志坚定者",
    "Vitality":     "💚 活力满满",
}


def get_titles(data):
    """返回 (主称号, 属性称号)。主称号看总等级，属性称号看最高属性。"""
    lv = data.get("total_earned", 0) // 100
    main = TITLE_DEFS[0][1]
    for min_lv, t in TITLE_DEFS:
        if lv >= min_lv:
            main = t
    stats = {k: v for k, v in data.get("stats", {}).items() if isinstance(v, (int, float))}
    attr_title = ATTR_TITLES.get(max(stats, key=stats.get)) if stats else None
    return main, attr_title


# ---------- 周报 / 月报生成 ----------
def _get_daily_map(data):
    """从 action_log + resistance_log 构建每日聚合字典"""
    daily = {}
    for entry in data.get("action_log", []):
        ds = entry.get("time", "")[:10]
        if len(ds) != 10 or ds[4] != "-" or ds[7] != "-":
            continue
        if ds not in daily:
            daily[ds] = {"Productivity": 0, "Creativity": 0, "Willpower": 0, "Vitality": 0, "total": 0, "count": 0}
        attr = entry.get("attribute", "")
        pts = entry.get("points", 0)
        if attr in daily[ds]:
            daily[ds][attr] += pts
        daily[ds]["total"] += pts
        daily[ds]["count"] += 1
    for entry in data.get("resistance_log", []):
        ds = entry.get("time", "")[:10]
        if len(ds) != 10 or ds[4] != "-" or ds[7] != "-":
            continue
        if ds not in daily:
            daily[ds] = {"Productivity": 0, "Creativity": 0, "Willpower": 0, "Vitality": 0, "total": 0, "count": 0}
        daily[ds]["Willpower"] += 1
        daily[ds]["total"] += 1
    return daily


def generate_weekly_report(data, as_of_date=None):
    """生成周报文本（纯模板，零 token）。as_of_date 默认今天，传上周日期则生成上周报告。"""
    daily = _get_daily_map(data)
    today = as_of_date or now_local().date()

    # 本周（周一到 as_of_date）
    monday = today - timedelta(days=today.weekday())
    week_days = [(monday + timedelta(days=i)) for i in range(7)]
    week_strs = [d.strftime("%Y-%m-%d") for d in week_days if d <= today]

    # 上周
    last_monday = monday - timedelta(days=7)
    last_sunday = monday - timedelta(days=1)
    last_week_strs = [(last_monday + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

    # 本周数据
    week_total = sum(daily.get(ds, {}).get("total", 0) for ds in week_strs)
    week_count = sum(daily.get(ds, {}).get("count", 0) for ds in week_strs)
    week_attrs = {"Productivity": 0, "Creativity": 0, "Willpower": 0, "Vitality": 0}
    for ds in week_strs:
        for k in week_attrs:
            week_attrs[k] += daily.get(ds, {}).get(k, 0)

    # 上周数据
    last_week_total = sum(daily.get(ds, {}).get("total", 0) for ds in last_week_strs)
    diff = week_total - last_week_total
    diff_pct = round(diff / max(last_week_total, 1) * 100) if last_week_total > 0 else 0

    # 最活跃的一天
    best_day = None
    best_pts = 0
    for ds in week_strs:
        pts = daily.get(ds, {}).get("total", 0)
        if pts > best_pts:
            best_pts = pts
            best_day = ds

    # 阻力复盘
    week_resist = [r for r in data.get("resistance_log", []) if r.get("time", "")[:10] in week_strs]
    resist_reasons = {}
    for r in week_resist:
        reason = r.get("reason", "未知")
        resist_reasons[reason] = resist_reasons.get(reason, 0) + 1
    top_reason = max(resist_reasons, key=resist_reasons.get) if resist_reasons else None

    # 趋势箭头
    if diff > 0:
        trend = f"比上周 +{diff} pts ↑"
    elif diff < 0:
        trend = f"比上周 {diff} pts ↓"
    else:
        trend = "与上周持平"

    lines = []
    lines.append(f"📊 本周小结（{week_strs[0]} ~ {week_strs[-1]}）")
    lines.append("─" * 40)
    lines.append(f"本周得分：{week_total} pts（{trend}）")
    if best_day:
        try:
            weekday_cn = ["一", "二", "三", "四", "五", "六", "日"][datetime.strptime(best_day, "%Y-%m-%d").weekday()]
            lines.append(f"最活跃：周{weekday_cn}（{best_pts} pts）")
        except (ValueError, TypeError):
            lines.append(f"最活跃：{best_day}（{best_pts} pts）")
    lines.append(f"记录次数：{week_count} 次")
    lines.append("")

    attr_labels = {"Productivity": "⚡ 生产力", "Creativity": "💡 创造力", "Willpower": "🔥 意志力", "Vitality": "💚 精力"}
    lines.append("属性分布：")
    for k, label in attr_labels.items():
        pct = round(week_attrs[k] / max(week_total, 1) * 100)
        lines.append(f"  {label} {week_attrs[k]} pts ({pct}%)")
    lines.append("")

    if week_resist:
        lines.append(f"阻力复盘：{len(week_resist)} 次")
        if top_reason:
            lines.append(f"  主要原因：{top_reason}（{resist_reasons[top_reason]} 次）")
        strategies = [r.get("strategy", "") for r in week_resist if r.get("strategy", "") and r.get("strategy", "") != "(未填写)"]
        if strategies:
            cleaned = [s.replace("「", "『").replace("」", "』") for s in strategies[:3]]
            lines.append(f"  策略摘要：「{'」「'.join(cleaned)}」")
    else:
        lines.append("阻力复盘：本周无记录")

    return "\n".join(lines)


def generate_monthly_report(data):
    """生成本月月报文本"""
    daily = _get_daily_map(data)
    today = now_local().date()

    month_start = today.replace(day=1)
    month_strs = []
    d = month_start
    while d <= today:
        month_strs.append(d.strftime("%Y-%m-%d"))
        d += timedelta(days=1)

    # 上月
    if month_start.month == 1:
        last_month_start = month_start.replace(year=month_start.year - 1, month=12)
    else:
        last_month_start = month_start.replace(month=month_start.month - 1)
    last_month_end = month_start - timedelta(days=1)
    last_month_strs = []
    d = last_month_start
    while d <= last_month_end:
        last_month_strs.append(d.strftime("%Y-%m-%d"))
        d += timedelta(days=1)

    month_total = sum(daily.get(ds, {}).get("total", 0) for ds in month_strs)
    last_month_total = sum(daily.get(ds, {}).get("total", 0) for ds in last_month_strs)
    diff = month_total - last_month_total

    month_attrs = {"Productivity": 0, "Creativity": 0, "Willpower": 0, "Vitality": 0}
    for ds in month_strs:
        for k in month_attrs:
            month_attrs[k] += daily.get(ds, {}).get(k, 0)

    active_days = sum(1 for ds in month_strs if ds in daily)
    month_resist = [r for r in data.get("resistance_log", []) if r.get("time", "")[:10] in month_strs]

    # 最活跃的一天
    best_day = None
    best_pts = 0
    for ds in month_strs:
        pts = daily.get(ds, {}).get("total", 0)
        if pts > best_pts:
            best_pts = pts
            best_day = ds

    # 阻力复盘统计
    resist_reasons = {}
    for r in month_resist:
        reason = r.get("reason", "未知")
        resist_reasons[reason] = resist_reasons.get(reason, 0) + 1
    top_reason = max(resist_reasons, key=resist_reasons.get) if resist_reasons else None

    if diff > 0:
        trend = f"比上月 +{diff} pts ↑"
    elif diff < 0:
        trend = f"比上月 {diff} pts ↓"
    else:
        trend = "与上月持平"

    lines = []
    lines.append(f"📅 月度报告（{month_start.strftime('%Y-%m')}）")
    lines.append("─" * 40)
    lines.append(f"本月得分：{month_total} pts（{trend}）")
    lines.append(f"活跃天数：{active_days} / {len(month_strs)} 天")
    lines.append(f"日均积分：{round(month_total / max(len(month_strs), 1), 1)}")
    if best_day:
        try:
            weekday_cn = ["一", "二", "三", "四", "五", "六", "日"][datetime.strptime(best_day, "%Y-%m-%d").weekday()]
            lines.append(f"最活跃：周{weekday_cn} {best_day}（{best_pts} pts）")
        except (ValueError, TypeError):
            lines.append(f"最活跃：{best_day}（{best_pts} pts）")
    lines.append("")

    attr_labels = {"Productivity": "⚡ 生产力", "Creativity": "💡 创造力", "Willpower": "🔥 意志力", "Vitality": "💚 精力"}
    lines.append("属性分布：")
    for k, label in attr_labels.items():
        pct = round(month_attrs[k] / max(month_total, 1) * 100)
        lines.append(f"  {label} {month_attrs[k]} pts ({pct}%)")
    lines.append("")

    if month_resist:
        lines.append(f"阻力复盘：{len(month_resist)} 次")
        if top_reason:
            lines.append(f"  主要原因：{top_reason}（{resist_reasons[top_reason]} 次）")
        strategies = [r.get("strategy", "") for r in month_resist if r.get("strategy", "") and r.get("strategy", "") != "(未填写)"]
        if strategies:
            cleaned = [s.replace("「", "『").replace("」", "』") for s in strategies[:3]]
            lines.append(f"  策略摘要：「{'」「'.join(cleaned)}」")
    else:
        lines.append("阻力复盘：本月无记录")

    return "\n".join(lines)


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

SB_URL        = get_secret("SUPABASE_URL", SUPABASE_URL)
SB_KEY        = get_secret("SUPABASE_ANON_KEY", SUPABASE_ANON_KEY)
JSONBIN_KEY   = get_secret("JSONBIN_API_KEY", JSONBIN_API_KEY)
JSONBIN_BIN   = get_secret("JSONBIN_BIN_ID", JSONBIN_BIN_ID)

# ---------- Session State 初始化 ----------
for k, v in {"authed": False, "data": None, "theme": "🌌 莫兰迪蓝", "uid": None, "user_email": ""}.items():
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
    # 同时重建 total_earned（任务积分 + 阻力复盘积分 + 成就 bonus）
    task_pts = sum(a.get("points", 0) for a in data.get("action_log", []))
    resist_pts = len(data.get("resistance_log", []))
    data["total_earned"] = task_pts + resist_pts
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
        "rev": 0,               # 存档版本号（每次保存 +1）
        "saved_at": "",         # 最后一次保存时间
        "reports": [],          # 周报/月报存档
        "checkin_log": [],      # 每日签到日期记录 ["YYYY-MM-DD", ...]
        "checkin_cards": {"bought": 0, "used": 0, "earned_seen": 0},  # 补签卡：已购/已用/已结算的赠送进度
        "repaired_checkins": [],   # 用补签卡补上的日期（不计送卡进度、不补发当日积分）
        "card_log": [],        # 补签卡 获赠/购买/使用 流水
        "achievements": [
            {**a, "unlocked": False, "unlocked_time": None}
            for a in ACHIEVEMENT_DEFS
        ],
        "quick_actions": [
            {"name": "🌅 起床", "attribute": "Willpower", "points": 1},
            {"name": "💻 开始工作", "attribute": "Productivity", "points": 5},
            {"name": "✍️ 写 25 分钟", "attribute": "Creativity", "points": 5},
            {"name": "🚶 出门散步", "attribute": "Vitality", "points": 5},
            {"name": "💧 喝水", "attribute": "Vitality", "points": 1},
        ],
    }



# ---------- 云存档（Supabase） ----------
LOCAL_FILE = "life_rpg_save.json"
SB_TABLE = "life_rpg_data"


@st.cache_resource
def get_sb_client():
    """全局缓存的 Supabase 客户端（rerun 不重建，auth session 存于其中）"""
    if _sb_create_client is None or not SB_URL or not SB_KEY:
        return None
    try:
        return _sb_create_client(SB_URL, SB_KEY)
    except Exception as e:
        print(f"[supabase init] {e!r}")
        return None


def _sb_refresh_auth():
    """token 失效时：先试 refresh，失败再用 session 内凭据静默重登"""
    sb = get_sb_client()
    if sb is None:
        return False
    try:
        sb.auth.refresh_session()
        return True
    except Exception:
        email = st.session_state.get("sb_email")
        pwd = st.session_state.get("sb_pwd")
        if not email or not pwd:
            return False
        try:
            sb.auth.sign_in_with_password({"email": email, "password": pwd})
            return True
        except Exception as e:
            print(f"[supabase re-auth] {e!r}")
            return False


def _sb_is_auth_error(e):
    s = str(e).lower()
    return any(k in s for k in ("401", "403", "jwt", "token", "unauthorized", "invalid api key"))


def cloud_load():
    """读取 Supabase 上当前用户的存档（行不存在返回 None）"""
    sb = get_sb_client()
    uid = st.session_state.get("uid")
    if sb is None or not uid:
        return None
    for attempt in range(2):
        try:
            r = sb.table(SB_TABLE).select("data").eq("id", uid).single().execute()
            d = r.data.get("data") if isinstance(r.data, dict) else None
            return d if isinstance(d, dict) else None
        except Exception as e:
            if "PGRST116" in (getattr(e, "code", "") or "") or "PGRST116" in str(e):
                return None  # 行不存在：云端还没有存档
            if attempt == 0 and _sb_is_auth_error(e) and _sb_refresh_auth():
                continue  # token 过期：刷新后重试一次
            print(f"[cloud_load] {e!r}")
            return None
    return None


def cloud_save(data):
    """把整份存档 upsert 到 Supabase 当前用户的行"""
    sb = get_sb_client()
    uid = st.session_state.get("uid")
    if sb is None or not uid:
        return False
    payload = {
        "id": uid,
        "data": data,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    for attempt in range(2):
        try:
            sb.table(SB_TABLE).upsert(payload, on_conflict="id").execute()
            return True
        except Exception as e:
            if attempt == 0 and _sb_is_auth_error(e) and _sb_refresh_auth():
                continue
            print(f"[cloud_save] {e!r}")
            return False
    return False


def jsonbin_load():
    """一次性迁移：从旧 JSONBin 存档拉取（仅 Supabase 无数据时调用）"""
    if not JSONBIN_KEY or not JSONBIN_BIN:
        return None
    try:
        r = requests.get(
            "https://api.jsonbin.io/v3/b/" + JSONBIN_BIN + "/latest",
            headers={"X-Master-Key": JSONBIN_KEY},
            timeout=10,
        )
        if r.status_code == 200:
            record = r.json().get("record")
            if isinstance(record, dict):
                return record
        else:
            print(f"[jsonbin_load] HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"[jsonbin_load] {e!r}")
    return None


def local_load():
    if os.path.exists(LOCAL_FILE):
        try:
            with open(LOCAL_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception as e:
            print(f"[local_load] {e!r}")
    return None


def local_save(data):
    try:
        tmp = LOCAL_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, LOCAL_FILE)
        return True
    except Exception as e:
        st.error(f"⚠️ 本地保存失败：{e}")
        return False


def _merge_entries_by_id(local_list, remote_list):
    """两个日志列表按 id 取并集（local 优先），按时间稳定排序"""
    merged = {}
    for e in local_list + remote_list:
        eid = e.get("id") or _stable_entry_id(e)
        if eid not in merged:
            merged[eid] = {**e, "id": eid}
    return sorted(merged.values(), key=lambda x: x.get("time", ""))


def _merge_by_name(local_list, remote_list):
    """奖励/快捷按钮按名称取并集，local 已有的保留"""
    merged = list(local_list)
    names = {r.get("name") for r in merged}
    for r in remote_list:
        if r.get("name") not in names:
            merged.append(r)
            names.add(r.get("name"))
    return merged


def _merge_reports(local_list, remote_list):
    """报告按 类型+周期 去重，保留 generated_time 较新的"""
    merged = {f"{r.get('type')}|{r.get('period_key')}": r for r in local_list}
    for r in remote_list:
        k = f"{r.get('type')}|{r.get('period_key')}"
        if k not in merged or str(r.get("generated_time", "")) > str(merged[k].get("generated_time", "")):
            merged[k] = r
    return list(merged.values())


def merge_data(local, remote):
    """云端∪本地 合并存档：日志按记录 id 去重取并集，派生值从日志重建。
    返回 (merged, cloud_new, local_new)：cloud_new=云端多出的条数，local_new=本地多出的条数。"""
    merged = dict(local)
    cloud_new = 0
    local_new = 0
    for key in ("action_log", "resistance_log", "redemption_log"):
        l_ids = {e.get("id") or _stable_entry_id(e) for e in local.get(key, [])}
        r_ids = {e.get("id") or _stable_entry_id(e) for e in remote.get(key, [])}
        cloud_new += len(r_ids - l_ids)
        local_new += len(l_ids - r_ids)
        merged[key] = _merge_entries_by_id(local.get(key, []), remote.get(key, []))
    l_ck, r_ck = set(local.get("checkin_log", [])), set(remote.get("checkin_log", []))
    cloud_new += len(r_ck - l_ck)
    local_new += len(l_ck - r_ck)
    merged["checkin_log"] = sorted(l_ck | r_ck)
    merged["rewards"] = _merge_by_name(local.get("rewards", []), remote.get("rewards", []))
    merged["quick_actions"] = _merge_by_name(local.get("quick_actions", []), remote.get("quick_actions", []))
    # 成就：unlocked 取两侧的或（bonus 积分以日志为准，迁移时会重新核对）
    r_achs = {a.get("id"): a for a in remote.get("achievements", [])}
    for a in merged.get("achievements", []):
        ra = r_achs.get(a.get("id"))
        if ra and ra.get("unlocked") and not a.get("unlocked"):
            a["unlocked"] = True
            a["unlocked_time"] = ra.get("unlocked_time")
    merged["reports"] = _merge_reports(local.get("reports", []), remote.get("reports", []))
    merged["rev"] = max(int(local.get("rev", 0) or 0), int(remote.get("rev", 0) or 0))
    if cloud_new or local_new:
        # 有分叉才重建，避免覆盖「重置属性为0」这类刻意清零的状态
        rebuild_stats_from_logs(merged)
    return merged, cloud_new, local_new


def _migrate_data(data):
    """数据迁移：补字段、兼容旧版、合并成就定义、追溯解锁。"""
    if not isinstance(data, dict):
        data = new_data()
    base = new_data()
    for k in base:
        if k not in data:
            data[k] = base[k]
    for k in base["stats"]:
        if k not in data["stats"]:
            data["stats"][k] = base["stats"][k]
    # 给旧记录补唯一 ID（云存档合并去重用）
    for key in ("action_log", "resistance_log", "redemption_log"):
        _ensure_ids(data.get(key, []))
    # 补签卡：按历史真实签到数折算赠送进度（静默，老用户登录即直接持有应得的卡）
    _cards = data.setdefault("checkin_cards", {"bought": 0, "used": 0, "earned_seen": 0})
    _derived_cards = real_checkin_count(data) // 30
    if int(_cards.get("earned_seen", 0)) < _derived_cards:
        _cards["earned_seen"] = _derived_cards
    # 兼容旧版：去掉旧的 claimed 字段
    for r in data.get("rewards", []):
        r.pop("claimed", None)
        r["cost"] = max(r.get("cost", 1), 1)
    # 合并新成就定义 + 更新已有成就的 bonus/desc（保留 unlocked 状态）
    # 先清理已移除的旧成就（不在 ACHIEVEMENT_DEFS 中的）
    valid_ids = {a["id"] for a in ACHIEVEMENT_DEFS}
    data["achievements"] = [a for a in data.get("achievements", []) if a["id"] in valid_ids]
    existing_map = {a["id"]: a for a in data.get("achievements", [])}
    for ach_def in ACHIEVEMENT_DEFS:
        if ach_def["id"] in existing_map:
            existing_map[ach_def["id"]]["bonus"] = ach_def["bonus"]
            existing_map[ach_def["id"]]["desc"] = ach_def["desc"]
            existing_map[ach_def["id"]]["name"] = ach_def["name"]
            existing_map[ach_def["id"]]["category"] = ach_def["category"]
        else:
            data.setdefault("achievements", []).append({
                **ach_def, "unlocked": False, "unlocked_time": None,
            })
    # 追溯解锁：根据历史行为点亮已有成就（发 bonus 积分）
    # 注意：这里不再自行保存，由调用方（load_data / 同步按钮）统一收口
    newly = check_achievements(data, retroactive=True)
    if newly:
        st.session_state["retroactive_achievements"] = newly
    return data


def load_data():
    cloud = cloud_load()
    sb_row_missing = cloud is None
    local = local_load()
    push_needed = False
    if cloud is None:
        # Supabase 首次使用：从旧 JSONBin 存档一次性迁移（之后不再读 JSONBin）
        jb = jsonbin_load()
        if jb:
            cloud = jb
    if cloud and local:
        # 云端、本地都存在：按记录 ID 做并集合并，谁都不丢
        data, cloud_new, local_new = merge_data(local, cloud)
        push_needed = cloud_new > 0 or local_new > 0
    else:
        data = cloud or local or new_data()
    if sb_row_missing:
        # Supabase 上还没有这一行（首次使用/迁移）：无论数据来自哪里，都推上去建行
        push_needed = True
    before = json.dumps(data, sort_keys=True, ensure_ascii=False)
    data = _migrate_data(data)
    after = json.dumps(data, sort_keys=True, ensure_ascii=False)
    if push_needed or before != after:
        # 把合并/迁移结果推回云端，两端对齐（迁移补 ID 等只发生一次）
        save_data(data)
    return data

def save_data(data):
    data["rev"] = int(data.get("rev", 0)) + 1
    data["saved_at"] = now_str()
    cloud_ok = cloud_save(data)
    local_ok = local_save(data)
    if cloud_ok:
        st.session_state["cloud_dirty"] = False
    elif get_sb_client() is not None and st.session_state.get("uid"):
        st.session_state["cloud_dirty"] = True
        st.toast("☁️ 云端保存失败，已保存到本地，下次操作会自动重试", icon="⚠️")
    if not local_ok:
        st.toast("⚠️ 本地保存也失败了，请检查磁盘空间", icon="🚨")
    return cloud_ok and local_ok

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
            "card": "#ffffff", "card_bd": "#dce3ea", "sh": "rgba(42,58,74,0.10)",
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
            "card": "#ffffff", "card_bd": "#eee0dd", "sh": "rgba(74,53,64,0.10)",
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
            "card": "#ffffff", "card_bd": "#dcede8", "sh": "rgba(58,40,40,0.10)",
            "ok_b": "#d4edda", "ok_t": "#2d5a2d", "ok_d": "#8fd49a",
            "in_b": "#d6eaf5", "in_t": "#2a5570", "in_d": "#8ac0d8",
            "wa_b": "#fef3cd", "wa_t": "#6a5200", "wa_d": "#d4be60",
            "er_b": "#f8d7da", "er_t": "#6a2530", "er_d": "#d48090",
            "ex_d": "#c0d5d0", "tb_b": "#764f51", "tb_a": "#e6f4f0",
        },
        "🌙 深空暗夜": {
            "bg1": "#0f1117", "bg2": "#131620", "bg3": "#0f1117",
            "sb1": "#1a1d27", "sb2": "#131520",
            "inp": "#1a1d27", "btn": "#2a2d3a", "btn_h": "#353846",
            "tx_h": "#e4e4e7", "tx_m": "#c4c4c7", "tx_s": "#8b8b96",
            "tx_p": "#6b6b76",
            "ac": "#818cf8", "ac_l": "#a5b4fc", "ac_d": "#6366f1",
            "bd": "#2a2d3a",
            "p1": "#6366f1", "p2": "#818cf8",
            "card": "#1e2130", "card_bd": "#2a2d3a", "sh": "rgba(0,0,0,0.35)",
            "ok_b": "rgba(34,197,94,0.15)", "ok_t": "#86efac", "ok_d": "rgba(34,197,94,0.3)",
            "in_b": "rgba(59,130,246,0.15)", "in_t": "#93c5fd", "in_d": "rgba(59,130,246,0.3)",
            "wa_b": "rgba(251,191,36,0.15)", "wa_t": "#fcd34d", "wa_d": "rgba(251,191,36,0.3)",
            "er_b": "rgba(239,68,68,0.15)", "er_t": "#fca5a5", "er_d": "rgba(239,68,68,0.3)",
            "ex_d": "#2a2d3a", "tb_b": "#818cf8", "tb_a": "#1e2130",
        },
        "🎮 热血冒险": {
            "bg1": "#fffef5", "bg2": "#fff8e7", "bg3": "#fffef0",
            "sb1": "#fff5e0", "sb2": "#ffefd0",
            "inp": "#ffffff", "btn": "#f0e6d0", "btn_h": "#e8dab8",
            "tx_h": "#1a1a2e", "tx_m": "#2d2d44", "tx_s": "#6a6a8a",
            "tx_p": "#a0a0b8",
            "ac": "#ff6b35", "ac_l": "#ff8c42", "ac_d": "#e55320",
            "bd": "#e5e0d0",
            "p1": "#ff6b35", "p2": "#ff8c42",
            "card": "#ffffff", "card_bd": "#f0e6d0", "sh": "rgba(255,107,53,0.12)",
            "ok_b": "#d4edda", "ok_t": "#2d5a2d", "ok_d": "#8fd49a",
            "in_b": "#d6eaf5", "in_t": "#2a5570", "in_d": "#8ac0d8",
            "wa_b": "#fef3cd", "wa_t": "#6a5200", "wa_d": "#d4be60",
            "er_b": "#f8d7da", "er_t": "#6a2530", "er_d": "#d48090",
            "ex_d": "#e5e0d0", "tb_b": "#ff6b35", "tb_a": "#fff0e0",
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
[data-testid="stMetric"] {
    background-color: [card];
    border: 1px solid [card_bd];
    border-radius: 10px;
    padding: 12px 16px;
    box-shadow: 0 2px 8px [sh];
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
    transition: all 0.2s ease;
}
.stButton > button:hover {
    background-color: [btn_h];
    border-color: [ac];
    transform: translateY(-1px);
    box-shadow: 0 4px 14px [sh];
}
.stButton > button:active {
    transform: translateY(0);
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, [p1], [p2]);
    border-color: [ac_d];
    color: [tx_h];
    font-weight: 600;
    box-shadow: 0 3px 0 [ac_d];
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, [p2], [ac_l]);
    box-shadow: 0 4px 0 [ac_d];
    transform: translateY(-1px);
}
.stButton > button[kind="primary"]:active {
    box-shadow: 0 1px 0 [ac_d];
    transform: translateY(2px);
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
.stAlert { border-radius: 8px; box-shadow: 0 2px 8px [sh]; }
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
    border-color: [card_bd];
    background-color: [card];
    border-radius: 10px;
    box-shadow: 0 2px 8px [sh];
}
.stDownloadButton > button {
    border-radius: 10px;
    color: [tx_m];
    background-color: [btn];
    border-color: [bd];
    transition: all 0.2s ease;
}
.stDownloadButton > button:hover {
    box-shadow: 0 4px 14px [sh];
    transform: translateY(-1px);
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
    [data-testid="stMetric"] {
        padding: 8px 10px;
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
            <div style="text-align: center; padding: 20px 0;">
                <h1 style="font-size: 3rem; margin-bottom: 4px;">🎮 Life-RPG</h1>
                <p style="font-size: 1.1rem; opacity: 0.6;">个人经验值管理系统 · Supabase 云存档</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)
        if _sb_create_client is None:
            st.error("⚠️ 未安装 supabase 库：请在运行环境执行 `pip install supabase`")
            st.stop()
        if not SB_URL or not SB_KEY:
            st.error("⚠️ 未配置 Supabase：请在文件顶部 SUPABASE_URL / SUPABASE_ANON_KEY 或 Streamlit Secrets 中填写（与清单程序相同的 URL 和可发布密钥）")
            st.stop()
        email = st.text_input("📧 邮箱", key="login_email")
        pwd = st.text_input("🔑 密码", type="password", key="login_pwd")
        if st.button("⚔️ 进入系统", use_container_width=True):
            sb = get_sb_client()
            if sb is None:
                st.error("❌ Supabase 初始化失败，请检查 URL / Key 配置")
            else:
                _login_ok = False
                try:
                    with st.spinner("登录中..."):
                        resp = sb.auth.sign_in_with_password(
                            {"email": email.strip(), "password": pwd}
                        )
                    if resp.user is not None:
                        st.session_state["uid"] = resp.user.id
                        st.session_state["user_email"] = resp.user.email or email.strip()
                        st.session_state["sb_email"] = email.strip()
                        st.session_state["sb_pwd"] = pwd
                        _login_ok = True
                except Exception as e:
                    _s = str(e).lower()
                    if "invalid api key" in _s or "invalid_api_key" in _s or "apikey" in _s:
                        st.error("❌ 配置错误：SUPABASE_URL 和 SUPABASE_ANON_KEY 不属于同一个项目（Key 必须从 URL 对应项目的 API Keys 页复制）")
                    elif "email not confirmed" in _s:
                        st.error("❌ 邮箱未验证：请在收件箱里点击 Supabase 发来的确认邮件")
                    elif "invalid login" in _s or "credentials" in _s or "password" in _s or "401" in _s:
                        st.error("❌ 邮箱或密码错误：账号必须是本项目 Authentication → Users 列表里已有的那个（Supabase 网站登录密码不算）")
                    else:
                        st.error(f"❌ 登录失败（网络/服务异常）：{e}")
                if _login_ok:
                    with st.spinner("读取存档中..."):
                        try:
                            _loaded = load_data()
                            if not isinstance(_loaded, dict):
                                _loaded = new_data()
                        except Exception as e:
                            st.error(f"⚠️ 存档读取失败，已使用新存档：{e}")
                            _loaded = new_data()
                    st.session_state.authed = True
                    st.session_state.data = _loaded
                    st.rerun()
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
# 安全兜底：如果 data 为 None 或非字典（如 load_data 曾异常），重新加载
if not isinstance(data, dict):
    try:
        data = load_data()
    except Exception:
        data = new_data()
    if not isinstance(data, dict):
        data = new_data()
    st.session_state.data = data

# 显示暂存的操作反馈消息（解决 st.success+rerun 消息丢失问题）
show_flash_message("top")

# 展示追溯解锁的成就通知（load_data 时存入 session_state）
if st.session_state.get("retroactive_achievements"):
    retro_achievements = st.session_state.pop("retroactive_achievements")
    st.balloons()
    total_bonus = sum(a["bonus"] for a in retro_achievements)
    names = "、".join(a["name"] for a in retro_achievements)
    st.success(
        f"🏅 **追溯解锁 {len(retro_achievements)} 个成就！**\n\n"
        f"{names}\n\n💰 追溯积分 +{total_bonus} pts 已到账！",
        icon="🏅"
    )

# -------- 侧边栏 --------
with st.sidebar:
    st.markdown("### 🎮 Life-RPG")

    # 侧边栏总等级简要显示
    _sb_total = data.get("total_earned", 0)
    _sb_lv = _sb_total // 100
    _sb_title, _sb_attr_title = get_titles(data)
    st.markdown(
        f'<div style="display: flex; justify-content: space-between; align-items: center; '
        f'padding: 8px 12px; border-radius: 8px; margin-bottom: 4px;'
        f'background: rgba(96,165,250,0.08); border: 1px solid rgba(96,165,250,0.2);">'
        f'<span style="font-size: 0.8rem; opacity: 0.6;">总等级</span>'
        f'<span style="font-size: 1.3rem; font-weight: 800;">Lv.{_sb_lv}</span>'
        f'</div>'
        f'<div style="text-align: center; font-size: 0.8rem; opacity: 0.8; margin-bottom: 2px;">'
        + _sb_title + (f' · {_sb_attr_title}' if _sb_attr_title else '') +
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("**存档状态**")
    if get_sb_client() is not None and st.session_state.get("uid"):
        st.success("☁️ Supabase 云存档已连接")
        _email_sb = st.session_state.get("user_email", "")
        if _email_sb:
            st.caption(f"账号：{_email_sb}")
        _saved_at = data.get("saved_at", "")
        if _saved_at:
            st.caption(f"上次保存：{_saved_at} · v{data.get('rev', 0)}")
        if st.session_state.get("cloud_dirty"):
            st.warning("⏳ 有更改尚未同步到云端，下次操作会自动重试")
        if st.button("🔄 同步云端", use_container_width=True):
            with st.spinner("同步中..."):
                cloud_data = cloud_load()
                if cloud_data:
                    # 与云端按记录 ID 合并（不再整体覆盖，谁的数据都不丢）
                    merged, cloud_new, local_new = merge_data(data, cloud_data)
                    merged = _migrate_data(merged)
                    if cloud_new or local_new:
                        save_data(merged)
                        st.session_state.data = merged
                        data = merged
                        if cloud_new and not local_new:
                            flash_success(f"✅ 已从云端合并 {cloud_new} 条新记录")
                        elif local_new and not cloud_new:
                            flash_success(f"✅ 本地 {local_new} 条新记录已推送到云端")
                        else:
                            flash_success(f"✅ 已合并云端 {cloud_new} 条、推送本地 {local_new} 条记录")
                    else:
                        flash_success("✅ 云端与本地一致，已是最新")
                    st.rerun()
                else:
                    st.error("⚠️ 同步失败，请检查网络后重试")
    else:
        st.warning("💾 仅本地存档")
        st.caption("Supabase 云端未连接（请检查配置）")

    # ---- 每日签到 ----
    st.markdown("---")
    st.markdown("**📅 每日签到**")
    show_flash_message("checkin")
    _checked_today = has_checked_in_today(data)
    _checkin_streak = get_checkin_streak(data)
    if _checked_today:
        _today_reward = get_checkin_reward(_checkin_streak)
        st.info(f"✅ 今日已签到 · 连续 **{_checkin_streak}** 天 · 今日 +{_today_reward} pts")
    else:
        _next_streak = _checkin_streak + 1
        _next_reward = get_checkin_reward(_next_streak)
        if st.button(f"📋 签到领 +{_next_reward} pts", use_container_width=True, type="primary"):
            today_ds = now_local().strftime("%Y-%m-%d")
            data.setdefault("checkin_log", []).append(today_ds)
            _new_streak = get_checkin_streak(data)
            _reward = get_checkin_reward(_new_streak)
            add_points(data, "", _reward, f"📅 每日签到（连续{_new_streak}天）", source=SOURCE_CHECKIN)
            _flash = f"✅ 签到成功！连续 {_new_streak} 天，+{_reward} pts"
            # 累计真实签到每满 30 天送一张补签卡
            _cards = data.setdefault("checkin_cards", {"bought": 0, "used": 0, "earned_seen": 0})
            _derived_cards = real_checkin_count(data) // 30
            if _derived_cards > int(_cards.get("earned_seen", 0)):
                _n_cards = _derived_cards - int(_cards.get("earned_seen", 0))
                _cards["earned_seen"] = _derived_cards
                data.setdefault("card_log", []).append(
                    {"time": now_str(), "action": "earn", "detail": f"累计签到满 {_derived_cards * 30} 天"}
                )
                _flash += f"\n\n🎁 累计签到满 {_derived_cards * 30} 天，赠送补签卡 ×{_n_cards}！"
            newly = check_achievements(data)
            save_data(data)
            st.session_state.data = data
            if newly:
                _ach_names = "、".join(a["name"] for a in newly)
                _flash += f"\n\n🏅 成就解锁：{_ach_names}"
            flash_success(_flash, icon="📋", position="checkin", balloons=bool(newly))
            st.rerun()
    if _checkin_streak > 0 and not _checked_today:
        st.caption(f"当前连续签到 {_checkin_streak} 天，别断了！")
    elif _checkin_streak >= 5:
        st.caption(f"🔥 已连续签到 {_checkin_streak} 天，每天 +5 pts！")

    # ---- 补签卡 ----
    _cards = data.get("checkin_cards", {})
    _avail_cards = available_checkin_cards(data)
    _real_checkins = real_checkin_count(data)
    _next_card_at = (_real_checkins // 30 + 1) * 30
    st.caption(
        f"🎫 补签卡 ×{_avail_cards} · 累计真实签到 {_real_checkins} 天，"
        f"满 {_next_card_at} 天再送 1 张（也可用积分购买）"
    )
    _spendable = data.get("total_earned", 0) - sum(r.get("cost", 0) for r in data.get("redemption_log", []))
    if st.button("🛒 购买补签卡（100 pts）", disabled=(_spendable < 100), use_container_width=True):
        data["redemption_log"].append({
            "id": new_entry_id(), "time": now_str(),
            "reward_name": "🎫 补签卡", "cost": 100,
        })
        data.setdefault("checkin_cards", {})["bought"] = int(_cards.get("bought", 0)) + 1
        data.setdefault("card_log", []).append({"time": now_str(), "action": "buy", "detail": "100 pts"})
        newly = check_achievements(data)
        save_data(data)
        st.session_state.data = data
        flash_success("🎫 已购买补签卡 ×1（-100 pts）", icon="🎫", position="checkin", balloons=bool(newly))
        st.rerun()

    _repair_gap = find_repairable_gap(data)
    if _repair_gap:
        if st.button(f"🎫 补签 {_repair_gap}（用 1 张卡）", disabled=(_avail_cards < 1), use_container_width=True):
            data.setdefault("checkin_log", []).append(_repair_gap)
            data.setdefault("repaired_checkins", []).append(_repair_gap)
            data.setdefault("checkin_cards", {})["used"] = int(_cards.get("used", 0)) + 1
            data.setdefault("card_log", []).append({"time": now_str(), "action": "use", "detail": _repair_gap})
            newly = check_achievements(data)
            save_data(data)
            st.session_state.data = data
            _flash = f"✅ 已补签 {_repair_gap}，连续签到恢复为 {get_checkin_streak(data)} 天"
            if newly:
                _flash += "\n\n🏅 成就解锁：" + "、".join(a["name"] for a in newly)
            flash_success(_flash, icon="🎫", position="checkin", balloons=bool(newly))
            st.rerun()
    elif _avail_cards > 0:
        st.caption("当前没有可修复的断签（只能补最近 7 天内的缺口）")

# --- 主题切换 ---
    st.markdown("---")
    st.markdown("**🎨 配色主题**")
    theme_options = ["🌌 莫兰迪蓝", "🌸 莫兰迪粉", "🍫 薄荷巧克力", "🌙 深空暗夜", "🎮 热血冒险"]
    current_theme = st.session_state.get("theme", "🌌 莫兰迪蓝")
    theme_idx = theme_options.index(current_theme) if current_theme in theme_options else 0
    st.selectbox(
        "选择配色",
        theme_options,
        index=theme_idx,
        key="theme_select",
        on_change=on_theme_change,
        label_visibility="collapsed",
    )
    
    st.markdown("---")
    _email = st.session_state.get("user_email", "")
    if _email:
        st.caption(f"👤 已登录：{_email}")
    if st.button("💾 保存并退出", use_container_width=True):
        save_data(data)
        st.session_state.authed = False
        st.session_state.data = None
        st.rerun()
    if st.button("🚪 退出账号", use_container_width=True):
        save_data(data)
        sb = get_sb_client()
        if sb is not None:
            try:
                sb.auth.sign_out()
            except Exception as e:
                print(f"[sign_out] {e!r}")
        st.session_state.authed = False
        st.session_state.data = None
        st.session_state["uid"] = None
        st.session_state.pop("sb_email", None)
        st.session_state.pop("sb_pwd", None)
        st.session_state.pop("login_email", None)
        st.session_state.pop("login_pwd", None)
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
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
    ["📝 记录任务", "🚧 阻力复盘", "🏆 奖励商店", "📋 历史日志", "📊 统计", "🏅 成就", "⚙️ 设置"]
)


# ════════ Tab 1：记录任务 ════════
with tab1:
    show_flash_message("record")
    st.markdown("### 📝 记录完成的任务")
    st.caption("每完成一件事，就赚一点经验值。积少成多。")

    # ---------- 快捷记录 ----------
    st.markdown("#### 🐾 我动了一下")
    st.caption("低能量时，点一下也算数。不想写也可以，这就是一次微小启动。")

    quick_actions = data.get("quick_actions", [])

    # 心情选择器（全局，适用于下方所有快捷按钮）
    quick_mood = st.selectbox("当前心情", MOOD_OPTIONS, index=0, key="quick_mood", label_visibility="collapsed")

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
                if attr_key not in VALID_ATTRS:
                    attr_key = "Productivity"
                try:
                    points = max(int(action.get("points", 1)), 1)
                except (ValueError, TypeError):
                    points = 1
                icon = attr_icon_map.get(attr_key, "✨")

                with cols[j]:
                    btn_label = f"{name}\n{icon}+{points}"
                    if st.button(btn_label, key="quick_action_" + str(idx), use_container_width=True):
                        add_points(data, attr_key, points, "快捷记录：" + name, mood=quick_mood)

                        newly = check_achievements(data)
                        save_data(data)
                        st.session_state.data = data

                        new_val = data["stats"][attr_key]
                        msg = encouragement_for(attr_key)
                        _flash = f"✅ {name} | +{points} {attr_key}，当前 {new_val}\n\n{msg}"
                        if newly:
                            _ach_names = "、".join(a["name"] for a in newly)
                            _flash += f"\n\n🏅 成就解锁：{_ach_names}"
                        flash_success(_flash, icon="🐾", position="record", balloons=(points >= 10 or bool(newly)))
                        st.rerun()

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

        c3a, c3b = st.columns(2)
        with c3a:
            task_mood = st.selectbox(
                "当时心情",
                MOOD_OPTIONS,
                index=0,
                key="task_mood",
            )
        with c3b:
            task_date = st.date_input(
                "📅 这是哪天做的？",
                value=now_local().date(),
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
            today_local = now_local().date()
            is_backdated = task_date != today_local
            if not is_backdated:
                task_time = now_str()
            else:
                task_time = task_date.strftime("%Y-%m-%d") + " 12:00"

            add_points(
                data, attr_key, points, task_desc or "(未填写)",
                mood=task_mood, backdated=is_backdated, time_str=task_time,
            )

            newly = check_achievements(data)
            save_data(data)
            st.session_state.data = data

            new_val = data["stats"][attr_key]
            msg = encouragement_for(attr_key)
            _flash = f"🎉 +{points} {attr_key}！当前 {new_val}\n\n{msg}"
            if newly:
                _ach_names = "、".join(a["name"] for a in newly)
                _flash += f"\n\n🏅 成就解锁：{_ach_names}"
            flash_success(_flash, icon="✅", position="record", balloons=(points >= 20 or bool(newly)))
            if "task_date" in st.session_state:
                del st.session_state["task_date"]
            st.rerun()


# ════════ Tab 2：阻力复盘 ════════
with tab2:
    show_flash_message("resistance")
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
                "id": new_entry_id(),
                "time": now_str(),
                "reason": reason,
                "detail": detail or "(未填写)",
                "strategy": strategy or "(未填写)",
            }
        )
        newly = check_achievements(data)
        save_data(data)
        st.session_state.data = data

        count = len(data["resistance_log"])
        _flash = f"🔥 +1 Willpower | 直面阻力 {count} 次\n\n💪 记录阻力本身就是勇气，你做到了。"
        if newly:
            _ach_names = "、".join(a["name"] for a in newly)
            _flash += f"\n\n🏅 成就解锁：{_ach_names}"
        flash_success(_flash, icon="💪", position="resistance", balloons=bool(newly))
        st.rerun()
        
# ════════ Tab 3：奖励商店 ════════
with tab3:
    show_flash_message("redeem")
    _total_spent = sum(r.get("cost", 0) for r in data.get("redemption_log", []))
    _total = data.get("total_earned", 0) - _total_spent

    st.markdown("### 🏆 奖励商店")
    st.markdown(
        "💰 **当前积分: "
        + str(_total)
        + "** — 同一个奖励可以反复兑换，每次都会扣积分"
    )
    st.markdown("---")

    rewards = data.get("rewards", [])
    redemption_log = data.get("redemption_log", [])

    redeem_counts = {}
    for r in redemption_log:
        name = r.get("reward_name", "")
        redeem_counts[name] = redeem_counts.get(name, 0) + 1

    if not rewards:
        st.warning("商店空空如也 → 去「设置」添加奖励")
    else:
        for i, reward in enumerate(rewards):
            cost = max(reward.get("cost", 1), 1)
            can_buy = _total >= cost
            times = redeem_counts.get(reward.get("name", ""), 0)

            col_info, col_btn = st.columns([3, 1])

            with col_info:
                st.markdown("🎁 **" + reward.get("name", "未命名") + "**")

                if can_buy:
                    cost_text = "✅ " + str(cost) + " pts"
                else:
                    cost_text = "❌ " + str(cost) + " pts（差 " + str(cost - _total) + "）"

                if times > 0:
                    times_text = "已兑 " + str(times) + " 次"
                else:
                    times_text = "尚未兑换"

                st.caption(cost_text + " ｜ " + times_text)

            with col_btn:
                if can_buy:
                    if st.button("兑换", key="r_" + str(i), type="primary", use_container_width=True):
                        data["redemption_log"].append(
                            {
                                "id": new_entry_id(),
                                "time": now_str(),
                                "reward_name": reward.get("name", "未命名"),
                                "cost": cost,
                            }
                        )
                        newly = check_achievements(data)
                        save_data(data)
                        st.session_state.data = data
                        _flash = f"🎉🎉🎉 **兑换成功！** {reward.get('name', '未命名')} — 好好享受！"
                        if newly:
                            _ach_names = "、".join(a["name"] for a in newly)
                            _flash += f"\n\n🏅 成就解锁：{_ach_names}"
                        flash_success(_flash, icon="🎁", position="redeem", balloons=bool(newly))
                        st.rerun()
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
    show_flash_message("history")
    st.markdown("### 📋 历史日志")

    # ---- 撤销最近一条（跨行为/阻力，取时间最新的一条非成就记录） ----
    _al = data.get("action_log", [])
    _rl = data.get("resistance_log", [])
    _last_act_idx = next((i for i in range(len(_al) - 1, -1, -1)
                          if _al[i].get("source", SOURCE_TASK) != SOURCE_ACH), None)
    _last_res_idx = len(_rl) - 1 if _rl else None

    if _last_act_idx is not None or _last_res_idx is not None:
        _ta = _al[_last_act_idx].get("time", "") if _last_act_idx is not None else ""
        _tr = _rl[_last_res_idx].get("time", "") if _last_res_idx is not None else ""
        _undo_from_action = _last_act_idx is not None and (not _tr or _ta >= _tr)
        _undo_label = (_al[_last_act_idx].get("task", "未命名记录") if _undo_from_action
                       else _rl[_last_res_idx].get("reason", "阻力复盘"))

        if not st.session_state.get("confirm_undo_latest"):
            if st.button("↩️ 撤销最近一条记录"):
                st.session_state["confirm_undo_latest"] = True
                st.rerun()
        else:
            st.warning(f"将撤销：{_undo_label}（属性与积分一并回收）")
            _uc1, _uc2 = st.columns(2)
            with _uc1:
                if st.button("⚠️ 确认撤销", key="confirm_undo_yes", type="primary"):
                    if _undo_from_action:
                        remove_action_entry(data, _last_act_idx)
                    else:
                        remove_resistance_entry(data, _last_res_idx)
                    save_data(data)
                    st.session_state.data = data
                    st.session_state.pop("confirm_undo_latest", None)
                    flash_success(f"↩️ 已撤销：{_undo_label}", position="history")
                    st.rerun()
            with _uc2:
                if st.button("取消", key="confirm_undo_no"):
                    st.session_state.pop("confirm_undo_latest", None)
                    st.rerun()
        st.markdown("---")

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
            # 用索引遍历，方便修改日期时定位
            _start = max(0, len(action_logs) - show_count_action)
            for _idx in range(len(action_logs) - 1, _start - 1, -1):
                entry = action_logs[_idx]
                source = entry.get("source", SOURCE_TASK)
                if source == SOURCE_ACH:
                    attr_emoji = "🏅"
                else:
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
                    st.markdown("**来源**: " + source)
                    if entry.get("attribute"):
                        st.markdown("**属性**: " + str(entry.get("attribute")))
                    st.markdown("**得分**: +" + str(entry.get("points", "?")))

                    # 修改日期（成就类不允许改）
                    if source != SOURCE_ACH:
                        _edit_key = f"edit_action_{_idx}"
                        if st.button("✏️ 修改日期", key=f"btn_{_edit_key}"):
                            st.session_state[_edit_key] = not st.session_state.get(_edit_key, False)

                        if st.session_state.get(_edit_key):
                            _time_str = entry.get("time", "")
                            try:
                                _cur_date = datetime.strptime(_time_str[:10], "%Y-%m-%d").date()
                            except (ValueError, TypeError):
                                _cur_date = now_local().date()
                            _new_date = st.date_input("新日期", value=_cur_date, key=f"input_{_edit_key}")
                            _ec1, _ec2 = st.columns(2)
                            with _ec1:
                                if st.button("💾 保存", key=f"save_{_edit_key}", type="primary"):
                                    _old_time = _time_str[11:] if len(_time_str) > 11 else "12:00"
                                    entry["time"] = _new_date.strftime("%Y-%m-%d") + " " + _old_time
                                    entry["backdated"] = (_new_date != now_local().date())
                                    save_data(data)
                                    st.session_state.data = data
                                    st.session_state.pop(_edit_key, None)
                                    flash_success("✅ 日期已修改！", position="history")
                                    st.rerun()
                            with _ec2:
                                if st.button("取消", key=f"cancel_{_edit_key}"):
                                    st.session_state.pop(_edit_key, None)
                                    st.rerun()

                    # 删除记录（成就来源不可删，会破坏成就积分一致性）
                    if source != SOURCE_ACH:
                        _del_key = f"del_action_{_idx}"
                        if st.button("🗑️ 删除此条", key=f"btn_{_del_key}"):
                            st.session_state[_del_key] = not st.session_state.get(_del_key, False)
                        if st.session_state.get(_del_key):
                            st.warning("删除后该条属性与积分会一并回收，确定吗？")
                            _dc1, _dc2 = st.columns(2)
                            with _dc1:
                                if st.button("⚠️ 确认删除", key=f"yes_{_del_key}", type="primary"):
                                    remove_action_entry(data, _idx)
                                    save_data(data)
                                    st.session_state.data = data
                                    st.session_state.pop(_del_key, None)
                                    flash_success("🗑️ 已删除该记录并回收积分", position="history")
                                    st.rerun()
                            with _dc2:
                                if st.button("取消", key=f"no_{_del_key}"):
                                    st.session_state.pop(_del_key, None)
                                    st.rerun()
                    else:
                        st.caption("🏅 成就记录不可删除（会破坏成就积分一致性）")

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
            _r_start = max(0, len(resist_logs) - show_count_resist)
            for _ridx in range(len(resist_logs) - 1, _r_start - 1, -1):
                entry = resist_logs[_ridx]
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

                    # 修改日期
                    _edit_key = f"edit_resist_{_ridx}"
                    if st.button("✏️ 修改日期", key=f"btn_{_edit_key}"):
                        st.session_state[_edit_key] = not st.session_state.get(_edit_key, False)

                    if st.session_state.get(_edit_key):
                        _time_str = entry.get("time", "")
                        try:
                            _cur_date = datetime.strptime(_time_str[:10], "%Y-%m-%d").date()
                        except (ValueError, TypeError):
                            _cur_date = now_local().date()
                        _new_date = st.date_input("新日期", value=_cur_date, key=f"input_{_edit_key}")
                        _ec1, _ec2 = st.columns(2)
                        with _ec1:
                            if st.button("💾 保存", key=f"save_{_edit_key}", type="primary"):
                                _old_time = _time_str[11:] if len(_time_str) > 11 else "12:00"
                                entry["time"] = _new_date.strftime("%Y-%m-%d") + " " + _old_time
                                save_data(data)
                                st.session_state.data = data
                                st.session_state.pop(_edit_key, None)
                                flash_success("✅ 日期已修改！", position="history")
                                st.rerun()
                        with _ec2:
                            if st.button("取消", key=f"cancel_{_edit_key}"):
                                st.session_state.pop(_edit_key, None)
                                st.rerun()

                    # 删除记录
                    _del_key = f"del_resist_{_ridx}"
                    if st.button("🗑️ 删除此条", key=f"btn_{_del_key}"):
                        st.session_state[_del_key] = not st.session_state.get(_del_key, False)
                    if st.session_state.get(_del_key):
                        st.warning("删除后会回收 1 点意志力与积分，确定吗？")
                        _dc1, _dc2 = st.columns(2)
                        with _dc1:
                            if st.button("⚠️ 确认删除", key=f"yes_{_del_key}", type="primary"):
                                remove_resistance_entry(data, _ridx)
                                save_data(data)
                                st.session_state.data = data
                                st.session_state.pop(_del_key, None)
                                flash_success("🗑️ 已删除该阻力记录", position="history")
                                st.rerun()
                        with _dc2:
                            if st.button("取消", key=f"no_{_del_key}"):
                                st.session_state.pop(_del_key, None)
                                st.rerun()

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

            # 删除兑换记录（可用积分 = 累计 - 已花费，删除后自动退回）
            del_rd_idx = st.selectbox(
                "选择要删除的兑换记录",
                range(len(redemption_logs)),
                format_func=lambda i: f"{redemption_logs[i].get('time', '')} | {redemption_logs[i].get('reward_name', '')} | -{redemption_logs[i].get('cost', 0)} pts",
                key="del_redemption",
            )
            if st.button("🗑️ 删除选中的兑换记录（积分退回）"):
                _removed = data["redemption_log"].pop(del_rd_idx)
                save_data(data)
                st.session_state.data = data
                flash_success(f"✅ 已删除兑换记录：{_removed.get('reward_name', '')}（积分已退回）", position="history")
                st.rerun()
                
                
# ════════ Tab 5：统计 ════════
with tab5:
    show_flash_message("stats")
    st.markdown("### 📊 统计")

    # ---- 周报 / 月报 ----
    with st.expander("📋 周报 / 月报", expanded=False):
        today_for_report = now_local().date()
        monday = today_for_report - timedelta(days=today_for_report.weekday())
        week_key = f"{monday.year}-W{monday.strftime('%W')}"

        reports = data.get("reports", [])

        # session_state 幂等标记：防止同一次 rerun 中重复触发自动生成
        auto_gen_key = f"report_auto_gen_{week_key}"
        if auto_gen_key not in st.session_state:
            st.session_state[auto_gen_key] = False

        # 自动补生成：上周周报还没生成 + 上周有数据 → 补一份
        last_week_monday = monday - timedelta(days=7)
        last_week_key = f"{last_week_monday.year}-W{last_week_monday.strftime('%W')}"
        has_last_weekly = any(r.get("type") == "weekly" and r.get("period_key") == last_week_key for r in reports)
        if not has_last_weekly:
            try:
                last_week_data = _get_daily_map(data)
                last_week_strs = [(last_week_monday + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
                has_last_week_data = any(ds in last_week_data for ds in last_week_strs)
                if has_last_week_data:
                    last_week_sunday = monday - timedelta(days=1)
                    report_text = generate_weekly_report(data, as_of_date=last_week_sunday)
                    reports.append({
                        "type": "weekly",
                        "period_key": last_week_key,
                        "generated_time": now_str(),
                        "content": report_text,
                        "auto": True,
                    })
                    data["reports"] = reports
                    save_data(data)
                    st.session_state.data = data
            except Exception as e:
                st.warning(f"上周周报自动补生成失败：{e}", icon="⚠️")

        # 本周周报自动生成（周日当天）
        is_sunday = today_for_report.weekday() == 6
        existing_weekly = [r for r in reports if r.get("type") == "weekly" and r.get("period_key") == week_key]
        if is_sunday and not existing_weekly and not st.session_state[auto_gen_key]:
            try:
                report_text = generate_weekly_report(data)
                reports.append({
                    "type": "weekly",
                    "period_key": week_key,
                    "generated_time": now_str(),
                    "content": report_text,
                    "auto": True,
                })
                data["reports"] = reports
                save_data(data)
                st.session_state.data = data
                st.session_state[auto_gen_key] = True
                existing_weekly = [reports[-1]]
            except Exception as e:
                st.warning(f"本周周报自动生成失败：{e}", icon="⚠️")

        # 清理：reports 最多保留 30 份（控制存档体积，JSONBin 免费版上限 100KB）
        if len(reports) > 30:
            reports = sorted(reports, key=lambda r: r.get("generated_time", ""), reverse=True)[:30]
            data["reports"] = reports
            save_data(data)
            st.session_state.data = data

        rc1, rc2 = st.columns(2)
        with rc1:
            if st.button("📋 生成本周周报", use_container_width=True):
                existing = [r for r in reports if r.get("type") == "weekly" and r.get("period_key") == week_key]
                if existing:
                    old = existing[0]
                    old["content"] = generate_weekly_report(data)
                    old["generated_time"] = now_str()
                    old["auto"] = False
                    data["reports"] = reports
                    save_data(data)
                    st.session_state.data = data
                    flash_success("✅ 本周周报已更新", position="stats")
                    st.rerun()
                else:
                    report_text = generate_weekly_report(data)
                    reports.append({
                        "type": "weekly",
                        "period_key": week_key,
                        "generated_time": now_str(),
                        "content": report_text,
                        "auto": False,
                    })
                    data["reports"] = reports
                    save_data(data)
                    st.session_state.data = data
                    flash_success("✅ 周报已生成", position="stats")
                    st.rerun()
        with rc2:
            if st.button("📅 生成本月月报", use_container_width=True):
                month_key = today_for_report.strftime("%Y-%m")
                existing_monthly = [r for r in reports if r.get("type") == "monthly" and r.get("period_key") == month_key]
                if existing_monthly:
                    old = existing_monthly[0]
                    old["content"] = generate_monthly_report(data)
                    old["generated_time"] = now_str()
                    old["auto"] = False
                    data["reports"] = reports
                    save_data(data)
                    st.session_state.data = data
                    flash_success("✅ 本月月报已更新", position="stats")
                    st.rerun()
                else:
                    report_text = generate_monthly_report(data)
                    reports.append({
                        "type": "monthly",
                        "period_key": month_key,
                        "generated_time": now_str(),
                        "content": report_text,
                        "auto": False,
                    })
                    data["reports"] = reports
                    save_data(data)
                    st.session_state.data = data
                    flash_success("✅ 月报已生成", position="stats")
                    st.rerun()

        # 显示最近报告
        recent_reports = sorted(reports, key=lambda r: r.get("generated_time", ""), reverse=True)
        if recent_reports:
            latest = recent_reports[0]
            st.markdown("---")
            auto_tag = " 🤖自动生成" if latest.get("auto") else ""
            st.caption(f"最近报告 · 生成于 {latest.get('generated_time', '')}{auto_tag}")
            st.code(latest.get("content", ""), language=None)

            if len(recent_reports) > 1:
                with st.expander(f"查看全部历史报告（共 {len(recent_reports)} 份）"):
                    for r in recent_reports[1:]:
                        tag = " 🤖" if r.get("auto") else ""
                        st.caption(f"{r.get('type', '')} · {r.get('generated_time', '')}{tag}")
                        st.code(r.get("content", ""), language=None)
                        st.markdown("")
        else:
            st.info("还没有报告。点击上方按钮生成一份。")
    st.markdown("---")

    # ---------- 汇总每日数据 ----------
    daily = _get_daily_map(data)

    today_date = now_local().date()

    # ---- 数据摘要 ----
    st.markdown("#### 📈 总览")

    total_days = len(daily)
    total_points = data.get("total_earned", 0)
    avg_daily = round(total_points / max(total_days, 1), 1)

    # 连续记录天数（今天没记录则从昨天开始算，不直接归零）
    streak = calc_streak(set(daily.keys()), today_date)

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

    # ---- 属性雷达图（本月 vs 上月） ----
    st.markdown("#### 🕸️ 属性雷达（本月 vs 上月）")
    st.caption("形状越饱满说明四维越均衡。虚线是上月的形状，对比可见变化。")

    def _month_attr_sum(prefix):
        vals = {"Productivity": 0, "Creativity": 0, "Willpower": 0, "Vitality": 0}
        for ds, dd in daily.items():
            if ds[:7] == prefix:
                for k in vals:
                    vals[k] += dd.get(k, 0)
        return vals

    _this_m = today_date.strftime("%Y-%m")
    _last_m = (today_date.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
    _mv_this = _month_attr_sum(_this_m)
    _mv_last = _month_attr_sum(_last_m)

    if sum(_mv_this.values()) > 0 or sum(_mv_last.values()) > 0:
        _attr_keys = ["Productivity", "Creativity", "Willpower", "Vitality"]
        _radar_labels = ["⚡ 生产力", "💡 创造力", "🔥 意志力", "💚 精力"]
        fig_radar = go.Figure()
        if sum(_mv_last.values()) > 0:
            fig_radar.add_trace(go.Scatterpolar(
                r=[_mv_last[k] for k in _attr_keys],
                theta=_radar_labels,
                fill="toself",
                name=f"上月（{_last_m}）",
                line=dict(dash="dash"),
                opacity=0.45,
            ))
        fig_radar.add_trace(go.Scatterpolar(
            r=[_mv_this[k] for k in _attr_keys],
            theta=_radar_labels,
            fill="toself",
            name=f"本月（{_this_m}）",
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(showticklabels=False)),
            height=360,
            margin=dict(t=50, b=20, l=50, r=50),
            legend=dict(orientation="h", yanchor="bottom", y=1.05),
        )
        st.plotly_chart(fig_radar, use_container_width=True)
    else:
        st.info("本月和上月还没有属性数据。")

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

    st.markdown("---")

    # ---- 心情 vs 积分 ----
    st.markdown("#### 😊 心情与产出")

    mood_data = {}
    for entry in data.get("action_log", []):
        source = entry.get("source", SOURCE_TASK)
        if source in (SOURCE_ACH, SOURCE_CHECKIN):
            continue
        mood = entry.get("mood", "🙂")
        if mood not in VALID_MOODS:
            mood = "🙂"
        pts = entry.get("points", 0)
        if mood not in mood_data:
            mood_data[mood] = {"total_pts": 0, "count": 0}
        mood_data[mood]["total_pts"] += pts
        mood_data[mood]["count"] += 1

    if mood_data and sum(v["count"] for v in mood_data.values()) > 0:
        mood_display_order = list(reversed(MOOD_OPTIONS))
        mood_labels = [m for m in mood_display_order if m in mood_data]
        mood_labels += [m for m in mood_data if m not in mood_display_order]

        avg_pts = [round(mood_data[m]["total_pts"] / max(mood_data[m]["count"], 1), 1) for m in mood_labels]
        counts = [mood_data[m]["count"] for m in mood_labels]

        mc1, mc2 = st.columns(2)
        with mc1:
            st.caption("各心情平均得分")
            fig_mood_bar = go.Figure(data=[go.Bar(
                x=mood_labels,
                y=avg_pts,
                marker_color=["#7fc5ca", "#51cf66", "#ffe066", "#ffa94d", "#ff5c5c"][:len(mood_labels)],
                text=[f"{v} pts" for v in avg_pts],
                textposition="outside",
            )])
            fig_mood_bar.update_layout(
                height=250,
                margin=dict(t=10, b=30, l=30, r=10),
                xaxis_title=None,
                yaxis_title="平均得分",
                showlegend=False,
            )
            st.plotly_chart(fig_mood_bar, use_container_width=True)

        with mc2:
            st.caption("各心情记录次数")
            fig_mood_pie = go.Figure(data=[go.Pie(
                labels=mood_labels,
                values=counts,
                hole=0.5,
                textinfo="label+percent",
                textposition="outside",
            )])
            fig_mood_pie.update_layout(
                height=250,
                margin=dict(t=10, b=10, l=10, r=10),
                showlegend=False,
            )
            st.plotly_chart(fig_mood_pie, use_container_width=True)

        # 文字洞察
        best_mood = max(mood_labels, key=lambda m: mood_data[m]["total_pts"] / max(mood_data[m]["count"], 1))
        best_avg = round(mood_data[best_mood]["total_pts"] / max(mood_data[best_mood]["count"], 1), 1)
        worst_mood = min(mood_labels, key=lambda m: mood_data[m]["total_pts"] / max(mood_data[m]["count"], 1))
        worst_avg = round(mood_data[worst_mood]["total_pts"] / max(mood_data[worst_mood]["count"], 1), 1)

        if len(mood_labels) == 1:
            st.info(
                f"💡 目前只有 {best_mood} 一种心情的记录（平均 {best_avg} pts/次）。"
                f"多记录几种心情后，这里会显示不同状态下的产出对比。"
            )
        elif best_mood == worst_mood:
            st.info(
                f"💡 各心情下的平均产出相同（{best_avg} pts/次），"
                f"说明心情对产出暂无显著影响。继续记录更多数据后再看趋势。"
            )
        else:
            st.info(
                f"💡 你在 {best_mood} 状态下产出最高（平均 {best_avg} pts/次），"
                f"在 {worst_mood} 状态下产出最低（平均 {worst_avg} pts/次）。"
            )
    else:
        st.info("还没有心情数据。记录任务时选择心情后，这里会显示分析。")

    # ---- 心情趋势线 ----
    st.markdown("---")
    st.markdown("#### 💗 心情趋势（近 30 天）")
    st.caption("每天心情的平均值（😴1 → 🚀5），橙线是最近 7 个有记录日子的滑动平均。")

    _mood_score = {"😴": 1, "😐": 2, "🙂": 3, "😄": 4, "🚀": 5}
    _day_mood = {}
    for entry in data.get("action_log", []):
        if entry.get("source", SOURCE_TASK) in (SOURCE_ACH, SOURCE_CHECKIN):
            continue
        m = entry.get("mood")
        if m not in _mood_score:
            continue
        ds = entry.get("time", "")[:10]
        _day_mood.setdefault(ds, []).append(_mood_score[m])

    _t_dates = [(today_date - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(29, -1, -1)]
    _t_vals = [round(sum(_day_mood[d]) / len(_day_mood[d]), 2) if _day_mood.get(d) else None for d in _t_dates]
    _have_days = sum(1 for v in _t_vals if v is not None)

    if _have_days >= 3:
        # 滑动平均基于有记录的日子（不是日历日），贴回对应日期
        _window = [v for v in _t_vals if v is not None]
        _roll_vals = [
            round(sum(_window[max(0, i - 6):i + 1]) / len(_window[max(0, i - 6):i + 1]), 2)
            for i in range(len(_window))
        ]
        _roll_iter = iter(_roll_vals)
        _t_roll = [next(_roll_iter) if v is not None else None for v in _t_vals]

        fig_mood_trend = go.Figure()
        fig_mood_trend.add_trace(go.Scatter(
            x=[d[5:] for d in _t_dates], y=_t_vals, name="当日心情均值",
            mode="lines+markers",
            line=dict(color="#7fc5ca", width=1.5),
            marker=dict(size=5),
            connectgaps=False,
        ))
        fig_mood_trend.add_trace(go.Scatter(
            x=[d[5:] for d in _t_dates], y=_t_roll, name="滑动平均",
            mode="lines",
            line=dict(color="#ffa94d", width=3),
            connectgaps=False,
        ))
        fig_mood_trend.update_layout(
            height=280,
            margin=dict(t=10, b=30, l=40, r=10),
            yaxis=dict(
                range=[0.5, 5.5],
                tickvals=[1, 2, 3, 4, 5],
                ticktext=["😴", "😐", "🙂", "😄", "🚀"],
            ),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            xaxis=dict(type="category"),
        )
        st.plotly_chart(fig_mood_trend, use_container_width=True)
    else:
        st.info(f"近 30 天只有 {_have_days} 天有心情记录，多记几天后就能看到趋势线。")


# ════════ Tab 7：设置 ════════
with tab7:
    show_flash_message("settings")
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
            flash_success("✅ 已添加快捷按钮: " + new_q_name.strip() + " (+" + str(new_q_points) + ")", position="settings")
            st.rerun()
        else:
            st.error("请输入按钮名称")

    st.markdown("##### 当前快捷按钮")

    quick_actions = data.get("quick_actions", [])

    if quick_actions:
        del_q_idx = st.selectbox(
            "选择要删除的快捷按钮",
            range(len(quick_actions)),
            format_func=lambda i: f"{quick_actions[i].get('name', '未命名')} | {quick_actions[i].get('attribute', 'Productivity')} +{quick_actions[i].get('points', 1)}",
            key="del_quick_action",
        )

        if st.button("🗑️ 删除选中快捷按钮"):
            removed = data["quick_actions"].pop(del_q_idx)
            save_data(data)
            st.session_state.data = data
            flash_success("✅ 已删除快捷按钮: " + removed.get("name", "未命名动作"), position="settings")
            st.rerun()
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
            flash_success("✅ 已添加: " + new_name + " (" + str(new_cost) + " pts)", position="settings")
            st.rerun()
        else:
            st.error("请输入奖励名称")

    # -- 删除奖励 --
    st.markdown("---")
    st.markdown("#### 🗑️ 删除奖励")
    if data["rewards"]:
        del_r_idx = st.selectbox(
            "选择要删除的奖励",
            range(len(data["rewards"])),
            format_func=lambda i: f"{data['rewards'][i]['name']} ({data['rewards'][i]['cost']} pts)",
            key="del_reward",
        )
        if st.button("🗑️ 删除选中奖励"):
            data["rewards"].pop(del_r_idx)
            save_data(data)
            st.session_state.data = data
            flash_success("✅ 已删除", position="settings")
            st.rerun()
    else:
        st.caption("暂无奖励可删除")

    # -- 危险区域 --
    st.markdown("---")
    st.markdown("#### ⚠️ 危险区域")
    col_r1, col_r2, col_r3 = st.columns(3)

    with col_r1:
        confirm_reset = st.checkbox("确认重置", key="confirm_reset_stats")
        if st.button("🔄 重置属性为0", type="secondary", disabled=not confirm_reset):
            for key in data["stats"]:
                data["stats"][key] = 0
            data["total_earned"] = 0
            save_data(data)
            st.session_state.data = data
            st.session_state["confirm_reset_stats"] = False
            flash_success("✅ 属性已清零", position="settings")
            st.rerun()

    with col_r2:
        confirm_clear = st.checkbox("确认清除", key="confirm_clear_data")
        if st.button("💣 清除所有数据", type="secondary", disabled=not confirm_clear):
            data = new_data()
            save_data(data)
            st.session_state.data = data
            st.session_state["confirm_clear_data"] = False
            flash_success("✅ 已恢复初始状态", position="settings")
            st.rerun()

    with col_r3:
        if st.button("🩹 修复属性(找回错扣分)", type="primary"):
            data = rebuild_stats_from_logs(data)
            newly = check_achievements(data)
            save_data(data)
            st.session_state.data = data
            s = data["stats"]
            _flash = f"✅ 已从历史重建属性！\n\n⚡{s['Productivity']} 💡{s['Creativity']} 🔥{s['Willpower']} 💚{s['Vitality']}"
            if newly:
                _ach_names = "、".join(a["name"] for a in newly)
                _flash += f"\n\n🏅 成就解锁：{_ach_names}"
            flash_success(_flash, icon="🩹", position="settings", balloons=bool(newly))
            st.rerun()


    # -- 备份 --
    st.markdown("---")
    st.markdown("#### 📤 备份数据")
    try:
        _size_kb = len(json.dumps(data, ensure_ascii=False).encode("utf-8")) / 1024
    except Exception:
        _size_kb = 0
    st.caption(f"当前存档体积：{_size_kb:.1f} KB（JSONBin 免费版单 bin 上限 100 KB，建议定期导出备份）")
    st.download_button(
        label="下载 JSON 备份",
        data=json.dumps(data, ensure_ascii=False, indent=2),
        file_name="life_rpg_backup_" + now_str().split(" ")[0].replace("-", "") + ".json",
        mime="application/json",
        use_container_width=True,
    )


# ════════ Tab 6：成就 ════════
with tab6:
    st.markdown("### 🏅 成就")

    achievements = data.get("achievements", [])
    unlocked = [a for a in achievements if a.get("unlocked")]
    total_bonus = sum(a.get("bonus", 0) for a in unlocked)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("🏅 已解锁", f"{len(unlocked)} / {len(achievements)}")
    with c2:
        st.metric("💰 成就积分", str(total_bonus))
    with c3:
        st.metric("📊 完成度", f"{int(len(unlocked) / max(len(achievements), 1) * 100)}%")

    st.progress(len(unlocked) / max(len(achievements), 1))
    st.markdown("---")

    cat_labels = {
        "cumulative": "📈 累积型成就",
        "daily": "📅 单日型成就",
        "special": "🎯 特殊行为型成就",
        "mood": "🎭 心情系列成就",
        "milestone": "🎯 里程碑成就",
        "checkin": "📋 签到系列成就",
    }
    cat_colors = {
        "cumulative": "#58CC02",
        "daily": "#1CB0F6",
        "special": "#CE82FF",
        "mood": "#FF6B9D",
        "milestone": "#FFA500",
        "checkin": "#20B2AA",
    }

    for cat in ["cumulative", "daily", "special", "mood", "milestone", "checkin"]:
        cat_achs = [a for a in achievements if a.get("category") == cat]
        if not cat_achs:
            continue
        # 同类成就按 bonus 升序排列（简单的在前）
        cat_achs = sorted(cat_achs, key=lambda a: a.get("bonus", 0))
        st.markdown(f"#### {cat_labels.get(cat, cat)}")

        badges_html = '<div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px;">'
        for ach in cat_achs:
            parts = ach["name"].split(" ", 1)
            emoji = parts[0] if len(parts) > 1 else "🏅"
            name = parts[1] if len(parts) > 1 else ach["name"]
            color = cat_colors.get(cat, "#888")

            if ach.get("unlocked"):
                badges_html += (
                    f'<div title="{ach["desc"]}" '
                    f'style="flex: 1 1 120px; min-width: 110px; '
                    f'background: linear-gradient(135deg, {color}22, {color}08); '
                    f'border: 1.5px solid {color}55; border-radius: 10px; '
                    f'padding: 10px 6px; text-align: center; transition: transform 0.15s;">'
                    f'<div style="font-size: 1.8rem; margin-bottom: 2px;">{emoji}</div>'
                    f'<div style="font-weight: 700; font-size: 0.82rem; line-height: 1.3;">{name}</div>'
                    f'<div style="font-size: 0.72rem; color: {color}; font-weight: 600;">+{ach["bonus"]} pts</div>'
                    f'</div>'
                )
            else:
                badges_html += (
                    f'<div title="{ach["desc"]}" '
                    f'style="flex: 1 1 120px; min-width: 110px; '
                    f'background: rgba(128,128,128,0.06); '
                    f'border: 1.5px solid rgba(128,128,128,0.15); border-radius: 10px; '
                    f'padding: 10px 6px; text-align: center; opacity: 0.45; filter: grayscale(0.7);">'
                    f'<div style="font-size: 1.8rem; margin-bottom: 2px;">🔒</div>'
                    f'<div style="font-weight: 700; font-size: 0.82rem; line-height: 1.3; color: #888;">{name}</div>'
                    f'<div style="font-size: 0.72rem; color: #aaa;">+{ach["bonus"]} pts</div>'
                    f'</div>'
                )
        badges_html += '</div>'
        st.markdown(badges_html, unsafe_allow_html=True)

        st.markdown("")


# ════════════════════════════════════════════════════════
#  ⚔️ 属性面板（回填到页面顶部占位，读取最新 data → 即时刷新）
# ════════════════════════════════════════════════════════
with stats_placeholder:
    _stats = data["stats"]
    _spent = sum(r.get("cost", 0) for r in data.get("redemption_log", []))
    _total = data.get("total_earned", 0) - _spent

    # ---- 总等级 ----
    _total_earned = data.get("total_earned", 0)
    _total_lv = _total_earned // 100
    _lv_progress = (_total_earned % 100) / 100
    _lv_remaining = 100 - (_total_earned % 100)

    _lv_c1, _lv_c2 = st.columns([1, 3])
    with _lv_c1:
        st.markdown(
            f'<div style="text-align: center; padding: 6px 0;">'
            f'<div style="font-size: 2.4rem; font-weight: 800; line-height: 1.2;">Lv.{_total_lv}</div>'
            f'<div style="font-size: 0.8rem; opacity: 0.6;">总等级</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with _lv_c2:
        st.progress(_lv_progress)
        st.caption(f"距 Lv.{_total_lv + 1} 还需 {_lv_remaining} pts · 累计 {_total_earned} pts")

    st.markdown("---")
    _panel_main, _panel_attr = get_titles(data)
    st.markdown("## ⚔️ 属性面板 · " + _panel_main + (f"（{_panel_attr}）" if _panel_attr else ""))

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
        
