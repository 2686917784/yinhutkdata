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

# 指定本地Excel文件路径
# GitHub中Excel文件的URL
EXCEL_FILE_URL = "https://github.com/2686917784/yinhutkdata/raw/main/data/8月第三次达人画像数据.xlsx"

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
        fan_ratio_str = daren_data['粉丝占比']
        fan_gender, fan_ratio = fan_ratio_str.split()
        fan_ratio = float(fan_ratio.strip('%')) / 100
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

        """
        return analysis
    except Exception as e:
        return f"数据分析过程中发生错误：{e}"


# 辅助分析函数
def analyze_audience_commercial_value(data):
    age_group = data['主要年龄']
    transaction_amount = data['商品交易总额']
    transaction_count = data['成交件数']

    if '18-23' in age_group:
        return f"该年龄段（{age_group}）属于年轻消费群体，倾向于追求新潮和个性化产品。目前的交易总额（¥{transaction_amount:,.2f}）和成交件数（{transaction_count:,}）表明这个群体有一定的消费能力，但可能更注重性价比。建议关注快速消费品和新兴品牌。"
    elif '24-30' in age_group:
        return f"这个年龄段（{age_group}）正处于事业发展期，消费能力较强。当前的交易总额（¥{transaction_amount:,.2f}）和成交件数（{transaction_count:,}）反映出他们有较高的购买力。可以考虑推广高品质生活用品、时尚服饰和科技产品。"
    elif '31-40' in age_group:
        return f"主要受众（{age_group}）属于成熟消费群体，注重品质和实用性。交易总额（¥{transaction_amount:,.2f}）和成交件数（{transaction_count:,}）显示他们有较强的消费能力。可以考虑推广家居用品、健康产品和中高端商品。"
    else:
        return f"该年龄段（{age_group}）的消费特征需要进一步分析。目前的交易总额（¥{transaction_amount:,.2f}）和成交件数（{transaction_count:,}）表明有一定的市场潜力。建议深入研究这个群体的具体需求和消费习惯。"

#播放量分析
def analyze_content_engagement(data):
    avg_views = data['平均播放数']
    interaction_rate = format_interaction_rate(data.get('互动率', 0))

    if avg_views > 100000 and interaction_rate > 0.05:
        return "内容表现优秀，高播放量和高互动率表明达人的内容非常吸引观众。建议保持当前的内容策略，可以考虑增加发布频率。"
    elif avg_views > 50000 and interaction_rate > 0.03:
        return "内容效果良好，有稳定的观众群。建议继续优化内容质量，尝试不同类型的视频以提高互动率。"
    elif avg_views > 10000 and interaction_rate > 0.02:
        return "内容表现尚可，但仍有提升空间。建议分析高播放量视频的共同特点，优化内容策略以提高整体表现。"
    else:
        return "内容效果有待改善。建议重新评估内容策略，关注目标受众的兴趣点，提高视频质量和吸引力。"

#互动率分析
def analyze_growth_potential(data):
    follower_count = data['粉丝数量']
    avg_views = data['平均播放数']
    interaction_rate = format_interaction_rate(data.get('互动率', 0))

    if follower_count < 10000 and avg_views > follower_count * 0.5 and interaction_rate > 0.05:
        return "具有较高的增长潜力。虽然当前粉丝基数不大，但高播放量和互动率表明内容很受欢迎。继续保持高质量内容，有望实现快速增长。"
    elif 10000 <= follower_count < 100000 and avg_views > follower_count * 0.3 and interaction_rate > 0.03:
        return "增长潜力良好。已经建立了稳定的粉丝基础，内容表现也不错。建议着重提高内容的传播性，以吸引更多新粉丝。"
    elif follower_count >= 100000 and avg_views > follower_count * 0.2 and interaction_rate > 0.02:
        return "仍有一定的增长空间。作为较大规模的账号，保持现有粉丝的活跃度很重要。可以考虑开展更多互动活动，同时尝试拓展新的内容领域。"
    else:
        return "增长潜力有限。建议重点关注提高内容质量和粉丝互动，可能需要调整内容策略或尝试新的营销方式来刺激增长。"

#商业价值分析
def generate_comprehensive_conclusion(data):
    follower_count = data['粉丝数量']
    transaction_amount = data['商品交易总额']
    avg_views = data['平均播放数']
    interaction_rate = format_interaction_rate(data.get('互动率', 0))

    strength = []
    weakness = []

    if follower_count > 100000:
        strength.append("拥有大量粉丝基础")
    else:
        weakness.append("粉丝基数还有提升空间")

    if transaction_amount > 1000000:
        strength.append("商业转化能力强")
    else:
        weakness.append("商业变现能力有待提高")

    if avg_views > follower_count * 0.5:
        strength.append("内容传播效果好")
    else:
        weakness.append("内容传播效果有待改善")

    if interaction_rate > 0.05:
        strength.append("粉丝互动活跃")
    else:
        weakness.append("粉丝互动度需要提升")

    conclusion = "综合评估：\n"
    conclusion += "优势：" + "，".join(strength) + "。\n" if strength else "暂无明显优势。\n"
    conclusion += "劣势：" + "，".join(weakness) + "。\n" if weakness else "暂无明显劣势。\n"

    if len(strength) > len(weakness):
        conclusion += "总体来看，该达人表现良好，具有较强的商业价值。建议维持现有策略，并着重发挥其优势。"
    elif len(strength) < len(weakness):
        conclusion += "该达人仍有较大的提升空间。建议重点改进劣势项，同时充分利用现有优势来促进整体发展。"
    else:
        conclusion += "该达人表现中等，有优有劣。建议制定平衡的发展策略，同时提升优势项和改进劣势项。"

    return conclusion

#综合暂未启用
def evaluate_performance(amount, count):
    if amount > 50000 and count > 10000:
        return "优秀"
    elif amount > 10000 and count > 1000:
        return "良好"
    elif amount > 1000 and count > 100:
        return "一般"
    else:
        return "需改进"

# 评估合作潜力函数，粉丝数量
def evaluate_cooperation_potential(data):
    score = 0
    reasons = []

    # 评估粉丝数量
    followers = data['粉丝数量']
    if followers > 1000000:
        score += 30
        reasons.append("大量粉丝基础，有广泛的影响力")
    elif followers > 100000:
        score += 20
        reasons.append("较多粉丝，有一定影响力")
    elif followers > 10000:
        score += 10
        reasons.append("粉丝数量适中，有发展潜力")

    # 评估商业转化能力
    transaction_amount = data['商品交易总额']
    transaction_count = data['成交件数']
    performance = evaluate_performance(transaction_amount, transaction_count)
    if performance == "优秀":
        score += 30
        reasons.append("商业转化能力强，有很高的合作价值")
    elif performance == "良好":
        score += 20
        reasons.append("商业转化能力不错，有合作价值")
    elif performance == "一般":
        score += 10
        reasons.append("商业转化能力一般，需要进一步观察")

    # 评估内容质量和互动性
    avg_views = data['平均播放数']
    interaction_rate = format_interaction_rate(data.get('互动率', 0))
    if avg_views > 100000 and interaction_rate > 0.05:
        score += 25
        reasons.append("内容质量高，粉丝互动活跃")
    elif avg_views > 50000 and interaction_rate > 0.03:
        score += 15
        reasons.append("内容质量和粉丝互动性良好")
    elif avg_views > 10000 and interaction_rate > 0.02:
        score += 5
        reasons.append("内容和互动有一定基础，但仍有提升空间")

    # 评估粉丝质量
    if '粉丝质量' in data:
        fan_quality = data['粉丝质量']
        if fan_quality > 8:
            score += 15
            reasons.append("粉丝质量高，有利于精准营销")
        elif fan_quality > 6:
            score += 10
            reasons.append("粉丝质量良好")
        elif fan_quality > 4:
            score += 5
            reasons.append("粉丝质量一般")

    # 根据得分给出建议
    if score >= 80:
        recommendation = "强烈推荐合作"
    elif score >= 60:
        recommendation = "建议合作"
    elif score >= 40:
        recommendation = "可以考虑合作"
    else:
        recommendation = "暂不建议合作"

    return recommendation, score, reasons


def analyze_fan_purchasing_power(data):
    fans_count = data['粉丝数量']
    transaction_amount = data['商品交易总额']
    transaction_count = data['成交件数']

    # 计算平均客单价
    average_order_value = transaction_amount / transaction_count if transaction_count > 0 else 0

    # 计算粉丝转化率
    conversion_rate = transaction_count / fans_count if fans_count > 0 else 0

    # 计算粉丝人均消费
    average_fan_spend = transaction_amount / fans_count if fans_count > 0 else 0

    analysis = f"""
    粉丝消费能力分析：

    1. 平均客单价：¥{average_order_value:.2f}
       这表明每次成交的平均金额。{'较高的客单价表明粉丝有较强的消费能力。' if average_order_value > 15 else '客单价较低，可能需要提高产品价值或改善营销策略。'}

    2. 粉丝转化率：{conversion_rate:.2%}
       这表示粉丝中有多少转化为实际购买。{'转化率较高，说明粉丝对达人推荐的商品有较高的购买意愿。' if conversion_rate > 0.01 else '转化率较低，可能需要提高内容的说服力或优化产品选择。'}

    3. 粉丝人均消费：¥{average_fan_spend:.2f}
       这反映了平均每个粉丝的消费水平。{'粉丝人均消费较高，表明整体消费能力强。' if average_fan_spend > 10 else '粉丝人均消费较低，可能需要更好地激活粉丝的消费意愿。'}

    综合评估：
    {'粉丝整体消费能力较强，有良好的商业价值。' if average_order_value > 15 and conversion_rate > 0.01 and average_fan_spend > 5 else '粉丝消费能力一般，仍有提升空间。建议优化内容策略和产品选择，提高粉丝的购买意愿和客单价。'}
    """

    return analysis
# 主程序
df = load_data()

if df is not None:
    # 创建侧边栏用于搜索和筛选
    st.sidebar.header("搜索和筛选选项")
    search_term = st.sidebar.text_input("输入达人ID或昵称")

    # 达人类型筛选
    daren_types = ['全部'] + list(df['达人类型'].unique())
    selected_type = st.sidebar.selectbox("选择达人类型", daren_types)

    if st.sidebar.button("搜索"):
        if search_term:
            # 使用索引和昵称进行搜索
            result = df[(df.index == search_term) | (df['达人名称'] == search_term)]

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

                # 创建三列布局
                col1, col2, col3 , col4 = st.columns([1, 1, 1, 1])

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
                with col2:
                        # 显示合作建议
                        recommendation, score, reasons = evaluate_cooperation_potential(daren_data)
                        st.subheader("合作建议")
                        st.write(f"建议: {recommendation}")
                        st.write(f"评分: {score}")
                        st.write("理由:")
                        for reason in reasons:
                            st.write(f"- {reason}")
                with col3:
                    # 添加粉丝消费能力分析
                    st.subheader("粉丝消费能力分析")
                    fan_purchasing_power_analysis = analyze_fan_purchasing_power(daren_data)
                    st.markdown(fan_purchasing_power_analysis)
                with col4:
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

                    # 在显示详细信息的部分添加粉丝消费能力分析

            else:
                st.warning(f"未找到匹配 ID 或昵称 '{search_term}' 的记录")
        else:
            st.warning("请输入达人ID或昵称")

else:
    st.error("无法加载数据，请检查Excel文件路径是否正确。")
