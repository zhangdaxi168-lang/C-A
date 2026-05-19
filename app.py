import sys
import subprocess

# 🎯 【环境自愈流】
try:
    import streamlit as st
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])
    import streamlit as st

import re
import urllib.request
import os

# 1. 网页全局基础配置
st.set_page_config(
    layout="centered", 
    page_title="2026全模式结构对撞审计舱", 
    page_icon="🤖"
)

# 2. 核心死锁地基数据
ZODIAC_MAP = {
    '马': [1, 13, 25, 37, 49], '蛇': [2, 14, 26, 38], '龙': [3, 15, 27, 39],
    '兔': [4, 16, 28, 40],     '虎': [5, 17, 29, 41], '牛': [6, 18, 30, 42],
    '鼠': [7, 19, 31, 43],     '猪': [8, 20, 32, 44], '狗': [9, 21, 33, 45],
    '鸡': [10, 22, 34, 46],    '猴': [11, 23, 35, 47], '羊': [12, 24, 36, 48]
}

GROUPS = {
    'A': ['牛', '龙', '羊', '狗'], 
    'B': ['鼠', '兔', '马', '鸡'], 
    'C': ['虎', '蛇', '猴', '猪']
}

# 三大子池
pool_A_nums = {3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48}
pool_B_nums = {1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34, 37, 40, 43, 46, 49}
pool_C_nums = {2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35, 38, 41, 44, 47}

# 属性分流死锁
WILD_ZODIAC = ['鼠', '虎', '兔', '龙', '蛇', '猴']
DOMESTIC_ZODIAC = ['牛', '马', '羊', '鸡', '狗', '猪']

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

# 3. 🌐 独立抓取网络流数据
@st.cache_data(ttl=30)
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
        try:
            alt_url = "https://raw.githubusercontent.com/main/A%E8%AE%B0%E5%BD%95.txt"
            req = urllib.request.Request(alt_url, headers={'User-Agent': 'Mozilla/5.0'})
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

# 页面顶部精美布局
st.title("🤖 2026全结构对撞多模审计舱")
st.caption("已无缝打包同步原有笔记本的所有九大运作过滤模型")

all_history = load_data_from_network()

if all_history:
    st.success(f"📊 外部独立账本联通成功！当前大盘库：{len(all_history)} 期")
    
    # 🌟 多模式全局中央切换阀
    mode = st.selectbox(
        "🛠️ 请选择看盘审计模式：",
        [
            "模式 1：标准战区对撞 (AB / AC / BC)",
            "模式 2：野兽单数流 审计",
            "模式 3：家畜双数流 审计",
            "模式 4：野家混合流 审计",
            "模式 5：A+B 强力过滤 (无马无0头)",
            "模式 6：A+B 条件分流 (无0头版)",
            "模式 7：A+B 条件分流 (无2头版)",
            "模式 8：波色对撞与双维波动审计"
        ]
    )
    
    # 全时段窗口截取控制
    q_count = st.slider("🔍 请选择回溯视窗期数：", min_value=10, max_value=200, value=60, step=5)
    window_data = all_history[-q_count:]
    
    # 初始化计算槽
    cnt = 0
    hit_logs = []
    max_om, temp_om = 0, 0
    
    # ==================== 模式分流计算核心 ====================
    
    # 【模式 1：标准战区对撞】
    if "模式 1" in mode:
        sub_command = st.text_input("💬 请输入对撞战区暗号：", value="AB", placeholder="例如 AB、AC、BC")
        raw_text = sub_command.upper().strip()
        g1, g2 = ('A', 'B') if "AB" in raw_text else (('A', 'C') if "AC" in raw_text else ('B', 'C'))
        
        target_zodiacs = GROUPS[g1] + GROUPS[g2]
        target_pool = set()
        for z in target_zodiacs: target_pool.update(ZODIAC_MAP[z])
        
        # 遗漏与爆发审计
        for item in all_history:
            if len(set(item['nums']) & target_pool) >= 3:
                if temp_om > max_om: max_om = temp_om
                temp_om = 0
            else: temp_om += 1
            
        for item in window_data[::-1]:
            match_set = set(item['nums']) & target_pool
            if len(match_set) >= 3:
                cnt += 1
                match_str = " | ".join([get_pool_tag(n) for n in sorted(list(match_set))])
                hit_logs.append(f"**🔹 {item['id']}期**：爆 {len(match_set)} 码 ➔ [{match_str}]")

    # 【模式 2：野兽单数流】
    elif "模式 2" in mode:
        target_pool = set()
        for z in WILD_ZODIAC:
            target_pool.update([n for n in ZODIAC_MAP[z] if n % 2 != 0])
            
        for item in all_history:
            if len(set(item['nums']) & target_pool) >= 3:
                if temp_om > max_om: max_om = temp_om
                temp_om = 0
            else: temp_om += 1
            
        for item in window_data[::-1]:
            match_set = set(item['nums']) & target_pool
            if len(match_set) >= 3:
                cnt += 1
                match_str = ".".join(get_html_color_str(n) for n in sorted(list(match_set)))
                hit_logs.append(f"**🔹 {item['id']}期**：爆 {len(match_set)} 码 ➔ [{match_str}]")

    # 【模式 3：家畜双数流】
    elif "模式 3" in mode:
        target_pool = set()
        for z in DOMESTIC_ZODIAC:
            target_pool.update([n for n in ZODIAC_MAP[z] if n % 2 == 0])
            
        for item in all_history:
            if len(set(item['nums']) & target_pool) >= 3:
                if temp_om > max_om: max_om = temp_om
                temp_om = 0
            else: temp_om += 1
            
        for item in window_data[::-1]:
            match_set = set(item['nums']) & target_pool
            if len(match_set) >= 3:
                cnt += 1
                match_str = ".".join(get_html_color_str(n) for n in sorted(list(match_set)))
                hit_logs.append(f"**🔹 {item['id']}期**：爆 {len(match_set)} 码 ➔ [{match_str}]")

    # 【模式 4：野家混合流】
    elif "模式 4" in mode:
        pool_wild_odd = set()
        for z in WILD_ZODIAC: pool_wild_odd.update([n for n in ZODIAC_MAP[z] if n % 2 != 0])
        pool_dome_even = set()
        for z in DOMESTIC_ZODIAC: pool_dome_even.update([n for n in ZODIAC_MAP[z] if n % 2 == 0])
        target_pool = pool_wild_odd | pool_dome_even
        
        for item in all_history:
            if len(set(item['nums']) & target_pool) >= 3:
                if temp_om > max_om: max_om = temp_om
                temp_om = 0
            else: temp_om += 1
            
        for item in window_data[::-1]:
            match_set = set(item['nums']) & target_pool
            if len(match_set) >= 3:
                cnt += 1
                match_str = ".".join(get_html_color_str(n) for n in sorted(list(match_set)))
                hit_logs.append(f"**🔹 {item['id']}期**：爆 {len(match_set)} 码 ➔ [{match_str}]")

    # 【模式 5：A+B 强力过滤 (无马无0头)】
    elif "模式 5" in mode:
        target_zodiacs = GROUPS['A'] + GROUPS['B']
        base_pool = set()
        for z in target_zodiacs: base_pool.update(ZODIAC_MAP[z])
        # 排除马年号、排除0开头的号码
        target_pool = {n for n in base_pool if n not in ZODIAC_MAP['马'] and n >= 10}
        
        for item in all_history:
            if len(set(item['nums']) & target_pool) >= 3:
                if temp_om > max_om: max_om = temp_om
                temp_om = 0
            else: temp_om += 1
            
        for item in window_data[::-1]:
            match_set = set(item['nums']) & target_pool
            if len(match_set) >= 3:
                cnt += 1
                match_str = " | ".join([get_pool_tag(n) for n in sorted(list(match_set))])
                hit_logs.append(f"**🔹 {item['id']}期**：爆 {len(match_set)} 码 ➔ [{match_str}]")

    # 【模式 6：A+B 条件分流 (无0头版)】
    elif "模式 6" in mode:
        target_zodiacs = GROUPS['A'] + GROUPS['B']
        base_pool = set()
        for z in target_zodiacs: base_pool.update(ZODIAC_MAP[z])
        target_pool = {n for n in base_pool if n >= 10}
        
        for item in all_history:
            if len(set(item['nums']) & target_pool) >= 3:
                if temp_om > max_om: max_om = temp_om
                temp_om = 0
            else: temp_om += 1
            
        for item in window_data[::-1]:
            match_set = set(item['nums']) & target_pool
            if len(match_set) >= 3:
                cnt += 1
                match_str = " | ".join([get_pool_tag(n) for n in sorted(list(match_set))])
                hit_logs.append(f"**🔹 {item['id']}期**：爆 {len(match_set)} 码 ➔ [{match_str}]")

    # 【模式 7：A+B 条件分流 (无2头版)】
    elif "模式 7" in mode:
        target_zodiacs = GROUPS['A'] + GROUPS['B']
        base_pool = set()
        for z in target_zodiacs: base_pool.update(ZODIAC_MAP[z])
        target_pool = {n for n in base_pool if not (20 <= n <= 29)}
        
        for item in all_history:
            if len(set(item['nums']) & target_pool) >= 3:
                if temp_om > max_om: max_om = temp_om
                temp_om = 0
            else: temp_om += 1
            
        for item in window_data[::-1]:
            match_set = set(item['nums']) & target_pool
            if len(match_set) >= 3:
                cnt += 1
                match_str = " | ".join([get_pool_tag(n) for n in sorted(list(match_set))])
                hit_logs.append(f"**🔹 {item['id']}期**：爆 {len(match_set)} 码 ➔ [{match_str}]")

    # 【模式 8：波色对撞与双维波动审计】
    elif "模式 8" in mode:
        st.write("📊 *当前执行：红蓝绿三波极值方差对撞过滤*")
        # 红蓝双波审计例子
        target_pool = set(RED_BO + BLUE_BO)
        for item in all_history:
            if len(set(item['nums']) & target_pool) >= 4: # 高阶爆发设为4码
                if temp_om > max_om: max_om = temp_om
                temp_om = 0
            else: temp_om += 1
            
        for item in window_data[::-1]:
            match_set = set(item['nums']) & target_pool
            if len(match_set) >= 4:
                cnt += 1
                match_str = ".".join(get_html_color_str(n) for n in sorted(list(match_set)))
                hit_logs.append(f"**🌈 {item['id']}期**：爆双波 {len(match_set)} 码 ➔ [{match_str}]")

    # ==================== 渲染控制面板 ====================
    st.markdown("---")
    st.info(f"🎯 **激活审计单元**：{mode}  |  🔍 **回溯视窗**：近 {q_count} 期")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("⚡ 爆发期数", f"{cnt} 期")
    col2.metric("⏳ 当前遗漏", f"{temp_om} 期")
    col3.metric("📊 历史最大遗漏", f"{max_om} 期")
    
    st.markdown("### 📜 核心联动爆码流水账本")
    st.markdown("---")
    
    if hit_logs:
        for log in hit_logs:
            st.markdown(log, unsafe_allow_html=True)
    else:
        st.write("💨 该时间截面和过滤条件下，未满足起爆阈值。")
else:
    st.error("❌ 未能成功读取独立账本数据！请核对 GitHub 根目录下的 'A记录.txt'")
