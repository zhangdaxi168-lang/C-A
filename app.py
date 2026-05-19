import sys
import subprocess

# 🎯 【环境自愈流】
try:
    import streamlit as st
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])
    import streamlit as st

import itertools
import re
import urllib.request
import os

# 1. 网页全局基础配置
st.set_page_config(
    layout="wide",  # 调整为宽屏模式，看盘视野更广
    page_title="2026 实战数据审计系统", 
    page_icon="🤖"
）
# 2. 核心铁证地基数据与池子
ZODIAC_MAP = {
    '马': [1, 13, 25, 37, 49], '蛇': [2, 14, 26, 38], '龙': [3, 15, 27, 39],
    '兔': [4, 16, 28, 40],     '虎': [5, 17, 29, 41], '牛': [6, 18, 30, 42],
    '鼠': [7, 19, 31, 43],     '猪': [8, 20, 32, 44], '狗': [9, 21, 33, 45],
    '鸡': [10, 22, 34, 46],    '猴': [11, 23, 35, 47], '羊': [12, 24, 36, 48]
}

GROUPS = {'A': ['牛', '龙', '羊', '狗'], 'B': ['鼠', '兔', '马', '鸡'], 'C': ['虎', '蛇', '猴', '猪']}

ATTR_GROUPS = {
    '1': {'name': '家禽双(牛羊鸡猪)', 'list': ['牛', '羊', '鸡', '猪']},
    '2': {'name': '野兽单(鼠虎龙猴)', 'list': ['鼠', '虎', '龙', '猴']}
}

pool_A_nums = {3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48}
pool_B_nums = {1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34, 37, 40, 43, 46, 49}
pool_C_nums = {2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35, 38, 41, 44, 47}

RED_BO = [1, 2, 7, 8, 12, 13, 18, 19, 23, 24, 29, 30, 34, 35, 40, 45, 46]
BLUE_BO = [3, 4, 9, 10, 14, 15, 20, 25, 26, 31, 36, 37, 41, 42, 47, 48]
GREEN_BO = [5, 6, 11, 16, 17, 21, 22, 27, 28, 32, 33, 38, 39, 43, 44, 49]

def get_html_color_str(n):
    if n in RED_BO: return f"<span style='color:#E63946;font-weight:bold;'>{n:02d}</span>"
    elif n in GREEN_BO: return f"<span style='color:#2A9D8F;font-weight:bold;'>{n:02d}</span>"
    elif n in BLUE_BO: return f"<span style='color:#457B9D;font-weight:bold;'>{n:02d}</span>"
    return f"<span>{n:02d}</span>"

def get_pool_tag(n):
    if n in pool_A_nums: return f"<b style='color:#2A9D8F;'>A池:</b>{get_html_color_str(n)}"
    if n in pool_B_nums: return f"<b style='color:#E63946;'>B池:</b>{get_html_color_str(n)}"
    if n in pool_C_nums: return f"<b style='color:#457B9D;'>C池:</b>{get_html_color_str(n)}"
    return f"未知:{n:02d}"

def get_omission(pool, all_history):
    max_om, cur_om = 0, 0
    for item in all_history:
        if len(set(item['nums']) & pool) >= 3:
            max_om = max(max_om, cur_om)
            cur_om = 0
        else:
            cur_om += 1
    return max_om, cur_om

# 3. 🌐 账本联通流
@st.cache_data(ttl=15)
def load_data_from_network():
    data = []
    url = "https://raw.githubusercontent.com/master/A%E8%AE%B0%E5%BD%95.txt"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            lines = response.read().decode('utf-8').splitlines()
            for line in lines:
                parts = line.strip().split()
                if len(parts) >= 3:
                    draw_nums = [int(n) for n in parts[2].split('-')[:6]]
                    data.append({'id': parts[1], 'nums': draw_nums})
    except:
        if os.path.exists('A记录.txt'):
            with open('A记录.txt', 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        draw_nums = [int(n) for n in parts[2].split('-')[:6]]
                        data.append({'id': parts[1], 'nums': draw_nums})
    return sorted(data, key=lambda x: x['id'])

all_history = load_data_from_network()

# ==================== 🛠️ 左侧控制侧边栏 (Sidebar) ====================
with st.sidebar:
    st.markdown("### 🛠️ 独立控制台")
    main_choice = st.selectbox(
        "选择运行模式:",
        [
            "1. 模式 1&2 (固定组联动审计)",
            "2. 模式 3   (家双野单三)",
            "3. 模式 4   (号码自定义查询)",
            "4. 模式 5   (对子统计)",
            "5. 模式 6   (生肖自定义对撞审计)",
            "6. 模式 7   (AB.AC.BC三全中)",
            "7. 模式 8   (全量对子统计)",
            "8. 模式 9   (4波色结构对撞排行)"
        ]
    )
    st.markdown("---")
    
    # 动态在左侧渲染子配置
    if main_choice.startswith("1."):
        m_type = st.radio("审计单双数:", ["双", "单"], horizontal=True)
        q_count = st.number_input("查询期数:", min_value=5, max_value=500, value=60, step=5)
    elif main_choice.startswith("2."):
        choice = st.radio("选择分类:", ["1. 家禽双 (牛 羊 鸡 猪)", "2. 野兽单 (鼠 虎 龙 猴)"])
        q_count = st.number_input("查询期数:", min_value=5, max_value=500, value=60, step=5)
    elif main_choice.startswith("3."):
        raw_input = st.text_input("自定义号码:", value="03 06 09 12 15")
        q_count = st.number_input("查询期数:", min_value=5, max_value=500, value=30, step=5)
    elif main_choice.startswith("4."):
        sub_choice = st.selectbox("一肖双号审计项:", [
            "1. 牛 羊 鸡 猪 (常规)", "2. 鼠 虎 龙 猴 (常规)", "3. 兔 蛇 马 狗 (常规)",
            "4. 【专项】家禽双 (牛羊鸡猪) + 2+1尾数验证", "5. 【专项】野兽单 (鼠虎龙猴) + 2+1尾数验证"
        ])
        q_count = st.number_input("查询期数:", min_value=5, max_value=500, value=60, step=5)
    elif main_choice.startswith("5."):
        raw_input = st.text_input("自定义生肖:", value="牛 羊 猪")
        q_count = st.number_input("查询期数:", min_value=5, max_value=500, value=60, step=5)
    elif main_choice.startswith("6."):
        pair_choice = st.radio("选择对撞组合:", ["1. A组(四库) + B组(四花)", "2. A组(四库) + C组(四马)", "3. B组(四花) + C组(四马)"])
        q_count = st.number_input("查询期数:", min_value=5, max_value=500, value=30, step=5)
    elif main_choice.startswith("7."):
        q_count = st.number_input("核心扫描截面期数:", min_value=5, max_value=500, value=60, step=5)
    elif main_choice.startswith("8."):
        q_count = st.number_input("回溯视窗期数:", min_value=5, max_value=500, value=60, step=5)

# ==================== 📊 右侧中央主视窗 (Main Page) ====================
st.markdown("## 🤖 2026 实战数据审计舱")
st.markdown("---")

if not all_history:
    st.error("❌ 未能成功读取独立账本数据！")
else:
    # ---------------- 1. 模式 1&2 ----------------
    if main_choice.startswith("1."):
        window_data = all_history[-q_count:]
        def is_odd(z): return ZODIAC_MAP[z][0] % 2 != 0
        f_g = {k: [z for z in v if (not is_odd(z) if m_type=="双" else is_odd(z))] for k, v in GROUPS.items()}
        
        st.subheader(f"📊 {m_type}数固定组联动审计")
        pairs = [('A', 'B'), ('B', 'C'), ('A', 'C')]
        for g1, g2 in pairs:
            st.markdown(f"#### 📍 【{g1}-{g2} 战区】")
            for n1, n2 in [(1, 2), (2, 1)]:
                c1_list = list(itertools.combinations(f_g[g1], n1))
                c2_list = list(itertools.combinations(f_g[g2], n2))
                for c1, c2 in itertools.product(c1_list, c2_list):
                    z_set = list(c1 + c2)
                    pool = set()
                    for z in z_set: pool.update(ZODIAC_MAP[z])
                    
                    hit_logs = [f"**{item['id']}期** (中{len(set(item['nums'])&pool)}码: {['%02d'%n for n in sorted(list(set(item['nums'])&pool))]})" 
                                for item in window_data if len(set(item['nums'])&pool) >= 3]
                    max_om, cur_om = get_omission(pool, all_history)
                    
                    with st.expander(f"⚙️ 组合: {z_set} | 💥 命中: {len(hit_logs)} 期 | 遗漏: {cur_om} 期 (最大: {max_om}期)"):
                        if hit_logs:
                            for log in hit_logs[::-1]: st.markdown(log)
                        else: st.caption("近期无3码及以上命中。")

    # ---------------- 2. 模式 3 ----------------
    elif main_choice.startswith("2."):
        attr_key = "1" if "家禽" in choice else "2"
        window_data = all_history[-q_count:]
        target_zodiacs = ATTR_GROUPS[attr_key]['list']
        full_pool = set()
        for z in target_zodiacs: full_pool.update(ZODIAC_MAP[z])
        
        st.subheader(f"🏮 整体结构拦截明细 ({'/'.join(target_zodiacs)})")
        for item in window_data[::-1]:
            match = sorted(list(set(item['nums']) & full_pool))
            if len(match) >= 3:
                match_str = ".".join([get_html_color_str(n) for n in match])
                st.markdown(f"➡️ **{item['id']}期** | 命中 **{len(match)}** 码 | 明细: [{match_str}]", unsafe_allow_html=True)
                
        st.subheader("🏮 内部三肖热度及遗漏排行")
        results = []
        for z_set in itertools.combinations(target_zodiacs, 3):
            pool = set()
            for z in z_set: pool.update(ZODIAC_MAP[z])
            hit_logs = [f"**{item['id']}期** ({['%02d'%n for n in sorted(list(set(item['nums'])&pool))]})" 
                        for item in window_data if len(set(item['nums'])&pool) >= 3]
            max_om, cur_om = get_omission(pool, all_history)
            results.append({'z': list(z_set), 'hits': len(hit_logs), 'logs': hit_logs, 'cur_om': cur_om, 'max_om': max_om})
        
        results.sort(key=lambda x: x['hits'], reverse=True)
        for i, res in enumerate(results):
            st.markdown(f"**NO.{i+1} 组合**: `{res['z']}` | 💥 命中: {res['hits']} 期 | 当前遗漏: {res['cur_om']} 期 (最大: {res['max_om']}期)")

    # ---------------- 3. 模式 4 ----------------
    elif main_choice.startswith("3."):
        nums = re.findall(r'\d+', raw_input)
        custom_pool = set(int(n) for n in nums)
        if custom_pool:
            window_data = all_history[-q_count:]
            max_om, cur_om = get_omission(custom_pool, all_history)
            leader_A, leader_B, leader_C = 0, 0, 0
            hit_logs = []
            
            for item in window_data[::-1]:
                match = sorted(list(set(item['nums']) & custom_pool))
                if len(match) >= 3:
                    color_match_str = ".".join(get_html_color_str(n) for n in match)
                    cA = len(set(match) & pool_A_nums)
                    cB = len(set(match) & pool_B_nums)
                    cC = len(set(match) & pool_C_nums)
                    
                    leader_tag = ""
                    if cA >= 2 and cA > cB and cA > cC: leader_tag = " <b style='color:#2A9D8F;'>[A池主导]</b>"; leader_A += 1
                    elif cB >= 2 and cB > cA and cB > cC: leader_tag = " <b style='color:#E63946;'>[B池主导]</b>"; leader_B += 1
                    elif cC >= 2 and cC > cA and cC > cB: leader_tag = " <b style='color:#457B9D;'>[C池主导]</b>"; leader_C += 1
                    hit_logs.append(f"🔹 **{item['id']}期**：中 {len(match)} 码 ➔ [{color_match_str}]{leader_tag}")
            
            st.info(f"📊 历史最长遗漏: **{max_om}** 期 | 当前已连开遗漏: **{cur_om}** 期")
            st.success(f"📈 战区主导统计 ➔ 🟢 A主导: {leader_A}期 | 🔴 B主导: {leader_B}期 | 🔵 C主导: {leader_C}期")
            st.markdown("### ✨ 爆发明细")
            for log in hit_logs: st.markdown(log, unsafe_allow_html=True)

    # ---------------- 4. 模式 5 ----------------
    elif main_choice.startswith("4."):
        groups_map = {
            "1.": ['牛', '羊', '鸡', '猪'], "2.": ['鼠', '虎', '龙', '猴'], "3.": ['兔', '蛇', '马', '狗'],
            "4.": ['牛', '羊', '鸡', '猪'], "5.": ['鼠', '虎', '龙', '猴']
        }
        target_list = groups_map[sub_choice[:2]]
        is_tail_verify = "专项" in sub_choice
        window_data = all_history[-q_count:]
        overlap_dict = {}
        
        for item in window_data:
            current_period_hits = []
            draw_nums = item['nums']
            intercepted_nums = set()
            
            for z in target_list:
                z_nums = set(ZODIAC_MAP[z])
                match = sorted(list(set(draw_nums) & z_nums))
                if len(match) >= 2:
                    if is_tail_verify:
                        match_tails = set([n % 10 for n in match])
                        other_nums = [n for n in draw_nums if n not in match]
                        hit_extra_tail = sorted([n for n in other_nums if n % 10 in match_tails])
                        if hit_extra_tail:
                            m_str = ".".join([f"{n:02d}" for n in match])
                            e_str = ".".join([f"{n:02d}" for n in hit_extra_tail])
                            color_segment = f"<span style='color:#457B9D;font-weight:bold;'>{z}({m_str})</span> 配尾:<span style='color:#E63946;'>{e_str}</span>"
                            current_period_hits.append((color_segment, set(match) | set(hit_extra_tail)))
                    else:
                        intercepted_nums.update(match)
                        m_str = ".".join([f"{n:02d}" for n in match])
                        current_period_hits.append(f"<span style='color:#457B9D;font-weight:bold;'>{z}({m_str})</span>")
            
            if current_period_hits:
                if is_tail_verify:
                    all_segments_str = " | ".join([part[0] for part in current_period_hits])
                    all_used = set()
                    for part in current_period_hits: all_used.update(part[1])
                    rem_str = ".".join([f"{n:02d}" for n in sorted([n for n in draw_nums if n not in all_used])])
                    overlap_dict[item['id']] = f"{all_segments_str} — <span style='color:#2A9D8F;'>{rem_str}</span>"
                else:
                    rem_str = ".".join([f"{n:02d}" for n in sorted([n for n in draw_nums if n not in intercepted_nums])])
                    overlap_dict[item['id']] = f"{' '.join(current_period_hits)} — <span style='color:#2A9D8F;'>{rem_str}</span>"

        st.subheader("✨ 一肖双号爆发流水账本")
        for p_id in sorted(overlap_dict.keys(), reverse=True):
            st.markdown(f"📟 **{p_id}期**：{overlap_dict[p_id]}", unsafe_allow_html=True)

    # ---------------- 5. 模式 6 ----------------
    elif main_choice.startswith("5."):
        target_zodiacs = re.findall(r'[\u4e00-\u9fa5]', raw_input)
        if target_zodiacs:
            window_data = all_history[-q_count:]
            custom_pool = set()
            for z in target_zodiacs:
                if z in ZODIAC_MAP: custom_pool.update(ZODIAC_MAP[z])
            max_om, cur_om = get_omission(custom_pool, all_history)
            st.info(f"🔍 联锁组合: {target_zodiacs} | 当前遗漏: {cur_om} 期 | 最大遗漏: {max_om} 期")
            
            for item in window_data[::-1]:
                match = sorted(list(set(item['nums']) & custom_pool))
                if len(match) >= 3:
                    match_str = ".".join([get_html_color_str(n) for n in match])
                    st.markdown(f"🔹 **{item['id']}期**：爆 {len(match)} 码 ➔ [{match_str}]", unsafe_allow_html=True)

    # ---------------- 6. 模式 7 ----------------
    elif main_choice.startswith("6."):
        if "A组" in pair_choice and "B组" in pair_choice: target_zodiacs = GROUPS['A'] + GROUPS['B']
        elif "A组" in pair_choice and "C组" in pair_choice: target_zodiacs = GROUPS['A'] + GROUPS['C']
        else: target_zodiacs = GROUPS['B'] + GROUPS['C']
        
        target_pool = set()
        for z in target_zodiacs: target_pool.update(ZODIAC_MAP[z])
        max_om, cur_om = get_omission(target_pool, all_history)
        window_data = all_history[-q_count:]
        
        st.success(f"📈 结构指标 ➔ 当前遗漏: {cur_om} 期 | 历史最大遗漏: {max_om} 期")
        for item in window_data[::-1]:
            match_set = set(item['nums']) & target_pool
            if len(match_set) >= 3:
                match_str = " | ".join([get_pool_tag(n) for n in sorted(list(match_set))])
                st.markdown(f"↳ **{item['id']}期**：中 {len(match_set)} 码 [ {match_str} ]", unsafe_allow_html=True)

    # ---------------- 7. 模式 8 ----------------
    elif main_choice.startswith("7."):
        st.subheader("📊 历史全量生肖对出概率审计")
        window_data = all_history[-q_count:]
        pair_counts = {}
        
        for item in window_data:
            hit_zodiacs = []
            for z, z_nums in ZODIAC_MAP.items():
                if len(set(item['nums']) & set(z_nums)) >= 2: hit_zodiacs.append(z)
            if len(hit_zodiacs) >= 2:
                for p in itertools.combinations(sorted(hit_zodiacs), 2):
                    pair_counts[p] = pair_counts.get(p, 0) + 1
                    
        sorted_pairs = sorted(pair_counts.items(), key=lambda x: x[1], reverse=True)
        for idx, (pair, cnt) in enumerate(sorted_pairs[:15]):
            st.markdown(f"🏅 **TOP {idx+1}** ➔ `{pair[0]} 🤝 {pair[1]}` 共对出爆发: **{cnt}** 期")

    # ---------------- 8. 模式 9 ----------------
    elif main_choice.startswith("8."):
        st.subheader("🌈 波色极值对撞审计大盘")
        window_data = all_history[-q_count:]
        target_pool = set(RED_BO + BLUE_BO)
        max_om, cur_om = 0, 0
        for item in all_history:
            if len(set(item['nums']) & target_pool) >= 4: max_om = max(max_om, cur_om); cur_om = 0
            else: cur_om += 1
            
        st.info(f"📊 红蓝双波对撞指标：当前遗漏 {cur_om} 期 | 最大极值遗漏 {max_om} 期")
        for item in window_data[::-1]:
            match_set = set(item['nums']) & target_pool
            if len(match_set) >= 4:
                match_str = ".".join(get_html_color_str(n) for n in sorted(list(match_set)))
                st.markdown(f"🌈 **{item['id']}期**：爆强波 {len(match_set)} 码 ➔ [{match_str}]", unsafe_allow_html=True)
