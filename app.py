import streamlit as st
import itertools
import re

# 1. 设置网页基础参数（优化移动端浏览体验）
st.set_page_config(
    layout="centered", 
    page_title="2026结构对撞审计舱", 
    page_icon="🤖"
)

# 2. 地基配置数据（铁证死锁马年口诀绝对主导版）
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

# 固定三个池子的号码边界
pool_A_nums = {3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48}
pool_B_nums = {1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34, 37, 40, 43, 46, 49}
pool_C_nums = {2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35, 38, 41, 44, 47}

# 3. 自动化深色波色调色盘
RED_BO = [1, 2, 7, 8, 12, 13, 18, 19, 23, 24, 29, 30, 34, 35, 40, 45, 46]
BLUE_BO = [3, 4, 9, 10, 14, 15, 20, 25, 26, 31, 36, 37, 41, 42, 47, 48]
GREEN_BO = [5, 6, 11, 16, 17, 21, 22, 27, 28, 32, 33, 38, 39, 43, 44, 49]

def get_html_color_str(n):
    """网页级调色净化器"""
    if n in RED_BO:
        return f"<span style='color:#E63946;font-weight:bold;'>{n:02d}</span>"
    elif n in GREEN_BO:
        return f"<span style='color:#2A9D8F;font-weight:bold;'>{n:02d}</span>"
    elif n in BLUE_BO:
        return f"<span style='color:#457B9D;font-weight:bold;'>{n:02d}</span>"
    return f"<span>{n:02d}</span>"

# 4. 动态加载 A记录.txt 引擎
@st.cache_data(ttl=3600)  # 网页缓存提速，每小时自动刷新
def load_data_from_file():
    data = []
    try:
        with open('A记录.txt', 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 3:
                    # 抓取前6位开奖号进行对撞
                    draw_nums = [int(n) for n in parts[2].split('-')[:6]]
                    data.append({'id': parts[1], 'nums': draw_nums})
    except Exception as e:
        st.error(f"⚠️ 找不到数据文件 'A记录.txt' 或读取错误：{e}")
    return sorted(data, key=lambda x: x['id'])

# 页面顶部精美排版
st.title("🤖 智能结构对撞审计舱")
st.caption("2026马年铁证单机版 ➔ 已适配 iOS 独立看盘流")

# 载入流水账本
all_history = load_data_from_file()

if all_history:
    st.success(f"📊 成功链接数据源！当前已加载历史流水：{len(all_history)} 期")
    
    # 5. 极简看盘指令交互槽
    user_command = st.text_input(
        "💬 请输入看盘指令：", 
        value="AC 30", 
        placeholder="例如：AB 30、或者 BC 60"
    )
    
    if user_command:
        raw_text = str(user_command).upper().replace(" ", "")
        
        # 智能匹配阵营
        combo = None
        if "AB" in raw_text or ("A" in raw_text and "B" in raw_text):
            combo = "1"
        elif "AC" in raw_text or ("A" in raw_text and "C" in raw_text):
            combo = "2"
        elif "BC" in raw_text or ("B" in raw_text and "C" in raw_text):
            combo = "3"
            
        # 智能匹配截取期数
        q_count = 60
        nums = re.findall(r'\d+', raw_text)
        for n in nums:
            if n not in ['1', '2', '3']:
                q_count = int(n)
                break
                
        if not combo:
            st.warning("⚠️ 无法自动识别战区，请输入类似 'AB 45' 或 'BC 60' 的指令")
        else:
            g1_k, g2_k = ('A', 'B') if combo == '1' else (('A', 'C') if combo == '2' else ('B', 'C'))
            
            # 锁定对撞母池
            target_zodiacs = GROUPS[g1_k] + GROUPS[g2_k]
            custom_pool = set()
            for z in target_zodiacs: 
                custom_pool.update(ZODIAC_MAP[z])
            
            # 划定时间视窗
            window_data = all_history[-q_count:]
            
            # 核心计算：遗漏与命中
            cnt = 0
            hit_logs = []
            
            # 全历史大盘扫描（用于精细计算当前的绝对遗漏）
            max_om, temp_om = 0, 0
            for item in all_history:
                if len(set(item['nums']) & custom_pool) >= 3:
                    if temp_om > max_om: 
                        max_om = temp_om
                    temp_om = 0
                else: 
                    temp_om += 1
            
            # 视窗期内流水生成
            for item in window_data[::-1]:
                match_set = set(item['nums']) & custom_pool
                if len(match_set) >= 3:
                    cnt += 1
                    match_A = sorted(list(match_set & pool_A_nums))
                    match_B = sorted(list(match_set & pool_B_nums))
                    match_C = sorted(list(match_set & pool_C_nums))
                    
                    pool_strings = []
                    if match_A:
                        pool_strings.append(f"<b style='color:#2A9D8F;'>A池:</b>" + ".".join(get_html_color_str(n) for n in match_A))
                    if match_B:
                        pool_strings.append(f"<b style='color:#E63946;'>B池:</b>" + ".".join(get_html_color_str(n) for n in match_B))
                    if match_C:
                        pool_strings.append(f"<b style='color:#457B9D;'>C池:</b>" + ".".join(get_html_color_str(n) for n in match_C))
                    
                    match_str = " | ".join(pool_strings)
                    hit_logs.append(f"**🔹 {item['id']}期**：爆 {len(match_set)} 码 ➔ [{match_str}]")
            
            # 6. 大字号数据看板渲染
            st.markdown("---")
            st.info(f"🎯 **当前死锁战区**：{g1_k}组 + {g2_k}组 对撞  |  🔍 **回溯周期**：近 {q_count} 期")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("⚡ 爆发期数", f"{cnt} 期")
            col2.metric("⏳ 当前遗漏", f"{temp_om} 期")
            col3.metric("📊 历史最大遗漏", f"{max_om} 期")
            
            st.markdown("### 📜 3码以上跨池爆发流水账本")
            st.markdown("---")
            
            if hit_logs:
                for log in hit_logs:
                    st.markdown(log, unsafe_allow_html=True)
            else:
                st.write("💨 该时间截面内未发生 3 码以上爆发。")
else:
    st.info("💡 请确保 `app.py` 同级目录下放了最新的 `A记录.txt`。")