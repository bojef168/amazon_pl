"""
使用目的分析器
功能：分析用户使用产品的主要目的和意图
"""
from typing import Dict, Set
import spacy
from collections import defaultdict
from .base_analyzer import BaseAnalyzer, ProcessingError

class PurposeAnalyzer(BaseAnalyzer):
    def __init__(self):
        """初始化使用目的分析器"""
        super().__init__()

        # 初始化目的相关的动词和名词模式
        self.purpose_patterns = {
            'maintenance': {
                'verbs': {'maintain', 'keep', 'preserve', 'protect', 'ensure'},
                'nouns': {'maintenance', 'upkeep', 'care', 'condition'}
            },
            'improvement': {
                'verbs': {'improve', 'enhance', 'upgrade', 'optimize', 'boost'},
                'nouns': {'improvement', 'enhancement', 'performance', 'efficiency'}
            },
            'problem_solving': {
                'verbs': {'solve', 'fix', 'resolve', 'address', 'handle'},
                'nouns': {'problem', 'issue', 'challenge', 'difficulty', 'concern'}
            },
            'convenience': {
                'verbs': {'save', 'simplify', 'facilitate', 'help', 'assist'},
                'nouns': {'time', 'effort', 'convenience', 'ease', 'simplicity'}
            }
        }

    def _extract_categories(self, df) -> Dict[str, Set[str]]:
        """
        从评论中提取使用目的相关的类别和关键词

        参数:
            df: 评论数据DataFrame
        返回:
            Dict[str, Set[str]]: {目的类别: {相关关键词集合}}
        """
        try:
            purpose_keywords = defaultdict(set)

            # 分析每条评论
            for _, row in df.iterrows():
                try:
                    text = f"{row['标题']} {row['内容']}"
                    doc = self.nlp(text.lower())

                    # 提取动词-名词短语
                    for token in doc:
                        try:
                            # 检查动词
                            if token.pos_ == 'VERB':
                                verb = token.lemma_
                                # 检查这个动词属于哪个目的类别
                                for purpose, patterns in self.purpose_patterns.items():
                                    if verb in patterns['verbs']:
                                        # 查找与该动词相关的名词
                                        for child in token.children:
                                            if child.pos_ == 'NOUN':
                                                phrase = f"{verb} {child.text}"
                                                purpose_keywords[purpose].add(phrase)

                            # 检查名词
                            elif token.pos_ == 'NOUN':
                                noun = token.lemma_
                                # 检查这个名词属于哪个目的类别
                                for purpose, patterns in self.purpose_patterns.items():
                                    if noun in patterns['nouns']:
                                        # 添加相关的形容词修饰语
                                        for child in token.children:
                                            if child.pos_ == 'ADJ':
                                                phrase = f"{child.text} {noun}"
                                                purpose_keywords[purpose].add(phrase)

                        except Exception as e:
                            self.logger.warning(f"Error processing token: {str(e)}")
                            continue

                except Exception as e:
                    self.logger.warning(f"Error processing row: {str(e)}")
                    continue

            # 过滤掉提及次数过少的类别
            min_mentions = 3
            filtered_purposes = {
                purpose: keywords
                for purpose, keywords in purpose_keywords.items()
                if len(keywords) >= min_mentions
            }

            return filtered_purposes

        except Exception as e:
            self.logger.error(f"Category extraction failed: {str(e)}")
            raise ProcessingError(f"Failed to extract purpose categories: {str(e)}")

    def _generate_purpose_specific_insights(self, results: Dict) -> Dict:
        """
        生成使用目的专属的洞察

        参数:
            results: 基础分析结果
        返回:
            Dict: 添加了专属洞察的结果
        """
        for purpose, data in results.items():
            # 确保 data 是字典类型
            if isinstance(data, dict):
                specific_insights = []

                # 基于使用目的的特定洞察
                if data.get('percentage', 0) > 40:
                    specific_insights.append(
                        f"{purpose} is a primary motivation for users, "
                        "indicating strong alignment with core user needs"
                    )

                # 基于情感的特定洞察
                if 'sentiment' in data and 'mention_count' in data and data['mention_count'] > 0:
                    pos_rate = (data['sentiment'].get('positive', 0) /
                                data['mention_count']) * 100
                    if pos_rate > 70:
                        specific_insights.append(
                            f"Users are highly satisfied with the product's ability to "
                            f"meet their {purpose} needs"
                        )
                    elif pos_rate < 30:
                        specific_insights.append(
                            f"There may be opportunities to better address user "
                            f"needs related to {purpose}"
                        )

                # 添加专属洞察
                if specific_insights:
                    data['insights'] = data.get('insights', []) + specific_insights

        return results

    def _generate_insights(self, trend_results: Dict) -> Dict:
        """生成目的相关的分析洞察"""
        base_insights = super()._generate_insights(trend_results)

        # 添加目的特定的分析
        purpose_insights = {
            'usage_purposes': getattr(self, 'purpose_distribution', {}),
            'purpose_satisfaction': getattr(self, 'purpose_satisfaction', {}),
            'common_scenarios': getattr(self, 'common_scenarios', [])
        }

        base_insights.update(purpose_insights)
        return base_insights

    def analyze(self, df) -> Dict:
        """
        分析使用目的

        参数:
            df: 评论数据DataFrame
        返回:
            Dict: 使用目的分析结果
        """
        # 使用基础分析流程
        results = super().analyze(df)

        # 添加使用目的专属的洞察
        results = self._generate_purpose_specific_insights(results)

        return results

"""
这个使用目的分析器的主要特点：
使用 spaCy 进行自然语言处理，提取动词-名词短语
定义了常见的使用目的类别（维护、改进、问题解决、便利性）
通过分析动词和名词的搭配来识别使用目的
生成针对使用目的的专属洞察
"""