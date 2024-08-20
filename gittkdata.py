import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import io
import requests
import matplotlib as mpl

# 设置页面配置
st.set_page_config(page_title="达人数据查询系统", layout="wide")

# 设置字体为 SimHei (SimHei 是一个常见的中文字体)
mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False  # 解决负号 '-' 显示为方块的问题

# 标题
st.title("达人数据查询系统")

# GitHub中Excel文件的URL
EXCEL_FILE_URL = "https://github.com/2686917784/yinhutkdata/raw/main/Aeg001.xlsx"

# 读取Excel文件
@st.cache_data
def load_data():
    try:
        response = requests.get(EXCEL_FILE_URL)
        response.raise_for_status()
        df = pd.read_excel(io.BytesIO(response.content))
        df['达人id'] = df['达人id'].astype(str)
        return df
    except Exception as e:
        st.error(f"加载Excel文件时出错：{e}")
        return None

df = load_data()

if df is not None:
    # 创建侧边栏用于搜索
    st.sidebar.header("搜索选项")
    search_option = st.sidebar.radio("选择搜索方式：", ["按达人ID搜索", "按达人名称搜索"])

    if search_option == "按达人ID搜索":
        search_term = st.sidebar.text_input("输入达人ID")
        search_column = '达人id'
    else:
        search_term = st.sidebar.text_input("输入达人名称")
        search_column = '达人名称'

    if st.sidebar.button("搜索"):
        if search_term:
            result = df[df[search_column].str.contains(search_term, case=False, na=False)]
            if not result.empty:
                st.success(f"找到 {len(result)} 条匹配的记录")

                # 增加搜索结果表格的尺寸和字体
                st.subheader("搜索结果")
                st.markdown(
                    """
                    <style>
                    .dataframe { font-size: 14px !important; }
                    table { font-size: 14px !important; }
                    th, td { padding: 8px; }
                    </style>
                    """,
                    unsafe_allow_html=True
                )
                st.dataframe(result[['达人id', '达人名称', '粉丝数量', '商品交易总额', '成交件数', '平均播放数', '互动率', '评分']], height=8)

                # 让用户选择一个达人进行详细分析
                selected_name = st.selectbox("选择一个达人进行详细分析：", result['达人名称'].tolist())

                if selected_name:
                    daren_data = df[df['达人名称'] == selected_name].iloc[0]

                    # 创建两列布局
                    col1, col2 = st.columns([1, 1])

                    with col1:
                        # 绘制雷达图
                        labels = ['粉丝数量_quantile', '商品交易总额_quantile', '成交件数_quantile', '平均播放数_quantile', '互动率_quantile', '评分']
                        values = daren_data[labels].tolist()
                        values += values[:1]
                        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
                        angles += angles[:1]

                        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
                        ax.fill(angles, values, color='#1f77b4', alpha=0.25)
                        ax.plot(angles, values, color='#1f77b4', linewidth=3, marker='o', markersize=6, markerfacecolor='#ff7f0e')

                        for angle, value in zip(angles, values[:-1]):
                            ax.text(angle, value + 5, f'{int(value)}', color='#ff7f0e', fontsize=12, ha='center', va='center')

                        ax.set_yticklabels([])
                        ax.set_xticks(angles[:-1])
                        ax.set_xticklabels(labels, fontsize=12, color='#444444')
                        ax.spines['polar'].set_visible(False)
                        ax.grid(color='#888888', linestyle='--', linewidth=0.5)
                        ax.set_theta_offset(np.pi / 2)
                        ax.set_theta_direction(-1)
                        ax.set_rlim(0, 100)

                        plt.title(f"达人: {selected_name} 的雷达图", size=16, color='#333333', y=1.1)
                        st.pyplot(fig)

                    with col2:
                        # 显示详细信息
                        st.subheader("达人详细信息")
                        info = {
                            "达人ID": daren_data['达人id'],
                            "达人名称": daren_data['达人名称'],
                            "粉丝数量": f"{daren_data['粉丝数量']:,}",
                            "商品交易总额": f"¥{daren_data['商品交易总额']:,.2f}",
                            "成交件数": f"{daren_data['成交件数']:,}",
                            "平均播放数": f"{daren_data['平均播放数']:,}",
                            "互动率": f"{daren_data['互动率']:.2%}",
                            "评分": f"{daren_data['评分']:.2f}"
                        }
                        for key, value in info.items():
                            st.markdown(f"<span style='font-size: 18px;'><b>{key}:</b> {value}</span>", unsafe_allow_html=True)

                        # 绘制条形图比较各维度得分
                        st.subheader("各维度得分比较")
                        comparison_data = daren_data[labels]
                        fig, ax = plt.subplots(figsize=(10, 5))

                        sns.set_palette("Blues_r")
                        sns.barplot(x=comparison_data.index, y=comparison_data.values, ax=ax)

                        ax.set_xticklabels(
                            [label for label in comparison_data.index],
                            rotation=45,
                            ha='right',
                            fontsize=14
                        )

                        ax.set_ylim(0, 100)

                        for i, v in enumerate(comparison_data.values):
                            ax.text(i, v + 3, f'{int(v)}', ha='center', va='bottom', fontsize=14)

                        ax.set_ylabel("得分", fontsize=16)
                        ax.set_xlabel("")
                        ax.set_title("各维度得分比较", fontsize=18, color='#333333')

                        plt.tight_layout()
                        st.pyplot(fig)

            else:
                st.warning(f"未找到匹配 '{search_term}' 的记录")
        else:
            st.warning("请输入搜索内容")

else:
    st.error("无法加载数据，请检查Excel文件路径是否正确。")
