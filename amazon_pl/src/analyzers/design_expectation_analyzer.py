"""
产品设计期望分析器
功能：分析用户对产品设计的期望、评价和建议，包括外观、交互、人体工程学等方面
"""
from typing import Dict, Set, List, Tuple
import spacy
from collections import defaultdict
from .base_analyzer import BaseAnalyzer
from datetime import datetime


class DesignExpectationAnalyzer(BaseAnalyzer):
    def __init__(self):
        """初始化产品设计期望分析器"""
        super().__init__()
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except OSError:
            import os
            os.system('python -m spacy download en_core_web_sm')
            self.nlp = spacy.load('en_core_web_sm')

        # 初始化设计期望相关的模式
        self.design_patterns = {
            'aesthetics': {
                'appearance': {
                    'look', 'design', 'style', 'appearance', 'aesthetic',
                    'beautiful', 'attractive', 'sleek', 'modern', 'elegant'
                },
                'color': {
                    'color', 'colour', 'finish', 'texture', 'pattern',
                    'shade', 'tone', 'metallic', 'matte', 'glossy'
                },
                'materials': {
                    'material', 'quality', 'plastic', 'metal', 'glass',
                    'build', 'construction', 'premium', 'durable'
                }
            },
            'ergonomics': {
                'comfort': {
                    'comfort', 'comfortable', 'ergonomic', 'fit',
                    'grip', 'hold', 'handle', 'weight', 'balance'
                },
                'accessibility': {
                    'access', 'reach', 'accessible', 'convenient',
                    'easy to use', 'user-friendly', 'intuitive'
                },
                'safety': {
                    'safe', 'safety', 'secure', 'protection', 'stable',
                    'sturdy', 'reliable', 'risk', 'hazard'
                }
            },
            'interaction': {
                'controls': {
                    'button', 'switch', 'control', 'interface',
                    'touchscreen', 'display', 'panel', 'dial'
                },
                'feedback': {
                    'feedback', 'response', 'indicator', 'signal',
                    'light', 'sound', 'vibration', 'notification'
                },
                'layout': {
                    'layout', 'arrangement', 'position', 'placement',
                    'organization', 'setup', 'configuration'
                }
            },
            'dimensions': {
                'size': {
                    'size', 'dimension', 'large', 'small', 'compact',
                    'big', 'tiny', 'space', 'footprint'
                },
                'portability': {
                    'portable', 'carry', 'transport', 'move',
                    'lightweight', 'heavy', 'bulky', 'mobility'
                },
                'storage': {
                    'store', 'storage', 'fit', 'space-saving',
                    'compact', 'fold', 'collapse', 'capacity'
                }
            }
        }

    def _extract_categories(self, df) -> Dict[str, Set[str]]:
        """
        从评论中提取设计期望相关的类别和关键词

        参数:
            df: 评论数据DataFrame
        返回:
            Dict[str, Set[str]]: {设计类别: {相关关键词集合}}
        """
        design_keywords = defaultdict(set)

        # 分析每条评论
        for _, row in df.iterrows():
            text = f"{row['标题']} {row['内容']}"
            doc = self.nlp(text.lower())

            # 提取设计相关的短语
            for sent in doc.sents:
                design_phrases = self._extract_design_phrases(sent)

                # 将短语分类到相应的设计类别中
                for phrase, category in design_phrases:
                    design_keywords[category].add(phrase)

        # 过滤掉提及次数过少的类别
        min_mentions = 2
        filtered_designs = {
            category: keywords
            for category, keywords in design_keywords.items()
            if len(keywords) >= min_mentions
        }

        return filtered_designs

    def _extract_design_phrases(self, sent) -> List[Tuple[str, str]]:
        """
        从句子中提取设计相关的短语及其类别

        参数:
            sent: spaCy的Span对象（句子）
        返回:
            List[Tuple[str, str]]: [(短语, 类别)]
        """
        phrases = []

        for token in sent:
            # 检查形容词-名词搭配
            if token.pos_ in {'ADJ', 'NOUN'}:
                design_phrase = self._extract_design_description(token)
                if design_phrase:
                    category = self._determine_design_category(design_phrase)
                    if category:
                        phrases.append((design_phrase, category))

            # 检查动词短语（如"fits well", "looks good"）
            elif token.pos_ == 'VERB':
                for pattern in {'look', 'feel', 'fit', 'work', 'handle'}:
                    if token.lemma_ == pattern:
                        design_phrase = self._extract_verb_phrase(token)
                        if design_phrase:
                            category = self._determine_design_category(design_phrase)
                            if category:
                                phrases.append((design_phrase, category))

        return phrases

    def _extract_design_description(self, token) -> str:
        """
        提取设计描述短语

        参数:
            token: spaCy的Token对象
        返回:
            str: 设计描述短语
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
                prep_phrase = [child.text]
                for grandchild in child.children:
                    if grandchild.dep_ == 'pobj':
                        prep_phrase.extend(t.text for t in grandchild.subtree)
                description_parts.extend(prep_phrase)

        return ' '.join(description_parts) if description_parts else None

    def _extract_verb_phrase(self, token) -> str:
        """
        提取动词短语

        参数:
            token: spaCy的Token对象
        返回:
            str: 动词短语
        """
        phrase_parts = [token.text]

        # 添加副词修饰语
        for child in token.children:
            if child.dep_ == 'advmod':
                phrase_parts.append(child.text)

            # 添加补语
            elif child.dep_ in {'acomp', 'xcomp'}:
                phrase_parts.extend(t.text for t in child.subtree)

        return ' '.join(phrase_parts) if len(phrase_parts) > 1 else None

    def _determine_design_category(self, text: str) -> str:
        """
        确定设计描述属于哪个类别

        参数:
            text: 设计描述文本
        返回:
            str: 设计类别名称
        """
        text = text.lower()
        for main_category, subcategories in self.design_patterns.items():
            for sub_category, keywords in subcategories.items():
                if any(keyword in text for keyword in keywords):
                    return f"{main_category}_{sub_category}"
        return None

    def _generate_insights(self, trend_results: Dict) -> Dict:
        """生成设计期望相关的分析洞察"""
        base_insights = super()._generate_insights(trend_results)

        # 添加设计特定的分析
        design_insights = {
            'design_satisfaction': {
                'aesthetics_score': getattr(self, 'aesthetics_score', 0),
                'ergonomics_score': getattr(self, 'ergonomics_score', 0),
                'interaction_score': getattr(self, 'interaction_score', 0),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 格式化日期时间
            },
            'design_preferences': getattr(self, 'design_preferences', {}),
            'improvement_suggestions': getattr(self, 'design_suggestions', [])
        }

        base_insights.update(design_insights)
        return base_insights

    def _generate_design_specific_insights(self, results: Dict) -> Dict:
        """
        生成设计期望专属的洞察
        """
        for category, data in results.items():
            # 确保 data 是字典类型
            if not isinstance(data, dict):
                continue

            specific_insights = []

            try:
                # 安全地分解类别名称
                if '_' in category:
                    main_cat, sub_cat = category.split('_', 1)
                else:
                    continue

                # 基于不同设计维度生成洞察
                if data.get('percentage', 0) > 15:
                    # 美学相关洞察
                    if main_cat == 'aesthetics':
                        sentiment = data.get('sentiment', {})
                        pos_count = sentiment.get('positive', 0)
                        neg_count = sentiment.get('negative', 0)

                        if pos_count > neg_count:
                            specific_insights.append(
                                f"Users appreciate the product's {sub_cat}, "
                                "indicating successful design choices"
                            )
                        else:
                            specific_insights.append(
                                f"The product's {sub_cat} could be improved "
                                "to better meet user expectations"
                            )

                # 人体工程学相关洞察
                elif main_cat == 'ergonomics':
                    specific_insights.append(
                        f"{sub_cat.title()} is a significant factor "
                        "in user experience and satisfaction"
                    )

                # 交互相关洞察
                elif main_cat == 'interaction':
                    specific_insights.append(
                        f"User interaction through {sub_cat} plays a key role "
                        "in product usability"
                    )

                # 尺寸相关洞察
                elif main_cat == 'dimensions':
                    specific_insights.append(
                        f"Product {sub_cat} is an important consideration "
                        "for users in their usage context"
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
        分析设计期望

        参数:
            df: 评论数据DataFrame
        返回:
            Dict: 设计期望分析结果
        """
        # 保存 DataFrame 引用
        self.df = df

        # 使用基础分析流程
        results = super().analyze(df)

        # 添加设计期望专属的洞察
        results = self._generate_design_specific_insights(results)

        return results

"""
这个产品设计期望分析器的主要特点：
分析四个主要维度：
美学（外观/颜色/材料）
人体工程学（舒适度/可及性/安全性）
交互（控制/反馈/布局）
尺寸（大小/便携性/存储）
特殊的分析方法：
形容词-名词搭配分析
动词短语分析
设计描述提取
生成针对设计体验的专属洞察
"""
