"""
用户特征分析器
功能：分析用户的特征，包括用户类型、使用习惯、专业程度等
"""
import pandas as pd
from typing import Dict, Set, List, Tuple
import spacy
from collections import defaultdict
from .base_analyzer import BaseAnalyzer, ProcessingError


class UserAnalyzer(BaseAnalyzer):
    def __init__(self):
        """初始化用户特征分析器"""
        super().__init__()

        # 添加日志前缀
        self.logger.name = "UserAnalyzer"

        # 初始化用户特征相关的模式
        self.user_patterns = {
            'user_type': {
                'professional': {
                    'professional', 'expert', 'experienced', 'advanced',
                    'tech-savvy', 'power user', 'specialist', 'pro'
                },
                'casual': {
                    'casual', 'regular', 'normal', 'average', 'typical',
                    'everyday', 'occasional', 'basic'
                },
                'beginner': {
                    'beginner', 'new', 'novice', 'first-time', 'starter',
                    'learning', 'starting out', 'inexperienced'
                }
            },
            'usage_pattern': {
                'frequent': {
                    'daily', 'frequently', 'regularly', 'often', 'always',
                    'heavy use', 'constant', 'intensive'
                },
                'moderate': {
                    'weekly', 'occasionally', 'sometimes', 'moderate',
                    'periodic', 'regular', 'routine'
                },
                'infrequent': {
                    'rarely', 'seldom', 'occasional', 'light use',
                    'sporadic', 'infrequent', 'once in a while'
                }
            },
            'tech_comfort': {
                'tech_savvy': {
                    'tech-savvy', 'technical', 'technology', 'gadget',
                    'digital', 'smart', 'connected', 'automated'
                },
                'tech_neutral': {
                    'comfortable', 'familiar', 'understand', 'manage',
                    'handle', 'work with', 'use'
                },
                'tech_cautious': {
                    'cautious', 'careful', 'hesitant', 'traditional',
                    'simple', 'basic', 'straightforward'
                }
            }
        }

    def _analyze_sentiment(self, df: pd.DataFrame, mention_results: Dict = None) -> Dict:
        """分析情感倾向"""
        try:
            sentiment_results = {}

            # 如果有提及统计结果，则按类别分析情感
            if mention_results:
                for category, mentions in mention_results.items():
                    # 使用 indices 而不是 comment_ids
                    if 'indices' in mentions and mentions['indices']:
                        category_comments = df.loc[mentions['indices']]
                        if not category_comments.empty:
                            sentiment_scores = [
                                self.sentiment_analyzer.analyze_sentiment(text)['polarity']
                                for text in category_comments['内容'].tolist()
                            ]
                            sentiment_results[category] = {
                                'sentiment_scores': sentiment_scores,
                                'average_sentiment': sum(sentiment_scores) / len(sentiment_scores)
                            }

            # 分析整体情感
            all_sentiments = [
                self.sentiment_analyzer.analyze_sentiment(text)['polarity']
                for text in df['内容'].tolist()
            ]
            sentiment_results['overall'] = {
                'sentiment_scores': all_sentiments,
                'average_sentiment': sum(all_sentiments) / len(all_sentiments)
            }

            return sentiment_results

        except Exception as e:
            self.logger.error(f"Error analyzing sentiment: {str(e)}")
            raise

    def _extract_categories(self, df) -> Dict[str, Set[str]]:
        """
        从评论中提取用户特征相关的类别和关键词

        参数:
            df: 评论数据DataFrame
        返回:
            Dict[str, Set[str]]: {特征类别: {相关关键词集合}}
        """
        try:
            user_keywords = defaultdict(set)

            # 分析每条评论
            for _, row in df.iterrows():
                try:
                    # 确保文本字段是字符串类型
                    title = str(row.get('标题', ''))
                    content = str(row.get('内容', ''))
                    text = f"{title} {content}"
                    doc = self.nlp(text.lower())

                    # 提取用户特征相关的短语
                    for sent in doc.sents:
                        try:
                            user_phrases = self._extract_user_phrases(sent)
                            for phrase, category in user_phrases:
                                # 确保 category 和 phrase 都是字符串
                                category_str = str(category)
                                phrase_str = str(phrase)

                                # 如果类别是复合的，将其转换为单个字符串
                                if isinstance(category, (list, tuple)):
                                    category_str = '_'.join(map(str, category))

                                user_keywords[category_str].add(phrase_str)
                        except Exception as e:
                            self.logger.warning(f"Error processing sentence: {str(e)}")
                            continue

                except Exception as e:
                    self.logger.warning(f"Error processing row: {str(e)}")
                    continue

            # 过滤掉提及次数过少的类别
            min_mentions = 2
            filtered_features = {
                str(category): {str(keyword) for keyword in keywords}
                for category, keywords in user_keywords.items()
                if len(keywords) >= min_mentions
            }

            return filtered_features

        except Exception as e:
            self.logger.error(f"Category extraction failed: {str(e)}")
            raise ProcessingError(f"Failed to extract user categories: {str(e)}")

    def _extract_user_phrases(self, sent) -> List[Tuple[str, str]]:
        """
        从句子中提取用户特征相关的短语及其类别

        参数:
            sent: spaCy的Span对象（句子）
        返回:
            List[Tuple[str, str]]: [(短语, 类别)]
        """
        phrases = []

        # 检查是否包含第一人称代词
        has_first_person = any(token.text in {'i', 'we', 'my', 'our'} for token in sent)

        for token in sent:
            # 如果句子包含第一人称，更可能是用户自我描述
            if has_first_person:
                # 检查形容词和名词搭配
                if token.pos_ in {'ADJ', 'NOUN'}:
                    user_phrase = self._extract_user_description(token)
                    if user_phrase:
                        category = self._determine_user_category(user_phrase)
                        if category:
                            phrases.append((user_phrase, category))

            # 检查动词短语，表示使用习惯
            if token.pos_ == 'VERB':
                usage_phrase = self._extract_usage_pattern(token)
                if usage_phrase:
                    category = self._determine_user_category(usage_phrase)
                    if category:
                        phrases.append((usage_phrase, category))

        return phrases

    def _extract_user_description(self, token) -> str:
        """
        提取用户描述短语

        参数:
            token: spaCy的Token对象
        返回:
            str: 用户描述短语
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

    def _extract_usage_pattern(self, token) -> str:
        """
        提取使用习惯相关的短语

        参数:
            token: spaCy的Token对象
        返回:
            str: 使用习惯短语
        """
        if token.lemma_ in {'use', 'utilize', 'operate', 'work'}:
            pattern_parts = [token.text]

            # 添加频率副词
            for child in token.children:
                if child.dep_ == 'advmod':
                    pattern_parts.append(child.text)

                # 添加时间相关的介词短语
                elif child.dep_ == 'prep' and child.text in {'for', 'since', 'during'}:
                    pattern_parts.extend(t.text for t in child.subtree)

            return ' '.join(pattern_parts) if len(pattern_parts) > 1 else None
        return None

    def _determine_user_category(self, text: str) -> str:
        """
        确定用户特征描述属于哪个类别

        参数:
            text: 用户特征描述文本
        返回:
            str: 特征类别名称
        """
        text = text.lower()
        for main_category, subcategories in self.user_patterns.items():
            for sub_category, keywords in subcategories.items():
                if any(keyword in text for keyword in keywords):
                    return f"{main_category}_{sub_category}"
        return None

    def _generate_user_specific_insights(self, results: Dict) -> Dict:
        """
        生成用户特征专属的洞察

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

            # 基于不同用户特征维度生成洞察
            if data.get('percentage', 0) > 15:  # 添加 get 方法的安全访问
                if main_cat == 'user_type':
                    specific_insights.append(
                        f"A significant portion of users identify as {sub_cat} users, "
                        "suggesting the need for appropriate feature complexity"
                    )

                elif main_cat == 'usage_pattern':
                    specific_insights.append(
                        f"The product sees {sub_cat} usage patterns, "
                        "indicating specific reliability requirements"
                    )

                elif main_cat == 'tech_comfort':
                    specific_insights.append(
                        f"Users demonstrate {sub_cat.replace('_', ' ')} "
                        "comfort levels with technology"
                    )

            # 添加专属洞察
            if 'insights' not in data:
                data['insights'] = []
            data['insights'].extend(specific_insights)

        return results

    def analyze(self, df) -> Dict:
        """
        分析用户特征

        参数:
            df: 评论数据DataFrame
        返回:
            Dict: 用户特征分析结果
        """
        # 保存 DataFrame 的引用
        self.df = df

        # 使用基础分析流程
        results = super().analyze(df)

        # 添加用户特征专属的洞察
        results = self._generate_user_specific_insights(results)

        return results

    def _generate_insights(self, trend_results: Dict) -> Dict:
        """
        生成用户分析洞察

        参数:
            trend_results: 趋势分析结果
        返回:
            Dict: 包含分析洞察的字典
        """
        insights = {
            'summary': {
                'total_reviews': len(self.df),
                'unique_users': len(self.df['用户ID'].unique()) if '用户ID' in self.df.columns else 0,
            },
            'sentiment': {
                'positive_ratio': (self.df['情感分数'] > 0).mean() if '情感分数' in self.df.columns else 0,
                'negative_ratio': (self.df['情感分数'] < 0).mean() if '情感分数' in self.df.columns else 0,
                'neutral_ratio': (self.df['情感分数'] == 0).mean() if '情感分数' in self.df.columns else 0,
            },
            'categories': self.category_counts if hasattr(self, 'category_counts') else {},
            'trends': trend_results,
            'key_findings': [
                "基于用户评论的主要发现...",
                "用户情感分布情况...",
                "主要关注的产品类别..."
            ]
        }

        return insights

"""
用户特征分析器的主要特点：
分析三个主要维度：
用户类型（专业用户/普通用户/新手用户）
使用频率（频繁/适中/不频繁）
技术熟悉度（技术熟练/技术中立/技术谨慎）
2. 特殊的分析方法：
识别第一人称代词，提高自我描述的识别准确性
形容词-名词搭配分析
使用习惯动词短语分析
生成针对用户群体特征的专属洞察
"""