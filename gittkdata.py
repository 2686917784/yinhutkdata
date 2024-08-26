import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import base64
import requests
# 设置页面配置
st.set_page_config(page_title="TikTok达人数据查询系统", layout="wide")

# 配置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 标题
st.title("TikTok达人数据查询系统")

# GitHub中Excel文件的URL
EXCEL_FILE_URL = "https://github.com/2686917784/yinhutkdata/raw/main/Aeg001.xlsx"

# 读取Excel文件
@st.cache_data
def load_data():
    try:
        response = requests.get(EXCEL_FILE_URL)
        response.raise_for_status()
        df = pd.read_excel(io.BytesIO(response.content), engine='openpyxl')
        df['达人id'] = df['达人id'].astype(str)
        df.set_index('达人id', inplace=True)
        return df
    except Exception as e:
        st.error(f"加载Excel文件时出错：{e}")
        return None

# 格式化互动率
def format_interaction_rate(rate):
    if isinstance(rate, str):
        return float(rate.strip('%')) / 100
    elif isinstance(rate, (int, float, np.number)):
        return float(rate)
    else:
        return 0

# 深度分析函数
def analyze_data(daren_data):
    try:
        # 处理粉丝占比数据
        fan_ratio_str = daren_data['粉丝占比']
        fan_gender, fan_ratio = fan_ratio_str.split()
        fan_ratio = float(fan_ratio.strip('%')) / 100

        # 处理互动率
        interaction_rate = format_interaction_rate(daren_data.get('互动率', 0))

        analysis = f"""
        达人 {daren_data['达人名称']} 深度数据分析：

        1. 受众分析与商业价值关联：
           该达人属于{daren_data['达人类型']}类型，拥有{daren_data['粉丝数量']:,}名粉丝，其中{fan_gender}粉丝占比{fan_ratio:.2%}。
           主要受众年龄为{daren_data['主要年龄']}。这个年龄段与商品交易总额（¥{daren_data['商品交易总额']:,.2f}）
           和成交件数（{daren_data['成交件数']:,}）的关系显示：
           {analyze_audience_commercial_value(daren_data)}

        2. 内容效果与互动性分析：
           平均播放数为{daren_data['平均播放数']:,}，互动率为{interaction_rate:.2%}。
           {analyze_content_engagement(daren_data)}

        3. 增长潜力评估：
           {analyze_growth_potential(daren_data)}

        4. 综合评估与建议：
           {generate_comprehensive_conclusion(daren_data)}
        """
        return analysis
    except KeyError as e:
        return f"数据分析错误：缺少必要的数据字段 {e}"
    except ValueError as e:
        return f"数据分析错误：数据格式不正确 {e}"
    except Exception as e:
        return f"数据分析过程中发生未知错误：{e}"

# 辅助分析函数
def analyze_audience_commercial_value(data):
    try:
        age_group = data['主要年龄']
        transaction_amount = float(data['商品交易总额'])
        transaction_count = int(data['成交件数'])
        fan_ratio_str = data['粉丝占比']
        fan_gender = fan_ratio_str.split()[0]

        gender_analysis = f"粉丝群体以{fan_gender}为主，" if fan_gender in ['男性', '女性'] else "粉丝性别分布较为均衡，"

        if '18-23' in age_group:
            return f"{gender_analysis}主要受众为年轻群体，购买力可能较低但购买频率高。建议关注性价比高的产品。"
        elif '24-30' in age_group:
            return f"{gender_analysis}核心消费群体，购买力强。当前交易总额与成交件数表现{evaluate_performance(transaction_amount, transaction_count)}，建议深挖这一年龄段的消费需求。"
        else:
            return f"{gender_analysis}成熟消费群体，注重品质。可能需要更有说服力的内容来促进交易。"
    except (KeyError, ValueError) as e:
        return f"无法分析受众商业价值：{e}"

def analyze_content_engagement(data):
    try:
        play_count = int(data['平均播放数'])
        engagement_rate = format_interaction_rate(data.get('互动率', 0))

        if engagement_rate > 0.05:
            return f"内容互动性强，粉丝参与度高。建议保持现有内容策略，可以尝试更多互动类型的内容。"
        elif play_count > 10000:
            return f"内容传播广泛但互动率较低。建议优化内容，增加互动元素，提高粉丝参与度。"
        else:
            return f"内容效果有待提升。建议分析高播放量视频的特点，优化内容策略。"
    except (ValueError, KeyError) as e:
        return f"无法分析内容效果与互动性：{e}"

def analyze_growth_potential(data):
    try:
        if data['是否为快速成长榜'] == '1':
            return f"该达人正处于快速增长期，具有高增长潜力。建议密切关注并考虑加大合作力度。"
        else:
            return f"达人增长趋势平稳。建议关注其内容创新能力和粉丝忠诚度，评估长期发展潜力。"
    except KeyError as e:
        return f"无法分析增长潜力：{e}"

def generate_comprehensive_conclusion(data):
    try:
        factors = [
            data['达人类型'],
            int(data['粉丝数量']),
            float(data['商品交易总额']),
            format_interaction_rate(data.get('互动率', 0)),
            data['是否为快速成长榜']
        ]
        if data['是否为快速成长榜'] == '是' and factors[3] > 0.05:
            return "该达人展现出强劲的增长潜力和良好的粉丝互动，是理想的合作对象。建议制定长期合作计划，可考虑独家合作或深度内容合作。"
        elif factors[2] > 10000:
            return "该达人具有强大的商业转化能力。建议重点关注产品匹配度，选择适合的产品进行深度合作。"
        else:
            return "该达人在某些方面表现良好，但仍有提升空间。建议进行短期合作测试，重点关注内容质量和粉丝互动，评估长期合作的可能性。"
    except (KeyError, ValueError) as e:
        return f"无法生成综合结论：{e}"

def evaluate_performance(amount, count):
    if amount > 10000 and count > 1000:
        return "优秀"
    elif amount > 1000 or count > 100:
        return "良好"
    else:
        return "一般"

# 新增: 评估合作潜力函数
def evaluate_cooperation_potential(data):
    score = 0
    reasons = []

    # 评估粉丝数量
    fans = int(data['粉丝数量'])
    if fans > 100000:
        score += 30
        reasons.append("大量粉丝基础")
    elif fans > 50000:
        score += 20
        reasons.append("较好的粉丝基础")
    elif fans > 10000:
        score += 10
        reasons.append("一定的粉丝基础")

    # 评估商品交易总额
    transaction = float(data['商品交易总额'])
    if transaction > 10000:
        score += 30
        reasons.append("强劲的商业转化能力")
    elif transaction > 5000:
        score += 20
        reasons.append("良好的商业转化能力")
    elif transaction > 1000:
        score += 10
        reasons.append("一定的商业转化能力")

    # 评估互动率
    interaction_rate = format_interaction_rate(data['互动率'])
    if interaction_rate > 0.05:
        score += 20
        reasons.append("高互动率")
    elif interaction_rate > 0.02:
        score += 10
        reasons.append("良好的互动率")

    # 评估是否为快速成长榜
    if data['是否为快速成长榜'] == '1':
        score += 20
        reasons.append("快速增长潜力")

    # 根据得分给出建议
    if score >= 80:
        recommendation = "强烈建议合作"
    elif score >= 60:
        recommendation = "建议合作"
    elif score >= 40:
        recommendation = "可以考虑小规模试探性合作"
    else:
        recommendation = "暂不建议合作"

    return recommendation, score, reasons

# 主程序
df = load_data()

if df is not None:
    # 创建侧边栏用于搜索和筛选
    st.sidebar.header("搜索和筛选选项")
    search_term = st.sidebar.text_input("输入达人ID")

    # 达人类型筛选
    daren_types = ['全部'] + list(df['达人类型'].unique())
    selected_type = st.sidebar.selectbox("选择达人类型", daren_types)

    if st.sidebar.button("搜索"):
        if search_term:
            # 使用索引进行快速搜索
            result = df[df.index == search_term]

            if selected_type != '全部':
                result = result[result['达人类型'] == selected_type]

            if not result.empty:
                st.success(f"找到匹配的记录")

                st.subheader("搜索结果")
                display_columns = ['达人名称', '达人类型', '粉丝数量', '商品交易总额', '成交件数', '平均播放数',
                                   '互动率', '平均评分']
                st.dataframe(result[display_columns].reset_index(), height=80)

                # 数据导出功能
                csv = result.reset_index().to_csv().encode('utf-8')
                st.download_button(
                    label="下载搜索结果",
                    data=csv,
                    file_name='daren_search_results.csv',
                    mime='text/csv',
                )

                # 获取达人数据
                daren_data = result.iloc[0]

                # 显示分析结论
                st.subheader("达人数据深度分析")
                analysis = analyze_data(daren_data)
                st.markdown(analysis)

                # 创建两列布局
                col1, col2, col3  = st.columns([1, 1, 1])

                with col1:
                    # 使用Plotly创建雷达图
                    labels = ['粉丝数量', '商品交易总额', '成交件数', '平均播放数', '互动率', '平均']
                    values = [float(daren_data[f'{label}评分']) for label in labels]

                    fig = go.Figure(data=go.Scatterpolar(
                        r=values,
                        theta=labels,
                        fill='toself',
                        name=daren_data['达人名称']
                    ))

                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, 100]
                            )),
                        showlegend=False,
                        title=f"达人: {daren_data['达人名称']} 的评分雷达图"
                    )

                    # 添加自定义的悬停文本
                    hover_text = [f"{label}: {value:.2f}" for label, value in zip(labels, values)]
                    fig.data[0].hoverinfo = 'text'
                    fig.data[0].hovertext = hover_text

                    # 在Streamlit中显示Plotly图表
                    st.plotly_chart(fig, use_container_width=True)

                with col3:
                    # 显示详细信息
                    st.subheader("达人详细信息")
                    fan_ratio_str = daren_data.get('粉丝占比', '未知')
                    fan_gender, fan_ratio = fan_ratio_str.split()
                    fan_ratio = float(fan_ratio.strip('%')) / 100
                    info = {
                        "达人ID": daren_data.name,
                        "达人名称": daren_data.get('达人名称', '未知'),
                        "达人类型": daren_data.get('达人类型', '未知'),
                        "粉丝数量": f"{int(daren_data.get('粉丝数量', 0)):,}",
                        "粉丝性别占比": f"{fan_gender} {fan_ratio:.2%}",
                        "商品交易总额": f"¥{float(daren_data.get('商品交易总额', 0)):,.2f}",
                        "成交件数": f"{int(daren_data.get('成交件数', 0)):,}",
                        "平均播放数": f"{int(daren_data.get('平均播放数', 0)):,}",
                        "互动率": f"{format_interaction_rate(daren_data.get('互动率', 0)):.2%}",
                        "平均评分": f"{float(daren_data.get('平均评分', 0)):.2f}"
                    }
                    for key, value in info.items():
                        st.markdown(f"<span style='font-size: 18px;'><b>{key}:</b> {value}</span>",
                                    unsafe_allow_html=True)
                with col2:
                    # 新增: 显示合作建议
                    recommendation, score, reasons = evaluate_cooperation_potential(daren_data)
                    st.subheader("合作建议")
                    st.write(f"建议: {recommendation}")
                    st.write(f"评分: {score}")
                    st.write("理由:")
                    for reason in reasons:
                        st.write(f"- {reason}")

            else:
                st.warning(f"未找到匹配 ID '{search_term}' 的记录")
        else:
            st.warning("请输入达人ID")

else:
    st.error("无法加载数据，请检查Excel文件路径是否正确。")
