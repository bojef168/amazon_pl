"""
用户体验分析器
功能：分析用户使用产品的体验，包括满意度、问题点、情感反应和具体反馈
"""
from typing import List, Tuple, Dict, Set, Optional
from collections import defaultdict
from .base_analyzer import BaseAnalyzer, ProcessingError
import spacy


class ExperienceAnalyzer(BaseAnalyzer):
    def __init__(self):
        """初始化用户体验分析器"""
        super().__init__()
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except OSError:
            import os
            os.system('python -m spacy download en_core_web_sm')
            self.nlp = spacy.load('en_core_web_sm')

        # 初始化用户体验相关的模式（移到这里）
        self.experience_patterns = {
            'satisfaction': {
                'positive': {
                    'excellent', 'great', 'amazing', 'love', 'perfect',
                    'fantastic', 'wonderful', 'satisfied', 'happy',
                    'impressed', 'awesome', 'best'
                },
                'negative': {
                    'disappointed', 'poor', 'bad', 'terrible', 'worst',
                    'frustrated', 'annoying', 'difficult', 'unhappy',
                    'dissatisfied', 'regret'
                }
            },
            'usability': {
                'ease_of_use': {
                    'easy', 'simple', 'intuitive', 'straightforward',
                    'user-friendly', 'convenient', 'effortless'
                },
                'learning_curve': {
                    'learn', 'understand', 'figure out', 'manual',
                    'instructions', 'tutorial', 'guidance'
                },
                'control': {
                    'control', 'adjust', 'customize', 'settings',
                    'options', 'flexible', 'versatile'
                }
            },
            'performance': {
                'reliability': {
                    'reliable', 'stable', 'consistent', 'dependable',
                    'trustworthy', 'solid', 'sturdy'
                },
                'efficiency': {
                    'fast', 'quick', 'efficient', 'powerful',
                    'effective', 'performance', 'speed'
                },
                'quality': {
                    'quality', 'well-made', 'durable', 'robust',
                    'premium', 'high-end', 'professional'
                }
            },
            'issues': {
                'technical': {
                    'error', 'bug', 'crash', 'malfunction', 'broken',
                    'defect', 'problem', 'issue'
                },
                'design': {
                    'awkward', 'bulky', 'heavy', 'noisy', 'loud',
                    'uncomfortable', 'inconvenient'
                },
                'support': {
                    'support', 'service', 'warranty', 'customer service',
                    'help', 'assistance', 'response'
                }
            }
        }

    def _extract_categories(self, df) -> Dict[str, Set[str]]:
        """
        从评论中提取用户体验相关的类别和关键词

        参数:
            df: 评论数据DataFrame
        返回:
            Dict[str, Set[str]]: {体验类别: {相关关键词集合}}
        """
        try:
            experience_keywords = defaultdict(set)

            # 分析每条评论
            for _, row in df.iterrows():
                try:
                    text = f"{row['标题']} {row['内容']}"
                    doc = self.nlp(text.lower())

                    # 提取体验相关的短语
                    for sent in doc.sents:
                        try:
                            # 分析每个句子的情感和体验描述
                            experience_phrases = self._extract_experience_phrases(sent)

                            # 将短语分类到相应的体验类别中
                            for phrase, category in experience_phrases:
                                experience_keywords[category].add(phrase)

                        except Exception as e:
                            self.logger.warning(f"Error processing sentence: {str(e)}")
                            continue

                except Exception as e:
                    self.logger.warning(f"Error processing row: {str(e)}")
                    continue

            # 过滤掉提及次数过少的类别
            min_mentions = 3
            filtered_experiences = {
                category: keywords
                for category, keywords in experience_keywords.items()
                if len(keywords) >= min_mentions
            }

            return filtered_experiences

        except Exception as e:
            self.logger.error(f"Category extraction failed: {str(e)}")
            raise ProcessingError(f"Failed to extract experience categories: {str(e)}")

    def _extract_experience_phrases(self, sent) -> List[Tuple[str, str]]:
        """
        从句子中提取体验相关的短语及其类别

        参数:
            sent: spaCy的Span对象（句子）
        返回:
            List[Tuple[str, str]]: [(短语, 类别)]
        """
        phrases = []

        for token in sent:
            # 检查是否是体验相关的词
            category = self._check_experience_category(token.text)
            if category:
                # 提取完整的体验描述短语
                phrase = self._extract_descriptive_phrase(token)
                if phrase:
                    phrases.append((phrase, category))

            # 检查形容词-名词搭配
            if token.pos_ == 'ADJ':
                for child in token.children:
                    if child.pos_ == 'NOUN':
                        compound = f"{token.text} {child.text}"
                        category = self._check_experience_category(compound)
                        if category:
                            phrases.append((compound, category))

        return phrases

    def _check_experience_category(self, text: str) -> str:
        """
        检查文本属于哪个体验类别

        参数:
            text: 待检查的文本
        返回:
            str: 体验类别名称
        """
        for main_category, subcategories in self.experience_patterns.items():
            for sub_category, keywords in subcategories.items():
                if any(keyword in text for keyword in keywords):
                    return f"{main_category}_{sub_category}"
        return None

    def _extract_descriptive_phrase(self, token) -> str:
        """
        提取完整的描述性短语

        参数:
            token: spaCy的Token对象
        返回:
            str: 描述性短语
        """
        phrase_parts = []

        # 添加前置修饰语
        for child in token.children:
            if child.dep_ in {'amod', 'advmod'} and child.i < token.i:
                phrase_parts.append(child.text)

        # 添加核心词
        phrase_parts.append(token.text)

        # 添加后置修饰语
        for child in token.children:
            if child.dep_ in {'prep', 'dobj', 'acomp'} and child.i > token.i:
                phrase_parts.append(child.text)
                # 添加介词短语的宾语
                if child.dep_ == 'prep':
                    for grandchild in child.children:
                        if grandchild.dep_ == 'pobj':
                            phrase_parts.append(grandchild.text)

        return ' '.join(phrase_parts) if phrase_parts else None

    def _generate_insights(self, trend_results: Dict) -> Dict:
        """生成体验相关的分析洞察"""
        base_insights = super()._generate_insights(trend_results)

        # 添加体验特定的分析
        experience_insights = {
            'satisfaction_metrics': {
                'overall_satisfaction': getattr(self, 'satisfaction_score', 0),
                'positive_experiences': getattr(self, 'positive_exp_count', 0),
                'negative_experiences': getattr(self, 'negative_exp_count', 0)
            },
            'usability_metrics': getattr(self, 'usability_scores', {}),
            'performance_metrics': getattr(self, 'performance_metrics', {}),
            'issue_tracking': getattr(self, 'reported_issues', {})
        }

        base_insights.update(experience_insights)
        return base_insights

    def _generate_experience_specific_insights(self, results: Dict) -> Dict:
        """
        生成用户体验专属的洞察

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

            # 基于不同体验维度生成洞察
            if main_cat == 'satisfaction':
                if data['percentage'] > 30:
                    if sub_cat == 'positive':
                        specific_insights.append(
                            "Users express high overall satisfaction with the product"
                        )
                    else:
                        specific_insights.append(
                            "There are significant user satisfaction concerns to address"
                        )

            elif main_cat == 'usability':
                if data['percentage'] > 20:
                    specific_insights.append(
                        f"Users frequently mention {sub_cat.replace('_', ' ')}, "
                        "indicating its importance in the user experience"
                    )

            elif main_cat == 'performance':
                if data['percentage'] > 25:
                    specific_insights.append(
                        f"Product {sub_cat} is a key factor in user experience"
                    )

            elif main_cat == 'issues':
                if data['percentage'] > 15:
                    specific_insights.append(
                        f"Users report notable {sub_cat} issues that need attention"
                    )

            # 添加专属洞察
            if 'insights' not in data:
                data['insights'] = []
            data['insights'].extend(specific_insights)

        return results

    def analyze(self, df) -> Dict:
        """
        分析用户体验

        参数:
            df: 评论数据DataFrame
        返回:
            Dict: 用户体验分析结果
        """
        # 使用基础分析流程
        results = super().analyze(df)

        # 添加用户体验专属的洞察
        results = self._generate_experience_specific_insights(results)

        return results

"""
这个用户体验分析器的主要特点：
分析四个主要维度：
满意度（正面/负面）
可用性（易用性/学习曲线/控制）
性能（可靠性/效率/质量）
问题（技术/设计/支持）
使用复杂的语言分析：
形容词-名词搭配分析
完
整描述性短语提取
多层次的体验分类
生成针对性的用户体验洞察
"""