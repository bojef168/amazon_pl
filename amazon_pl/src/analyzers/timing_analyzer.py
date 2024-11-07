"""
使用时刻分析器
功能：分析用户在什么时候使用产品，包括时间点、频率和持续时间
"""
from typing import Dict, Set
import spacy
from collections import defaultdict
from datetime import datetime
from .base_analyzer import BaseAnalyzer, ProcessingError



class TimingAnalyzer(BaseAnalyzer):
    def __init__(self):
        """初始化使用时刻分析器"""
        super().__init__()

        # 初始化时间相关的模式
        self.timing_patterns = {
            'time_of_day': {
                'morning': {'morning', 'dawn', 'breakfast', 'early', 'sunrise', 'am'},
                'afternoon': {'afternoon', 'lunch', 'noon', 'midday', 'pm'},
                'evening': {'evening', 'dinner', 'sunset', 'dusk'},
                'night': {'night', 'midnight', 'late', 'bedtime', 'sleep'}
            },
            'frequency': {
                'daily': {'daily', 'everyday', 'day', 'regular', 'routine'},
                'weekly': {'weekly', 'week', 'weekend', 'weekday'},
                'monthly': {'monthly', 'month', 'occasional'},
                'as_needed': {'needed', 'necessary', 'occasionally', 'sometimes'}
            },
            'duration': {
                'quick': {'quick', 'brief', 'short', 'minute', 'instant'},
                'medium': {'hour', 'while', 'session'},
                'long': {'long', 'extended', 'hours', 'throughout'}
            }
        }

    def _extract_categories(self, df) -> Dict[str, Set[str]]:
        """
        从评论中提取时间相关的类别和关键词

        参数:
            df: 评论数据DataFrame
        返回:
            Dict[str, Set[str]]: {时间类别: {相关关键词集合}}
        """
        try:
            timing_keywords = defaultdict(set)

            # 分析每条评论
            for _, row in df.iterrows():
                try:
                    text = f"{row['标题']} {row['内容']}"
                    doc = self.nlp(text.lower())

                    # 提取时间相关的短语
                    for sent in doc.sents:
                        # 检查每个词是否匹配时间模式
                        for token in sent:
                            try:
                                # 检查时间点
                                for time_category, patterns in self.timing_patterns['time_of_day'].items():
                                    if token.text in patterns:
                                        context = self._extract_context(token)
                                        timing_keywords[f"time_{time_category}"].add(context)

                                # 检查频率
                                for freq_category, patterns in self.timing_patterns['frequency'].items():
                                    if token.text in patterns:
                                        context = self._extract_context(token)
                                        timing_keywords[f"frequency_{freq_category}"].add(context)

                                # 检查持续时间
                                for dur_category, patterns in self.timing_patterns['duration'].items():
                                    if token.text in patterns:
                                        context = self._extract_context(token)
                                        timing_keywords[f"duration_{dur_category}"].add(context)
                            except Exception as e:
                                self.logger.warning(f"Error processing token: {str(e)}")
                                continue

                except Exception as e:
                    self.logger.warning(f"Error processing row: {str(e)}")
                    continue

            # 过滤掉提及次数过少的类别
            min_mentions = 2
            filtered_timing = {
                category: keywords
                for category, keywords in timing_keywords.items()
                if len(keywords) >= min_mentions
            }

            return filtered_timing

        except Exception as e:
            self.logger.error(f"Category extraction failed: {str(e)}")
            raise ProcessingError(f"Failed to extract timing categories: {str(e)}")

    def _extract_context(self, token, window_size=3) -> str:
        """
        提取词语的上下文短语

        参数:
            token: spaCy的Token对象
            window_size: 上下文窗口大小
        返回:
            str: 上下文短语
        """
        start = max(0, token.i - window_size)
        end = min(len(token.doc), token.i + window_size + 1)
        context_tokens = token.doc[start:end]
        return ' '.join([t.text for t in context_tokens])

    def _generate_timing_specific_insights(self, results: Dict) -> Dict:
        """
        生成使用时刻专属的洞察

        参数:
            results: 基础分析结果
        返回:
            Dict: 添加了专属洞察的结果
        """
        # 按类别分组
        time_of_day_results = {k: v for k, v in results.items() if k.startswith('time_')}
        frequency_results = {k: v for k, v in results.items() if k.startswith('frequency_')}
        duration_results = {k: v for k, v in results.items() if k.startswith('duration_')}

        for category, data in results.items():
            # 确保 data 是字典类型
            if isinstance(data, dict):
                specific_insights = []

                # 时间点相关洞察
                if category.startswith('time_'):
                    if data.get('percentage', 0) > 30:
                        specific_insights.append(
                            f"Product usage is particularly high during {category.replace('time_', '')}, "
                            "suggesting strong temporal usage patterns"
                        )

            # 频率相关洞察
            elif category.startswith('frequency_'):
                if data['percentage'] > 40:
                    specific_insights.append(
                        f"Users tend to use the product {category.replace('frequency_', '')}, "
                        "indicating established usage habits"
                    )

            # 持续时间相关洞察
            elif category.startswith('duration_'):
                if data['percentage'] > 30:
                    specific_insights.append(
                        f"Usage sessions are typically {category.replace('duration_', '')}, "
                        "which should inform product optimization"
                    )

                # 添加专属洞察
                if 'insights' not in data:
                    data['insights'] = []
                data['insights'].extend(specific_insights)

        return results

    def _generate_insights(self, trend_results: Dict) -> Dict:
        """生成时间相关的分析洞察"""
        base_insights = super()._generate_insights(trend_results)

        # 添加时间特定的分析
        timing_insights = {
            'timing_patterns': {
                'peak_hours': getattr(self, 'peak_hours', []),
                'low_activity_hours': getattr(self, 'low_activity_hours', []),
                'weekly_pattern': getattr(self, 'weekly_pattern', {})
            },
            'response_times': {
                'average_response': getattr(self, 'avg_response_time', 0),
                'response_distribution': getattr(self, 'response_distribution', {})
            }
        }

        base_insights.update(timing_insights)
        return base_insights

    def analyze(self, df) -> Dict:
        """
        分析使用时刻

        参数:
            df: 评论数据DataFrame
        返回:
            Dict: 使用时刻分析结果
        """
        # 使用基础分析流程
        results = super().analyze(df)

        # 添加使用时刻专属的洞察
        results = self._generate_timing_specific_insights(results)

        return results
"""
这个使用时刻分析器的主要特点：
分析三个维度：
使用时间点（早晨、下午、晚上、夜间）
使用频率（每天、每周、每月、按需）
使用时长（短暂、中等、长时间）
使用上下文窗口提取时间相关的短语，而不是单个词
生成针对时间模式的专属洞察
"""