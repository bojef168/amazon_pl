"""
使用地点分析器
功能：分析用户在什么地点使用产品，包括具体空间、场景和环境特征
"""
from typing import Dict, Set
import spacy
from collections import defaultdict
from .base_analyzer import BaseAnalyzer


class LocationAnalyzer(BaseAnalyzer):
    def __init__(self):
        """初始化使用地点分析器"""
        super().__init__()
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except OSError:
            import os
            os.system('python -m spacy download en_core_web_sm')
            self.nlp = spacy.load('en_core_web_sm')

        # 初始化地点相关的模式
        self.location_patterns = {
            'indoor_spaces': {
                'living_areas': {
                    'living room', 'bedroom', 'dining room', 'kitchen',
                    'bathroom', 'hallway', 'corridor', 'study', 'office room'
                },
                'storage_areas': {
                    'closet', 'storage room', 'garage', 'basement',
                    'attic', 'cabinet', 'drawer'
                },
                'functional_areas': {
                    'laundry room', 'utility room', 'workshop',
                    'gym', 'entertainment room'
                }
            },
            'outdoor_spaces': {
                'immediate_outdoor': {
                    'balcony', 'patio', 'deck', 'porch', 'terrace',
                    'garden', 'yard', 'driveway'
                },
                'extended_outdoor': {
                    'pool', 'outdoor kitchen', 'playground',
                    'garage exterior', 'walkway'
                }
            },
            'environment_types': {
                'residential': {
                    'house', 'apartment', 'condo', 'flat', 'studio',
                    'home', 'residence', 'living space'
                },
                'commercial': {
                    'office', 'shop', 'store', 'business',
                    'workplace', 'commercial space'
                }
            }
        }

    def _extract_categories(self, df) -> Dict[str, Set[str]]:
        """
        从评论中提取地点相关的类别和关键词

        参数:
            df: 评论数据DataFrame
        返回:
            Dict[str, Set[str]]: {地点类别: {相关关键词集合}}
        """
        location_keywords = defaultdict(set)

        # 分析每条评论
        for _, row in df.iterrows():
            text = f"{row['标题']} {row['内容']}"
            doc = self.nlp(text.lower())

            # 提取地点相关的短语
            for sent in doc.sents:
                # 使用依存句法分析找到地点相关的短语
                for token in sent:
                    if token.dep_ in {'pobj', 'dobj', 'nsubj'} or token.pos_ == 'NOUN':
                        # 检查是否匹配任何地点模式
                        location_phrase = self._extract_location_phrase(token)
                        if location_phrase:
                            # 确定地点类别
                            category = self._determine_location_category(location_phrase)
                            if category:
                                location_keywords[category].add(location_phrase)

        # 过滤掉提及次数过少的类别
        min_mentions = 2
        filtered_locations = {
            category: keywords
            for category, keywords in location_keywords.items()
            if len(keywords) >= min_mentions
        }

        return filtered_locations

    def _extract_location_phrase(self, token) -> str:
        """
        提取地点相关的完整短语

        参数:
            token: spaCy的Token对象
        返回:
            str: 地点短语
        """
        phrase_tokens = []

        # 添加修饰语
        for child in token.children:
            if child.dep_ in {'amod', 'compound'} or child.pos_ == 'ADJ':
                phrase_tokens.append(child.text)

        # 添加核心词
        phrase_tokens.append(token.text)

        # 添加后置修饰语
        for child in token.children:
            if child.dep_ == 'prep':
                prep_phrase = []
                prep_phrase.append(child.text)
                for grandchild in child.children:
                    if grandchild.dep_ == 'pobj':
                        prep_phrase.append(grandchild.text)
                phrase_tokens.extend(prep_phrase)

        return ' '.join(phrase_tokens)

    def _determine_location_category(self, phrase: str) -> str:
        """
        确定地点短语属于哪个类别

        参数:
            phrase: 地点短语
        返回:
            str: 地点类别名称
        """
        for main_category, subcategories in self.location_patterns.items():
            for sub_category, keywords in subcategories.items():
                for keyword in keywords:
                    if keyword in phrase:
                        return f"{main_category}_{sub_category}"
        return None

    def _generate_location_specific_insights(self, results: Dict) -> Dict:
        """
        生成使用地点专属的洞察

        参数:
            results: 基础分析结果
        返回:
            Dict: 添加了专属洞察的结果
        """
        for category, data in results.items():
            # 确保 data 是字典类型
            if isinstance(data, dict):
                specific_insights = []

                # 基于使用地点的特定洞察
                if data.get('percentage', 0) > 30:
                    category_name = category.replace('_', ' ').title()
                    specific_insights.append(
                        f"{category_name} represents a key usage environment, "
                        "suggesting importance of optimizing for this space"
                    )

                # 基于情感分析的特定洞察
                if 'sentiment' in data and 'mention_count' in data and data['mention_count'] > 0:
                    pos_rate = (data['sentiment'].get('positive', 0) /
                                data['mention_count']) * 100
                    if pos_rate > 70:
                        specific_insights.append(
                            f"Users report particularly positive experiences when using "
                            f"the product in {category.replace('_', ' ')} settings"
                        )
                    elif pos_rate < 30:
                        specific_insights.append(
                            f"Users face some challenges when using the product in "
                            f"{category.replace('_', ' ')} environments"
                        )

                # 添加专属洞察
                if specific_insights:
                    data['insights'] = data.get('insights', []) + specific_insights

        return results

    def _generate_insights(self, trend_results: Dict) -> Dict:
        """生成位置相关的分析洞察"""
        base_insights = super()._generate_insights(trend_results)

        # 添加位置特定的分析
        location_insights = {
            'geographic_distribution': getattr(self, 'location_distribution', {}),
            'regional_preferences': getattr(self, 'regional_preferences', {}),
            'location_sentiment': getattr(self, 'location_sentiment', {})
        }

        base_insights.update(location_insights)
        return base_insights

    def analyze(self, df) -> Dict:
        """
        分析使用地点

        参数:
            df: 评论数据DataFrame
        返回:
            Dict: 使用地点分析结果
        """
        # 使用基础分析流程
        results = super().analyze(df)

        # 添加使用地点专属的洞察
        results = self._generate_location_specific_insights(results)

        return results

"""
这个使用地点分析器的主要特点：
分析三个主要维度：
室内空间（生活区、储物区、功能区）
室外空间（直接室外区、扩展室外区）
环境类型（住宅、商业）
使用依存句法分析提取完整的地点短语
考虑地点的层次关系（主类别和子类别）
生成针对不同使用环境的专属洞察
"""
