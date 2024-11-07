"""
情感分析工具
功能：提供文本情感分析功能，包括细粒度情感分类、关键词提取和置信度评分
"""
from textblob import TextBlob
from typing import Dict, List, Tuple
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import sentiwordnet as swn
import re
import logging

class SentimentAnalysisError(Exception):
    """情感分析错误"""
    pass


class SentimentAnalyzer:
    def __init__(self):
        """初始化情感分析器"""
        # 设置日志
        self.logger = logging.getLogger(self.__class__.__name__)

        # 确保必要的NLTK数据已下载
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/sentiwordnet')
        except LookupError:
            try:
                nltk.download('punkt')
                nltk.download('sentiwordnet')
                nltk.download('averaged_perceptron_tagger')
                nltk.download('wordnet')
            except Exception as e:
                self.logger.error(f"Failed to download NLTK data: {str(e)}")
                raise SentimentAnalysisError(f"NLTK initialization failed: {str(e)}")

        # 情感强度阈值
        self.intensity_thresholds = {
            'very_positive': 0.6,
            'positive': 0.1,
            'very_negative': -0.6,
            'negative': -0.1
        }

        # 情感词典
        self.sentiment_words = {
            'positive': {'excellent', 'great', 'good', 'nice', 'wonderful', 'amazing', 'fantastic'},
            'negative': {'poor', 'bad', 'terrible', 'awful', 'horrible', 'disappointing', 'useless'}
        }

    def analyze_sentiment(self, text: str) -> Dict:
        """
        分析文本情感

        参数:
            text: 待分析文本
        返回:
            Dict: {
                'polarity': float,  # 情感极性 (-1到1)
                'subjectivity': float,  # 主观性程度 (0到1)
                'label': str,  # 详细情感标签
                'confidence': float,  # 置信度
                'sentiment_words': List[Tuple[str, str]]  # 情感词及其极性
            }
        """
        try:
            blob = TextBlob(str(text))
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity

            # 获取详细情感标签和置信度
            label, confidence = self._get_detailed_sentiment(polarity, subjectivity)

            # 提取情感词
            sentiment_words = self._extract_sentiment_words(text)

            return {
                'polarity': polarity,
                'subjectivity': subjectivity,
                'label': label,
                'confidence': confidence,
                'sentiment_words': sentiment_words
            }
        except Exception as e:
            self.logger.error(f"Sentiment analysis failed: {str(e)}")
            raise SentimentAnalysisError(f"Failed to analyze sentiment: {str(e)}")

    def _get_detailed_sentiment(
            self,
            polarity: float,
            subjectivity: float
        ) -> Tuple[str, float]:
        """
        获取详细的情感标签和置信度

        参数:
            polarity: 情感极性值
            subjectivity: 主观性程度
        返回:
            Tuple[str, float]: (情感标签, 置信度)
        """
        # 基于极性值确定标签
        if polarity >= self.intensity_thresholds['very_positive']:
            label = 'very positive'
        elif polarity >= self.intensity_thresholds['positive']:
            label = 'positive'
        elif polarity <= self.intensity_thresholds['very_negative']:
            label = 'very negative'
        elif polarity <= self.intensity_thresholds['negative']:
            label = 'negative'
        else:
            label = 'neutral'

        # 计算置信度
        # 考虑极性的绝对值和主观性程度
        confidence = (abs(polarity) + subjectivity) / 2

        return label, confidence

    def _extract_sentiment_words(self, text: str) -> List[Tuple[str, str]]:
        """
        提取文本中的情感词及其极性

        参数:
            text: 输入文本
        返回:
            List[Tuple[str, str]]: [(词语, 极性), ...]
        """
        tokens = word_tokenize(text.lower())
        tagged = nltk.pos_tag(tokens)
        sentiment_words = []

        for word, tag in tagged:
            # 只分析形容词、副词和动词
            if tag.startswith(('JJ', 'RB', 'VB')):
                sentiment = self._get_word_sentiment(word)
                if sentiment != 'neutral':
                    sentiment_words.append((word, sentiment))

        return sentiment_words

    def _get_word_sentiment(self, word: str) -> str:
        """
        获取单词的情感极性

        参数:
            word: 输入单词
        返回:
            str: 情感极性 (positive/negative/neutral)
        """
        # 首先检查预定义的情感词典
        if word in self.sentiment_words['positive']:
            return 'positive'
        if word in self.sentiment_words['negative']:
            return 'negative'

        # 使用SentiWordNet进行更深入的分析
        synsets = list(swn.senti_synsets(word))
        if not synsets:
            return 'neutral'

        # 计算平均情感分数
        pos_score = sum(s.pos_score() for s in synsets) / len(synsets)
        neg_score = sum(s.neg_score() for s in synsets) / len(synsets)

        if pos_score > neg_score:
            return 'positive' if pos_score > 0.1 else 'neutral'
        elif neg_score > pos_score:
            return 'negative' if neg_score > 0.1 else 'neutral'
        else:
            return 'neutral'

    def analyze_sentiment_trend(
            self,
            texts: List[str],
            timestamps: List[str] = None
        ) -> Dict:
        """
        分析情感变化趋势

        参数:
            texts: 文本列表
            timestamps: 对应的时间戳列表（可选）
        返回:
            Dict: {
                'trend': str,  # 趋势描述
                'sentiment_scores': List[float],  # 情感分数列表
                'average_sentiment': float,  # 平均情感分数
                'volatility': float  # 情感波动性
            }
        """
        try:
            if not texts:
                raise ValueError("Empty text list provided")

            sentiment_scores = []
            for text in texts:
                try:
                    score = self.analyze_sentiment(text)['polarity']
                    sentiment_scores.append(score)
                except Exception as e:
                    self.logger.warning(f"Error analyzing text: {str(e)}")
                    continue

            if not sentiment_scores:
                raise SentimentAnalysisError("No valid sentiment scores generated")

            # 计算平均情感分数
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)

            # 计算情感波动性（标准差）
            volatility = (sum((s - avg_sentiment) ** 2 for s in sentiment_scores)
                          / len(sentiment_scores)) ** 0.5

            # 确定趋势
            if len(sentiment_scores) > 1:
                start_avg = sum(sentiment_scores[:3]) / 3  # 前3个评论的平均
                end_avg = sum(sentiment_scores[-3:]) / 3  # 后3个评论的平均

                if end_avg - start_avg > 0.2:
                    trend = 'improving'
                elif start_avg - end_avg > 0.2:
                    trend = 'declining'
                else:
                    trend = 'stable'
            else:
                trend = 'insufficient_data'

            return {
                'trend': trend,
                'sentiment_scores': sentiment_scores,
                'average_sentiment': avg_sentiment,
                'volatility': volatility
            }

        except Exception as e:
            self.logger.error(f"Sentiment trend analysis failed: {str(e)}")
            raise SentimentAnalysisError(f"Failed to analyze sentiment trend: {str(e)}")

    """
    细粒度情感分类：
    五个级别：very
    positive, positive, neutral, negative, very
    negative
    基于极性值和主观性程度
    情感词提取：
    使用NLTK进行词性标注
    结合SentiWordNet进行情感分析
    维护自定义情感词典
    置信度评分：
    结合极性值和主观性程度
    提供分析结果的可信度评估
    情感趋势分析：
    分析情感变化趋势
    计算情感波动性
    支持时间序列分析
    """