"""
使用场景分析器
功能：分析用户在什么场景下使用产品，包括具体情境、活动类型和环境条件
"""
from typing import Dict, Set, List, Tuple
import spacy
from collections import defaultdict
from .base_analyzer import BaseAnalyzer


class ScenarioAnalyzer(BaseAnalyzer):
    def __init__(self):
        """初始化使用场景分析器"""
        super().__init__()
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except OSError:
            import os
            os.system('python -m spacy download en_core_web_sm')
            self.nlp = spacy.load('en_core_web_sm')

        # 初始化场景相关的模式
        self.scenario_patterns = {
            'activity_type': {
                'daily_routine': {
                    'cleaning', 'cooking', 'working', 'studying',
                    'exercise', 'relaxing', 'entertainment', 'daily'
                },
                'special_occasion': {
                    'party', 'gathering', 'event', 'holiday',
                    'celebration', 'special', 'occasion', 'guest'
                },
                'emergency': {
                    'emergency', 'urgent', 'quick', 'immediate',
                    'unexpected', 'sudden', 'crisis', 'problem'
                }
            },
            'environment': {
                'indoor': {
                    'home', 'office', 'room', 'indoor', 'inside',
                    'house', 'apartment', 'building'
                },
                'outdoor': {
                    'outdoor', 'outside', 'garden', 'yard', 'patio',
                    'balcony', 'terrace', 'exterior'
                },
                'public': {
                    'public', 'shared', 'common', 'community',
                    'social', 'group', 'collective'
                }
            },
            'condition': {
                'weather': {
                    'rain', 'sunny', 'hot', 'cold', 'wet', 'dry',
                    'weather', 'temperature', 'climate'
                },
                'noise': {
                    'quiet', 'noisy', 'loud', 'silent', 'peaceful',
                    'sound', 'noise', 'disturbance'
                },
                'lighting': {
                    'bright', 'dark', 'light', 'dim', 'shadow',
                    'sunlight', 'lighting', 'illumination'
                }
            }
        }

    def _extract_categories(self, df) -> Dict[str, Set[str]]:
        """
        从评论中提取场景相关的类别和关键词

        参数:
            df: 评论数据DataFrame
        返回:
            Dict[str, Set[str]]: {场景类别: {相关关键词集合}}
        """
        scenario_keywords = defaultdict(set)

        # 分析每条评论
        for _, row in df.iterrows():
            text = f"{row['标题']} {row['内容']}"
            doc = self.nlp(text.lower())

            # 提取场景相关的短语
            for sent in doc.sents:
                scenario_phrases = self._extract_scenario_phrases(sent)

                # 将短语分类到相应的场景类别中
                for phrase, category in scenario_phrases:
                    scenario_keywords[category].add(phrase)

        # 过滤掉提及次数过少的类别
        min_mentions = 2
        filtered_scenarios = {
            category: keywords
            for category, keywords in scenario_keywords.items()
            if len(keywords) >= min_mentions
        }

        return filtered_scenarios

    def _extract_scenario_phrases(self, sent) -> List[Tuple[str, str]]:
        """
        从句子中提取场景相关的短语及其类别

        参数:
            sent: spaCy的Span对象（句子）
        返回:
            List[Tuple[str, str]]: [(短语, 类别)]
        """
        phrases = []

        # 检查时间和地点相关的介词短语
        for token in sent:
            if token.dep_ == 'prep' and token.text in {'in', 'at', 'during', 'while', 'when'}:
                scenario_phrase = self._extract_prep_phrase(token)
                if scenario_phrase:
                    category = self._determine_scenario_category(scenario_phrase)
                    if category:
                        phrases.append((scenario_phrase, category))

            # 检查场景描述词
            elif token.pos_ in {'NOUN', 'ADJ'}:
                scenario_phrase = self._extract_scenario_description(token)
                if scenario_phrase:
                    category = self._determine_scenario_category(scenario_phrase)
                    if category:
                        phrases.append((scenario_phrase, category))

        return phrases

    def _extract_prep_phrase(self, token) -> str:
        """
        提取介词短语

        参数:
            token: spaCy的Token对象
        返回:
            str: 介词短语
        """
        phrase_parts = [token.text]

        # 添加介词的宾语及其修饰语
        for child in token.children:
            if child.dep_ == 'pobj':
                # 添加宾语的修饰语
                for grandchild in child.children:
                    if grandchild.dep_ in {'amod', 'compound'} and grandchild.i < child.i:
                        phrase_parts.append(grandchild.text)

                # 添加宾语
                phrase_parts.append(child.text)

                # 添加后置修饰语
                for grandchild in child.children:
                    if grandchild.dep_ in {'prep', 'advmod'} and grandchild.i > child.i:
                        phrase_parts.extend(t.text for t in grandchild.subtree)

        return ' '.join(phrase_parts) if len(phrase_parts) > 1 else None

    def _extract_scenario_description(self, token) -> str:
        """
        提取场景描述短语

        参数:
            token: spaCy的Token对象
        返回:
            str: 场景描述短语
        """
        description_parts = []

        # 添加前置修饰语
        for child in token.children:
            if child.dep_ in {'amod', 'compound'} and child.i < token.i:
                description_parts.append(child.text)

        # 添加核心词
        description_parts.append(token.text)

        # 添加后置修饰语
        for child in token.children:
            if child.dep_ in {'prep', 'advmod'} and child.i > token.i:
                description_parts.extend(t.text for t in child.subtree)

        return ' '.join(description_parts) if description_parts else None

    def _determine_scenario_category(self, text: str) -> str:
        """
        确定场景描述属于哪个类别

        参数:
            text: 场景描述文本
        返回:
            str: 场景类别名称
        """
        text = text.lower()
        for main_category, subcategories in self.scenario_patterns.items():
            for sub_category, keywords in subcategories.items():
                if any(keyword in text for keyword in keywords):
                    return f"{main_category}_{sub_category}"
        return None

    def _generate_insights(self, trend_results: Dict) -> Dict:
        """生成场景相关的分析洞察"""
        base_insights = super()._generate_insights(trend_results)

        # 添加场景特定的分析
        scenario_insights = {
            'activity_patterns': getattr(self, 'activity_distribution', {}),
            'environment_usage': getattr(self, 'environment_distribution', {}),
            'condition_impact': getattr(self, 'condition_impact', {}),
            'common_scenarios': getattr(self, 'frequent_scenarios', [])
        }

        base_insights.update(scenario_insights)
        return base_insights

    def _generate_scenario_specific_insights(self, results: Dict) -> Dict:
        """
        生成使用场景专属的洞察

        参数:
            results: 基础分析结果
        返回:
            Dict: 添加了专属洞察的结果
        """
        for category, data in results.items():
            # 确保 data 是字典类型
            if not isinstance(data, dict):
                continue

            specific_insights = []

            try:
                # 安全地分解类别名称
                if '_' in category:
                    main_cat, sub_cat = category.split('_', 1)  # 只分割第一个下划线
                else:
                    # 如果没有下划线，将整个类别作为 main_cat
                    main_cat = category
                    sub_cat = ''

                # 基于不同场景维度生成洞察
                if data.get('percentage', 0) > 15:
                    if main_cat == 'activity_type':
                        specific_insights.append(
                            f"The product is frequently used during {sub_cat.replace('_', ' ')} "
                            "activities, suggesting specific use case optimization"
                        )

                    elif main_cat == 'environment':
                        specific_insights.append(
                            f"{sub_cat.title() if sub_cat else 'Various'} environments represent "
                            "a key usage context, indicating important design considerations"
                        )

                    elif main_cat == 'condition':
                        specific_insights.append(
                            f"{sub_cat.title() if sub_cat else 'Environmental'} conditions "
                            "significantly impact product usage, requiring specific optimizations"
                        )

                # 添加专属洞察
                if specific_insights:
                    data['insights'] = data.get('insights', []) + specific_insights

            except Exception as e:
                self.logger.warning(f"Error generating insights for category {category}: {str(e)}")
                continue

        return results

    def analyze(self, df) -> Dict:
        """
        分析使用场景

        参数:
            df: 评论数据DataFrame
        返回:
            Dict: 使用场景分析结果
        """
        # 使用基础分析流程
        results = super().analyze(df)

        # 添加使用场景专属的洞察
        results = self._generate_scenario_specific_insights(results)

        return results

    """
    这个使用场景分析器的主要特点：
    分析三个主要维度：
    活动类型（日常 / 特殊场合 / 紧急情况）
    环境（室内 / 室外 / 公共场所）
    条件（天气 / 噪音 / 光线）
    特殊的分析方法：
    介词短语分析（ in, at, during等）
    场景描述词提取
    环境条件识别
    生成针对使用场景的专属洞察
    """