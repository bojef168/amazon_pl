import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import pandas as pd

# 设置默认渲染器为浏览器
pio.renderers.default = "browser"

# 创建子图布局，指定饼图类型
fig = make_subplots(
    rows=2, cols=2,
    specs=[
        [{"type": "pie"}, {"type": "polar"}],  # 第一行：饼图和极坐标图
        [{"type": "xy"}, {"type": "xy"}]       # 第二行：普通xy图表
    ],
    subplot_titles=("用户体验情感分布", "产品多维度满意度评分",
                   "用户问题类型分布", "用户评分趋势分析")
)

# 1. 情感分布饼图
labels = ['正面评价', '中性评价', '负面评价']
values = [65, 20, 15]
fig.add_trace(
    go.Pie(labels=labels, values=values, hole=.3,
           marker_colors=['#2ecc71', '#95a5a6', '#e74c3c']),
    row=1, col=1
)

# 2. 雷达图数据
categories = ['易用性', '性能', '外观设计',
              '功能完整性', '稳定性', '性价比']
values = [4.5, 4.2, 4.8, 4.0, 4.3, 4.1]
fig.add_trace(
    go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        marker_color='rgb(31, 119, 180)'
    ),
    row=1, col=2
)

# 3. 堆叠柱状图数据
categories = ['界面问题', '性能问题', '功能缺失', '兼容性问题']
urgent = [20, 15, 10, 8]
normal = [30, 25, 20, 15]
low = [15, 10, 12, 8]
fig.add_trace(
    go.Bar(name='紧急', x=categories, y=urgent, marker_color='#e74c3c'),
    row=2, col=1
)
fig.add_trace(
    go.Bar(name='普通', x=categories, y=normal, marker_color='#f39c12'),
    row=2, col=1
)
fig.add_trace(
    go.Bar(name='低优先级', x=categories, y=low, marker_color='#3498db'),
    row=2, col=1
)

# 4. 趋势折线图数据
months = ['1月', '2月', '3月', '4月', '5月', '6月']
satisfaction = [4.2, 4.3, 4.4, 4.5, 4.6, 4.7]
engagement = [3.8, 4.0, 4.1, 4.3, 4.4, 4.5]
fig.add_trace(
    go.Scatter(x=months, y=satisfaction, name='满意度',
               line=dict(color='#2ecc71', width=4)),
    row=2, col=2
)
fig.add_trace(
    go.Scatter(x=months, y=engagement, name='参与度',
               line=dict(color='#3498db', width=4)),
    row=2, col=2
)

# 更新布局
fig.update_layout(
    title_text="产品分析报告可视化概览",
    height=1000,
    width=1200,
    showlegend=True
)

# 更新极坐标图的范围
fig.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 5]
        )
    )
)

# 更新堆叠柱状图的模式
fig.update_layout(barmode='stack')

# 保存为HTML文件
fig.write_html("product_analysis_report.html")

# 在浏览器中显示
fig.show()