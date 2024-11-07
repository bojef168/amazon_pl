"""
购买动机分析器
功能：分析用户购买产品的原因、决策因素和期望
"""
from typing import Dict, Set, List, Tuple
import spacy
from collections import defaultdict
from .base_analyzer import BaseAnalyzer


class MotivationAnalyzer(BaseAnalyzer):
    def __init__(self):
        """初始化购买动机分析器"""
        super().__init__()
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except OSError:
            import os
            os.system('python -m spacy download en_core_web_sm')
            self.nlp = spacy.load('en_core_web_sm')

        # 初始化购买动机相关的模式
        self.motivation_patterns = {
            'problem_solving': {
                'pain_points': {
                    'solve', 'fix', 'address', 'resolve', 'handle',
                    'problem', 'issue', 'challenge', 'difficulty'
                },
                'needs': {
                    'need', 'require', 'necessary', 'essential',
                    'must-have', 'important', 'crucial'
                }
            },
            'value_proposition': {
                'price': {
                    'price', 'cost', 'affordable', 'expensive',
                    'value', 'worth', 'budget', 'deal', 'discount'
                },
                'features': {
                    'feature', 'function', 'capability', 'option',
                    'specification', 'technology', 'innovation'
                },
                'quality': {
                    'quality', 'premium', 'high-end', 'professional',
                    'reliable', 'durable', 'well-made'
                }
            },
            'external_influence': {
                'recommendations': {
                    'recommend', 'suggestion', 'advice', 'review',
                    'rating', 'feedback', 'testimonial'
                },
                'comparison': {
                    'compare', 'alternative', 'competitor', 'better',
                    'best', 'difference', 'similar', 'versus'
                },
                'brand': {
                    'brand', 'reputation', 'trust', 'popular',
                    'well-known', 'famous', 'reliable'
                }
            },
            'timing_factors': {
                'urgency': {
                    'urgent', 'immediate', 'soon', 'emergency',
                    'quickly', 'asap', 'right away'
                },
                'opportunity': {
                    'opportunity', 'sale', 'promotion', 'offer',
                    'limited time', 'special', 'seasonal'
                }
            }
        }

    def _extract_categories(self, df) -> Dict[str, Set[str]]:
        """
        从评论中提取购买动机相关的类别和关键词

        参数:
            df: 评论数据DataFrame
        返回:
            Dict[str, Set[str]]: {动机类别: {相关关键词集合}}
        """
        motivation_keywords = defaultdict(set)

        # 分析每条评论
        for _, row in df.iterrows():
            text = f"{row['标题']} {row['内容']}"
            doc = self.nlp(text.lower())

            # 提取购买动机相关的短语
            for sent in doc.sents:
                # 分析购买相关的句子
                if self._is_purchase_related(sent):
                    motivation_phrases = self._extract_motivation_phrases(sent)

                    # 将短语分类到相应的动机类别中
                    for phrase, category in motivation_phrases:
                        motivation_keywords[category].add(phrase)

        # 过滤掉提及次数过少的类别
        min_mentions = 2
        filtered_motivations = {
            category: keywords
            for category, keywords in motivation_keywords.items()
            if len(keywords) >= min_mentions
        }

        return filtered_motivations

    def _is_purchase_related(self, sent) -> bool:
        """
        判断句子是否与购买相关

        参数:
            sent: spaCy的Span对象（句子）
        返回:
            bool: 是否与购买相关
        """
        purchase_words = {
            'buy', 'purchase', 'order', 'choose', 'select', 'decide',
            'get', 'acquire', 'invest', 'spend', 'bought', 'ordered'
        }
        return any(token.lemma_ in purchase_words for token in sent)

    def _extract_motivation_phrases(self, sent) -> List[Tuple[str, str]]:
        """
        从句子中提取动机相关的短语及其类别

        参数:
            sent: spaCy的Span对象（句子）
        返回:
            List[Tuple[str, str]]: [(短语, 类别)]
        """
        phrases = []

        # 寻找因果关系
        for token in sent:
            if token.dep_ in {'because', 'since', 'as'} or token.text in {'for', 'to'}:
                # 提取原因子句
                reason_phrase = self._extract_reason_phrase(token)
                if reason_phrase:
                    category = self._determine_motivation_category(reason_phrase)
                    if category:
                        phrases.append((reason_phrase, category))

            # 检查动机相关的关键词
            category = self._check_motivation_category(token.text)
            if category:
                phrase = self._extract_descriptive_phrase(token)
                if phrase:
                    phrases.append((phrase, category))

        return phrases

    def _extract_reason_phrase(self, token) -> str:
        """
        提取原因子句

        参数:
            token: spaCy的Token对象
        返回:
            str: 原因短语
        """
        # 找到从属子句
        for child in token.children:
            if child.dep_ in {'ccomp', 'advcl', 'pobj'}:
                # 获取子句的所有词
                subtree = list(child.subtree)
                return ' '.join(t.text for t in subtree)
        return None

    def _extract_descriptive_phrase(self, token) -> str:
        """
        提取描述性短语

        参数:
            token: spaCy的Token对象
        返回:
            str: 描述性短语
        """
        phrase_parts = []

        # 添加前置修饰语
        for child in token.children:
            if child.dep_ in {'amod', 'compound'} and child.i < token.i:
                phrase_parts.append(child.text)

        # 添加核心词
        phrase_parts.append(token.text)

        # 添加后置修饰语
        for child in token.children:
            if child.dep_ in {'prep', 'advmod', 'acomp'} and child.i > token.i:
                # 获取整个介词短语
                prep_phrase = [child.text]
                for grandchild in child.children:
                    if grandchild.dep_ == 'pobj':
                        prep_phrase.extend(t.text for t in grandchild.subtree)
                phrase_parts.extend(prep_phrase)

        return ' '.join(phrase_parts) if phrase_parts else None

    def _determine_motivation_category(self, text: str) -> str:
        """
        确定文本属于哪个动机类别

        参数:
            text: 待分析文本
        返回:
            str: 动机类别名称
        """
        for main_category, subcategories in self.motivation_patterns.items():
            for sub_category, keywords in subcategories.items():
                if any(keyword in text.lower() for keyword in keywords):
                    return f"{main_category}_{sub_category}"
        return None

    def _check_motivation_category(self, text: str) -> str:
        """
        检查单个词属于哪个动机类别

        参数:
            text: 待检查的文本
        返回:
            str: 动机类别名称
        """
        text = text.lower()
        for main_category, subcategories in self.motivation_patterns.items():
            for sub_category, keywords in subcategories.items():
                if text in keywords:
                    return f"{main_category}_{sub_category}"
        return None

    def _generate_insights(self, trend_results: Dict) -> Dict:
        """生成动机相关的分析洞察"""
        base_insights = super()._generate_insights(trend_results)

        # 添加动机特定的分析
        motivation_insights = {
            'purchase_drivers': {
                'primary_motivations': getattr(self, 'primary_motivations', []),
                'decision_factors': getattr(self, 'decision_factors', {}),
                'influence_sources': getattr(self, 'influence_sources', {})
            },
            'motivation_strength': getattr(self, 'motivation_scores', {}),
            'purchase_timing': getattr(self, 'timing_analysis', {})
        }

        base_insights.update(motivation_insights)
        return base_insights

    def _generate_motivation_specific_insights(self, results: Dict) -> Dict:
        """
        生成购买动机专属的洞察

        参数:
            results: 基础分析结果
        返回:
            Dict: 添加了专属洞察的结果
        """
        for category, data in results.items():
            specific_insights = []

            # 添加安全检查
            if '_' in category:
                main_cat, sub_cat = category.split('_')
            else:
                main_cat = category
                sub_cat = category
                continue  # 跳过不符合格式的类别

            # 基于不同动机维度生成洞察
            if main_cat == 'problem_solving':
                if data['percentage'] > 30:
                    specific_insights.append(
                        f"Users primarily purchase the product to address {sub_cat}, "
                        "highlighting key pain points in the market"
                    )

            elif main_cat == 'value_proposition':
                if data['percentage'] > 25:
                    specific_insights.append(
                        f"Product {sub_cat} is a crucial factor in purchase decisions"
                    )

            elif main_cat == 'external_influence':
                if data['percentage'] > 20:
                    specific_insights.append(
                        f"{sub_cat.title()} plays a significant role in "
                        "influencing purchase decisions"
                    )

            elif main_cat == 'timing_factors':
                if data['percentage'] > 15:
                    specific_insights.append(
                        f"{sub_cat.title()} is a key trigger for purchase decisions"
                    )

            # 添加专属洞察
            if 'insights' not in data:
                data['insights'] = []
            data['insights'].extend(specific_insights)

        return results

    def analyze(self, df) -> Dict:
        """
        分析购买动机

        参数:
            df: 评论数据DataFrame
        返回:
            Dict: 购买动机分析结果
        """
        # 使用基础分析流程
        results = super().analyze(df)

        # 添加购买动机专属的洞察
        results = self._generate_motivation_specific_insights(results)

        return results

"""
这个购买动机分析器的主要特点：
分析四个主要维度：
问题解决（痛点/需求）
价值主张（价格/功能/质量）
外部影响（推荐/对比/品牌）
时机因素（紧急程度/机会）
特殊的分析方法：
识别购买相关的句子
分析因果关系
提取原因子句
生成针对购买决策的专属洞察
"""