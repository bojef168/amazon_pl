"""
洞察生成工具
功能：根据分析结果生成洞察文本和优先级评估
"""
from typing import Dict, List, Union, Tuple
from collections import defaultdict

class InsightGenerator:
    def __init__(self):
        """初始化洞察生成器"""
        # 定义维度权重
        self.dimension_weights = {
            'user_type': 1.0,      # 用户类型
            'usage_pattern': 0.9,   # 使用模式
            'pain_point': 1.0,     # 痛点
            'satisfaction': 0.8,    # 满意度
            'feature_request': 0.9, # 功能需求
            'scenario': 0.7,       # 使用场景
            'motivation': 0.8      # 购买动机
        }

        # 定义优先级阈值
        self.priority_thresholds = {
            'high': 0.8,
            'medium': 0.5,
            'low': 0.3
        }

    def generate_comprehensive_insights(
            self,
            analysis_results: Dict,
            min_support: float = 0.1
        ) -> List[Dict]:
        """
        生成综合洞察

        参数:
            analysis_results: 所有分析器的结果
            min_support: 最小支持度阈值
        返回:
            List[Dict]: 包含优先级的洞察列表
        """
        insights = []

        # 处理每个维度的分析结果
        for dimension, results in analysis_results.items():
            # 生成频率洞察
            if 'percentage' in results:
                freq_insight = self.generate_frequency_insight(
                    dimension,
                    results['count'],
                    results['total']
                )
                insights.append({
                    'dimension': dimension,
                    'type': 'frequency',
                    'insight': freq_insight,
                    'priority': self._calculate_priority(dimension, results)
                })

            # 生成情感洞察
            if 'sentiment' in results:
                sentiment_insight = self.generate_sentiment_insight(
                    dimension,
                    results['sentiment']
                )
                insights.append({
                    'dimension': dimension,
                    'type': 'sentiment',
                    'insight': sentiment_insight,
                    'priority': self._calculate_priority(dimension, results)
                })

            # 生成趋势洞察
            if 'trend' in results:
                trend_insight = self.generate_trend_insight(
                    dimension,
                    results['trend']
                )
                insights.append({
                    'dimension': dimension,
                    'type': 'trend',
                    'insight': trend_insight,
                    'priority': self._calculate_priority(dimension, results)
                })

        # 生成维度间的关联洞察
        correlation_insights = self.generate_correlation_insights(analysis_results)
        insights.extend(correlation_insights)

        # 按优先级排序
        insights.sort(key=lambda x: x['priority'], reverse=True)

        return insights

    def generate_sentiment_insight(self, dimension: str, sentiment_data: Dict) -> str:
        """
        生成情感洞察

        参数:
            dimension: 维度名称
            sentiment_data: 情感分析数据
        返回:
            str: 情感洞察描述
        """
        mean = sentiment_data.get('mean', 0)
        positive = sentiment_data.get('positive', 0)
        negative = sentiment_data.get('negative', 0)
        total = positive + negative + sentiment_data.get('neutral', 0)

        if total == 0:
            return f"No sentiment data available for {dimension}"

        pos_ratio = (positive / total) * 100 if total > 0 else 0
        neg_ratio = (negative / total) * 100 if total > 0 else 0

        if mean > 0.5:
            return f"{dimension} receives highly positive feedback ({pos_ratio:.1f}% positive)"
        elif mean > 0:
            return f"{dimension} receives moderately positive feedback ({pos_ratio:.1f}% positive)"
        elif mean < -0.5:
            return f"{dimension} receives significant negative feedback ({neg_ratio:.1f}% negative)"
        elif mean < 0:
            return f"{dimension} receives some negative feedback ({neg_ratio:.1f}% negative)"
        else:
            return f"{dimension} receives mixed feedback"

    def generate_frequency_insight(self, dimension: str, count: int, total: int) -> str:
        """
        生成频率洞察

        参数:
            dimension: 维度名称
            count: 出现次数
            total: 总样本数
        返回:
            str: 频率洞察描述
        """
        percentage = (count / total) * 100 if total > 0 else 0
        if percentage > 50:
            return f"{dimension} is highly prevalent, appearing in {percentage:.1f}% of cases"
        elif percentage > 25:
            return f"{dimension} shows moderate presence, mentioned in {percentage:.1f}% of cases"
        else:
            return f"{dimension} has limited presence, only in {percentage:.1f}% of cases"

    # 修改 generate_comprehensive_insights 方法中的数据处理
    def generate_comprehensive_insights(self, analysis_results: Dict, min_support: float = 0.1) -> List[Dict]:
        """
        生成综合洞察

        参数:
            analysis_results: 所有分析器的结果
            min_support: 最小支持度阈值
        返回:
            List[Dict]: 包含优先级的洞察列表
        """
        insights = []

        # 处理每个维度的分析结果
        for dimension, results in analysis_results.items():
            if dimension == 'metadata':
                continue

            # 处理类别数据
            for category, category_data in results.items():
                if isinstance(category_data, dict):
                    # 生成频率洞察
                    if 'mention_count' in category_data and 'total_mentions' in category_data:
                        freq_insight = self.generate_frequency_insight(
                            f"{dimension}_{category}",
                            category_data['mention_count'],
                            category_data['total_mentions']
                        )
                        insights.append({
                            'dimension': dimension,
                            'category': category,
                            'type': 'frequency',
                            'insight': freq_insight,
                            'priority': self._calculate_priority(dimension, category_data)
                        })

                    # 生成情感洞察
                    if 'sentiment' in category_data:
                        sentiment_insight = self.generate_sentiment_insight(
                            f"{dimension}_{category}",
                            category_data['sentiment']
                        )
                        insights.append({
                            'dimension': dimension,
                            'category': category,
                            'type': 'sentiment',
                            'insight': sentiment_insight,
                            'priority': self._calculate_priority(dimension, category_data)
                        })

                    # 生成趋势洞察
                    if 'trend' in category_data:
                        trend_insight = self.generate_trend_insight(
                            f"{dimension}_{category}",
                            category_data['trend']
                        )
                        insights.append({
                            'dimension': dimension,
                            'category': category,
                            'type': 'trend',
                            'insight': trend_insight,
                            'priority': self._calculate_priority(dimension, category_data)
                        })

        # 生成维度间的关联洞察
        correlation_insights = self.generate_correlation_insights(analysis_results)
        insights.extend(correlation_insights)

        # 按优先级排序
        insights.sort(key=lambda x: x['priority'], reverse=True)

        return insights

    def generate_trend_insight(
            self,
            category: str,
            trend_data: Dict[str, float]
        ) -> str:
        """
        生成趋势洞察

        参数:
            category: 类别名称
            trend_data: 趋势数据
        返回:
            str: 趋势洞察描述
        """
        trend_value = trend_data.get('slope', 0)

        if abs(trend_value) < 0.1:
            return f"{category} shows stable patterns over time"
        elif trend_value > 0:
            return f"{category} shows an increasing trend, growing by {trend_value:.1f}% per period"
        else:
            return f"{category} shows a decreasing trend, declining by {abs(trend_value):.1f}% per period"

    def generate_correlation_insights(
            self,
            analysis_results: Dict
        ) -> List[Dict]:
        """
        生成维度间的关联洞察

        参数:
            analysis_results: 所有分析器的结果
        返回:
            List[Dict]: 关联洞察列表
        """
        correlation_insights = []
        dimensions = list(analysis_results.keys())

        for i in range(len(dimensions)):
            for j in range(i + 1, len(dimensions)):
                dim1, dim2 = dimensions[i], dimensions[j]

                # 计算两个维度间的关联强度
                correlation = self._calculate_correlation(
                    analysis_results[dim1],
                    analysis_results[dim2]
                )

                if abs(correlation) > 0.5:  # 只关注强相关
                    insight = {
                        'dimension': f"{dim1}_{dim2}",
                        'type': 'correlation',
                        'insight': self._format_correlation_insight(dim1, dim2, correlation),
                        'priority': abs(correlation) * 0.8  # 关联洞察的优先级
                    }
                    correlation_insights.append(insight)

        return correlation_insights

    def _calculate_correlation(
            self,
            data1: Dict,
            data2: Dict
        ) -> float:
        """
        计算两个维度间的关联强度

        参数:
            data1: 第一个维度的数据
            data2: 第二个维度的数据
        返回:
            float: 关联强度 (-1到1)
        """
        # 这里可以实现更复杂的关联计算
        # 当前使用简化版本
        if 'percentage' in data1 and 'percentage' in data2:
            return (data1['percentage'] * data2['percentage']) / 10000
        return 0.0

    def _format_correlation_insight(
            self,
            dim1: str,
            dim2: str,
            correlation: float
        ) -> str:
        """
        格式化关联洞察文本

        参数:
            dim1: 第一个维度
            dim2: 第二个维度
            correlation: 关联强度
        返回:
            str: 格式化的洞察文本
        """
        if correlation > 0.7:
            return f"Strong positive correlation between {dim1} and {dim2}"
        elif correlation > 0.5:
            return f"Moderate positive correlation between {dim1} and {dim2}"
        elif correlation < -0.7:
            return f"Strong negative correlation between {dim1} and {dim2}"
        elif correlation < -0.5:
            return f"Moderate negative correlation between {dim1} and {dim2}"
        else:
            return f"Weak correlation between {dim1} and {dim2}"

    def _calculate_priority(
            self,
            dimension: str,
            results: Dict
        ) -> float:
        """
        计算洞察的优先级

        参数:
            dimension: 维度名称
            results: 分析结果
        返回:
            float: 优先级分数 (0-1)
        """
        base_weight = self.dimension_weights.get(dimension.split('_')[0], 0.5)

        # 考虑多个因素
        factors = {
            'percentage': results.get('percentage', 0) / 100,
            'sentiment': abs(results.get('sentiment_score', 0)),
            'trend': abs(results.get('trend', {}).get('slope', 0)) / 100
        }

        # 计算综合分数
        score = base_weight * sum(factors.values()) / len(factors)

        return min(max(score, 0), 1)  # 确保分数在0-1之间

"""
多维度洞察生成：
频率洞察
情感洞察
趋势洞察
关联洞察
优先级评估系统：
维度权重
多因素考虑
优先级阈值
关联分析功能：
维度间关联强度计算
关联洞察生成
关联优先级评估
"""