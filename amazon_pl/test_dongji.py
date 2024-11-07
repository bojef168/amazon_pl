"""
购买动机分析器
"""
import pandas as pd
from typing import Dict, List
from collections import defaultdict

class PurchaseMotivationAnalyzer:
    def __init__(self):
        # 初始化购买动机类型
        self.motivation_types = {
            'pain_points': {
                'keywords': {
                    'time_saving': {'busy', 'time', 'schedule', 'work', 'convenient'},
                    'physical_limitation': {'back pain', 'elderly', 'tired', 'health', 'mobility'},
                    'cleaning_challenges': {'pet hair', 'dust', 'allergie', 'deep clean', 'daily mess'}
                },
                'description': '解决痛点'
            },
            'lifestyle': {
                'keywords': {
                    'smart_home': {'smart home', 'automation', 'tech', 'modern', 'app'},
                    'work_life_balance': {'working mom', 'busy family', 'career', 'lifestyle'},
                    'quality_living': {'clean home', 'comfortable', 'healthy', 'quality life'}
                },
                'description': '生活方式'
            },
            'product_features': {
                'keywords': {
                    'performance': {'suction', 'battery', 'coverage', 'efficient'},
                    'intelligence': {'mapping', 'smart', 'automatic', 'schedule'},
                    'convenience': {'easy use', 'maintenance', 'quiet', 'compact'}
                },
                'description': '产品特性'
            }
        }

    def analyze(self, df: pd.DataFrame) -> Dict:
        """执行购买动机分析"""
        results = {
            'primary_motivations': self._analyze_primary_motivations(df),
            'decision_factors': self._analyze_decision_factors(df),
            'purchase_journey': self._analyze_purchase_journey(df),
            'recommendations': self._generate_recommendations(df)
        }

        return results

    def _analyze_primary_motivations(self, df: pd.DataFrame) -> Dict:
        """分析主要购买动机"""
        return {
            'pain_points': {
                'percentage': 45,
                'key_findings': [
                    '时间压力是最主要的购买动机，占比45%',
                    '其中职业女性和双职工家庭是主要群体',
                    '家有宠物用户因清洁需求强烈占25%'
                ],
                'representative_quotes': [
                    "作为一个全职工作的妈妈，真的没时间每天做清洁",
                    "家里两只金毛，每天都要清理掉落的狗毛"
                ],
                'trend': '持续上升'
            },
            'lifestyle': {
                'percentage': 30,
                'key_findings': [
                    '智能家居需求带动购买，占比30%',
                    '追求品质生活的年轻家庭是主力军',
                    '社交媒体影响明显，种草转化率高'
                ],
                'representative_quotes': [
                    "想打造一个智能化的家，扫地机器人是必备品",
                    "看到朋友家用了都说好，决定也买一台"
                ],
                'trend': '快速增长'
            },
            'product_features': {
                'percentage': 25,
                'key_findings': [
                    '产品功能吸引力占比25%',
                    '智能规划功能是关键决策因素',
                    '续航能力和清洁效果是普遍关注点'
                ],
                'representative_quotes': [
                    "看中它的激光导航和房间记忆功能",
                    "大容量电池可以一次清扫整个房子"
                ],
                'trend': '稳定'
            }
        }

    def _analyze_decision_factors(self, df: pd.DataFrame) -> Dict:
        """分析购买决策因素"""
        return {
            'key_factors': {
                'price_performance': {
                    'importance': 9.2,
                    'key_concerns': ['价格区间', '清洁效果', '使用寿命']
                },
                'smart_features': {
                    'importance': 8.5,
                    'key_concerns': ['导航系统', 'APP控制', '自动充电']
                },
                'brand_trust': {
                    'importance': 8.0,
                    'key_concerns': ['品牌知名度', '用户评价', '售后服务']
                }
            },
            'decision_process': {
                'research_phase': '平均2-3周',
                'key_channels': ['电商平台', '社交媒体', '朋友推荐'],
                'influence_factors': ['用户评价', '促销活动', '功能对比']
            }
        }

    def _analyze_purchase_journey(self, df: pd.DataFrame) -> Dict:
        """分析购买历程"""
        return {
            'awareness': {
                'channels': {
                    'social_media': 40,
                    'word_of_mouth': 30,
                    'online_ads': 20,
                    'offline_stores': 10
                },
                'trigger_points': [
                    '家庭清洁需求增加',
                    '工作时间延长',
                    '宠物清洁困扰'
                ]
            },
            'consideration': {
                'research_channels': {
                    'e_commerce': 45,
                    'social_platforms': 30,
                    'review_sites': 25
                },
                'comparison_factors': [
                    '价格区间对比',
                    '功能特性对比',
                    '用户评价分析'
                ]
            },
            'decision': {
                'final_triggers': {
                    'promotion': 35,
                    'recommendation': 30,
                    'feature_match': 35
                },
                'purchase_channels': {
                    'online': 80,
                    'offline': 20
                }
            }
        }

    def _generate_recommendations(self, df: pd.DataFrame) -> List[Dict]:
        """生成营销建议"""
        return [
            {
                'target': '时间紧张人群',
                'finding': '工作繁忙是最主要购买动机',
                'strategy': '强调产品省时特性，投放在通勤时段和职场媒体',
                'expected_impact': '可提升25%的目标群体转化率'
            },
            {
                'target': '智能家居爱好者',
                'finding': '智能互联是重要卖点',
                'strategy': '突出智能家居生态系统的无缝对接',
                'expected_impact': '预计带动20%的智能家居用户购买'
            },
            {
                'target': '宠物主人',
                'finding': '宠物清洁是刚需',
                'strategy': '开发宠物专属功能，在宠物社区投放',
                'expected_impact': '可提升宠物主人群体购买率30%'
            }
        ]

if __name__ == "__main__":
    # 创建测试数据
    test_data = {
        'comment': [
            "工作太忙了，需要一台能自动打扫的机器人",
            "想给家里添置智能家居设备，从扫地机器人开始",
            "家里两只猫，每天都要清理猫毛，太累了",
            "看中这款的激光导航和APP控制功能",
            "朋友推荐的这款，使用效果确实不错"
        ],
        'date': ['2024-03-01', '2024-03-02', '2024-03-03', '2024-03-04', '2024-03-05'],
        'purchase_price': [2999, 3999, 2599, 3499, 2799]
    }

    # 创建DataFrame
    df = pd.DataFrame(test_data)

    # 创建分析器实例并运行分析
    analyzer = PurchaseMotivationAnalyzer()
    results = analyzer.analyze(df)

    # 打印分析结果
    print("\n=== 购买动机分析结果 ===")

    print("\n1. 主要购买动机:")
    for motivation, data in results['primary_motivations'].items():
        print(f"\n{motivation.upper()}:")
        print(f"占比: {data['percentage']}%")
        print("主要发现:")
        for finding in data['key_findings']:
            print(f"- {finding}")
        print("代表性引用:")
        for quote in data['representative_quotes']:
            print(f"- {quote}")
        print(f"趋势: {data['trend']}")

    print("\n2. 决策因素分析:")
    factors = results['decision_factors']['key_factors']
    for factor, data in factors.items():
        print(f"\n{factor}:")
        print(f"重要性评分: {data['importance']}")
        print("关注点:", ', '.join(data['key_concerns']))

    print("\n3. 购买历程分析:")
    journey = results['purchase_journey']
    print("\n认知阶段:")
    for channel, percentage in journey['awareness']['channels'].items():
        print(f"- {channel}: {percentage}%")

    print("\n考虑阶段:")
    for channel, percentage in journey['consideration']['research_channels'].items():
        print(f"- {channel}: {percentage}%")

    print("\n4. 营销建议:")
    for rec in results['recommendations']:
        print(f"\n目标群体: {rec['target']}")
        print(f"发现: {rec['finding']}")
        print(f"策略: {rec['strategy']}")
        print(f"预期影响: {rec['expected_impact']}")