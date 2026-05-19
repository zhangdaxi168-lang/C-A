import streamlit as st
import itertools
import re

# ====================== 页面配置 ======================
st.set_page_config(page_title="2026 马年地基分析", layout="wide", initial_sidebar_state="expanded")
st.title("🧧 2026 马年地基号码分析系统")
st.markdown("**严格对撞 · 遗漏统计 · 波色可视化 · 主导分析**")

# ====================== 加载数据 ======================
@st.cache_data
def load_data():
    data = []
    try:
        with open('A记录.txt', 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 3:
                    draw_nums = [int(n) for n in parts[2].split('-')[:6]]
                    data.append({'id': parts[1], 'nums': draw_nums})
    except Exception as e:
        st.error(f"读取 A记录.txt 失败: {e}")
    return sorted(data, key=lambda x: x['id'])

all_history = load_data()

if not all_history:
    st.warning("⚠️ 未检测到历史数据，请确保 A记录.txt 存在且格式正确")
    st.stop()

st.success(f"✅ 已加载 {len(all_history)} 期历史数据")

# ====================== 公共数据 ======================
ZODIAC_MAP = {
    '马': [1, 13, 25, 37, 49], '蛇': [2, 14, 26, 38], '龙': [3, 15, 27, 39],
    '兔': [4, 16, 28, 40], '虎': [5, 17, 29, 41], '牛': [6, 18, 30, 42],
    '鼠': [7, 19, 31, 43], '猪': [8, 20, 32, 44], '狗': [9, 21, 33, 45],
    '鸡': [10, 22, 34, 46], '猴': [11, 23, 35, 47], '羊': [12, 24, 36, 48]
}

GROUPS = {'A': ['牛', '龙', '羊', '狗'], 'B': ['鼠', '兔', '马', '鸡'], 'C': ['虎', '蛇', '猴', '猪']}
ATTR_GROUPS = {
    '1': {'name': '家禽双(牛羊鸡猪)', 'list': ['牛', '羊', '鸡', '猪']},
    '2': {'name': '野兽单(鼠虎龙猴)', 'list': ['鼠', '虎', '龙', '猴']}
}

RED_BO = [1,2,7,8,12,13,18,19,23,24,29,30,34,35,40,45,46]
BLUE_BO = [3,4,9,10,14,15,20,25,26,31,36,37,41,42,47,48]
GREEN_BO = [5,6,11,16,17,21,22,27,28,32,33,38,39,43,44,49]

pool_A_nums = {3,6,9,12,15,18,21,24,27,30,33,36,39,42,45,48}
pool_B_nums = {1,4,7,10,13,16,19,22,25,28,31,34,37,40,43,46,49}
pool_C_nums = {2,5,8,11,14,17,20,23,26,29,32,35,38,41,44,47}

def get_color_num_str(n):
    if n in RED_BO: return f"**{n:02d}**"   # Streamlit 支持 markdown 加粗
    if n in GREEN_BO: return f":green[{n:02d}]"
    if n in BLUE_BO: return f":blue[{n:02d}]"
    return f"{n:02d}"

def get_omission(pool, history):
    max_om, cur_om = 0, 0
    for item in history:
        if len(set(item['nums']) & pool) >= 3:
            max_om = max(max_om, cur_om)
            cur_om = 0
        else:
            cur_om += 1
    return max_om, cur_om

# ====================== 侧边栏 ======================
st.sidebar.header("🎯 分析模式")
mode = st.sidebar.selectbox("请选择模式", [
    "模式 4：号码自定义查询",
    "模式 6：生肖自定义对撞",
    "模式 1&2：固定组联动审计",
    "模式 3：属性穿透排行",
    "模式 5：一肖双号审计",
    "模式 7：结构对撞审计"
])

# ====================== 模式 4 ======================
if mode == "模式 4：号码自定义查询":
    st.header("模式 4：号码自定义查询")
    raw = st.text_input("请输入自定义号码", placeholder="6 18 30 12 24 或 6,18,30")
    q_count = st.slider("查询期数", 10, 100, 40)
    
    if st.button("🚀 开始查询", type="primary"):
        nums = re.findall(r'\d+', raw)
        custom_pool = set(int(n) for n in nums)
        if not custom_pool:
            st.error("未检测到有效号码")
        else:
            window = all_history[-q_count:]
            max_om, cur_om = get_omission(custom_pool, all_history)
            
            st.subheader(f"号码池: {sorted(custom_pool)}")
            st.write(f"**历史最长遗漏**: {max_om} 期 | **当前遗漏**: {cur_om} 期")
            
            for item in window[::-1]:
                match = sorted(list(set(item['nums']) & custom_pool))
                if len(match) >= 3:
                    colored = " ".join(get_color_num_str(n) for n in match)
                    st.success(f"**{item['id']}期** 中 {len(match)} 码 → {colored}")

# ====================== 其他模式（后续可继续扩展） ======================
elif mode == "模式 6：生肖自定义对撞":
    st.header("模式 6：生肖自定义对撞")
    raw_z = st.text_input("请输入生肖（空格分隔）", placeholder="牛 羊 猪")
    q_count = st.slider("查询期数", 10, 100, 40)
    
    if st.button("🚀 开始查询", type="primary"):
        target_z = re.findall(r'[\u4e00-\u9fa5]+', raw_z)
        custom_pool = set()
        for z in target_z:
            if z in ZODIAC_MAP:
                custom_pool.update(ZODIAC_MAP[z])
        
        if custom_pool:
            st.write("正在计算...")
            # 这里可以继续补充完整逻辑...
            st.info("模式6 核心逻辑已准备好，可继续扩展")
        else:
            st.error("请输入有效生肖")

else:
    st.info("👈 请从左侧选择模式")
    st.write("当前支持完整运行 **模式4**，其他模式可继续按需完善")

st.caption("Made with ❤️ for 2026 马年分析")
