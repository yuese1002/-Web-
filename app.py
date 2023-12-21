# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import jieba
import re
from collections import Counter
from pyecharts import options as opts
from pyecharts.charts import Pie, Bar, Line, WordCloud, Scatter
from pyecharts.globals import ThemeType
import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import font_manager
def scrape_website(url):
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.content, 'html.parser')
    text = soup.get_text()
    filter_words = ['\n', ' ', '，', '。', '！', '？', '的', '是', '在', '了', '和', '同', '为', '也', '这', '有',
                    '就', '又', '或', '但', '如果', '由于', '因此', '所以', '之', '与',
                    '及', '或者', '一些', '一样', '例如', '这些', '那些', '不', '也不',
                    '之一', '之二', '之三', '之四', '之五', '之六', '之七', '之八', '之九', '之十',
                    '……', '。', '，', '、', '：', '；', '！', '？', '“', '”',
                    '（', '）', '【', '】', '《', '》', '［', '］', '｛', '｝'
                    ,'我', '他', '她', '你']
    for word in filter_words:
        text = text.replace(word, '')
    clean_text = re.sub('<.*?>', '', text)
    clean_text = re.sub('[^\w\s]', '', clean_text)
    clean_text = re.sub('\s+', '', clean_text)
    words = jieba.cut(clean_text)

    word_count = Counter(words)

    top_10_words = dict(word_count.most_common(20))

    x = list(top_10_words.keys())
    y = list(top_10_words.values())

    return x, y


def generate_word_frequency(x, y):
    pie = (
        Pie(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        .add("", [list(z) for z in zip(x, y)])
        .set_global_opts(title_opts=opts.TitleOpts(title="饼状图"),
                         legend_opts=opts.LegendOpts(orient="vertical", pos_top="15%", pos_left="-1%"))
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    )


    bar = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        .add_xaxis(x)
        .add_yaxis("word Count", y)
        .set_global_opts(title_opts=opts.TitleOpts(title="柱状图 "),
                         xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),
                         legend_opts=opts.LegendOpts(is_show=False))
    )

    line = (
        Line(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        .add_xaxis(x)
        .add_yaxis("word Count", y)
        .set_global_opts(title_opts=opts.TitleOpts(title=" 折线图"),
                         xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),
                         legend_opts=opts.LegendOpts(is_show=False))
    )


    word_cloud = (
        WordCloud(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        .add("", [list(z) for z in zip(x, y)], word_size_range=[20, 100])
        .set_global_opts(title_opts=opts.TitleOpts(title="词云图"))
    )


    scatter = (
        Scatter(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        .add_xaxis(x)
        .add_yaxis("word Count", y)
        .set_global_opts(title_opts=opts.TitleOpts(title="散点图"),
                         xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),
                         legend_opts=opts.LegendOpts(is_show=False))
    )

    return pie.render_embed(), bar.render_embed(), line.render_embed(), word_cloud.render_embed(), scatter.render_embed()


def Seaborn(x, y, chart_type):
    data = np.column_stack((x, y))
    df = pd.DataFrame(data, columns=["x", "y"])
    if chart_type == "直方图":
        plt.hist(y)
        plt.xlabel("Value")
        plt.ylabel("Frequency")
        plt.title("Histogram")
        st.pyplot(plt.gcf())  # 使用plt.gcf()获取当前图形对象并传递给st.pyplot()

    elif chart_type == "回归图":
        x= np.array(y).astype(float)
        y = np.array(y).astype(float)
        fig, ax = plt.subplots()
        sns.regplot(x=np.arange(len(x)), y=y, ax=ax)
        ax.set_xticks(np.arange(len(x)))
        ax.set_xticklabels(x, rotation=45)
        st.pyplot(fig)# 直接将已创建的fig传递给st.pyplot()

    elif chart_type == "成对关系图":
        g = sns.pairplot(df, vars=["x", "y"], height=6, aspect=1.2)
        g.fig.subplots_adjust(top=0.9, wspace=0.3)
        st.pyplot(g.fig)  # 使用g.fig获取图形对象并传递给st.pyplot()


def main():
    st.title("文本分析")
    url = st.sidebar.text_input("请输入要爬取的网址")
    plotting_function = st.sidebar.selectbox("选择绘制图表的函数", ["Pyecharts", "Seaborn"])
    if plotting_function == "Pyecharts":
        chart_type = st.sidebar.selectbox("请选择要显示的图表类型",["饼状图", "柱状图", "折线图", "词云图", "散点图"])
        if st.sidebar.button("生成图") or url:
            if url:
                x, y = scrape_website(url)
                pie_html, bar_html, line_html, word_cloud_html, scatter_html, = generate_word_frequency(x, y)
                if chart_type == "饼状图":
                    chart_html = pie_html
                elif chart_type == "柱状图":
                    chart_html = bar_html
                elif chart_type == "折线图":
                    chart_html = line_html
                elif chart_type == "词云图":
                    chart_html = word_cloud_html
                else:
                    chart_html = scatter_html

                chart_component = components.html(chart_html, height=500, width=1000)
    elif plotting_function == "Seaborn":
        chart_type = st.sidebar.selectbox("请选择要显示的图表类型", ["直方图", "回归图", "成对关系图"])
        if st.sidebar.button("生成图") or url:
            if url:
                x, y = scrape_website(url)
                Seaborn(x, y, chart_type)

if __name__ == "__main__":
    main()