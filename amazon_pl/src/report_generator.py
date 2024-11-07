"""
报告生成器
功能：生成分析报告，包括文本报告和Excel报表
"""
import pandas as pd
from typing import Dict, List, Any
import os
from datetime import datetime


class ReportGenerator:
    def __init__(self):
        """初始化报告生成器"""
        self.output_dir = 'reports'
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_text_report(self, analysis_results: Dict) -> str:
        """生成文本格式的分析报告"""
        report = []

        # 1. 基础信息
        report.append("=== 亚马逊评论分析报告 ===")
        report.append("\n1. 基础信息:")
        metadata = analysis_results.get('metadata', {})
        report.append(f"总评论数: {metadata.get('total_reviews', 0)}")
        report.append(f"分析时间: {metadata.get('timestamp', '')}")
        report.append(f"分析可信度: {metadata.get('confidence_score', 0):.2f}")

        # 2. 用户维度分析
        report.append("\n2. 用户维度分析:")

        # 2.1 用户特征
        report.append("\n2.1 用户特征:")
        user_features = analysis_results.get('user_features', {})
        for feature, data in user_features.items():
            report.append(f"\n{feature.upper()}:")
            report.append(f"提及次数: {data.get('mention_count', 0)}")
            report.append(f"占比: {data.get('percentage', 0)}%")
            if 'characteristics' in data:
                report.append("主要特征:")
                for char in data['characteristics']:
                    report.append(f"- {char}")
            if 'representative_comments' in data:
                report.append("代表性评论:")
                for comment in data['representative_comments'][:2]:
                    report.append(f"- {comment}")

        # 2.2 使用目的
        report.append("\n2.2 使用目的:")
        purposes = analysis_results.get('purposes', {})
        for purpose, data in purposes.items():
            report.append(f"\n{purpose.upper()}:")
            report.append(f"提及次数: {data.get('mention_count', 0)}")
            report.append(f"占比: {data.get('percentage', 0)}%")
            if 'key_points' in data:
                report.append("主要观点:")
                for point in data['key_points']:
                    report.append(f"- {point}")

        # 2.3 使用场景
        report.append("\n2.3 使用场景:")
        scenarios = analysis_results.get('scenarios', {})
        for scenario, data in scenarios.items():
            report.append(f"\n{scenario.upper()}:")
            report.append(f"提及次数: {data.get('mention_count', 0)}")
            report.append(f"占比: {data.get('percentage', 0)}%")
            if 'descriptions' in data:
                report.append("场景描述:")
                for desc in data['descriptions']:
                    report.append(f"- {desc}")

        # 3. 时空维度分析
        report.append("\n3. 时空维度分析:")

        # 3.1 使用时间
        report.append("\n3.1 使用时间:")
        timing = analysis_results.get('timing', {})
        for time_type, data in timing.items():
            report.append(f"\n{time_type.upper()}:")
            report.append(f"提及次数: {data.get('mention_count', 0)}")
            report.append(f"占比: {data.get('percentage', 0)}%")
            if 'patterns' in data:
                report.append("时间模式:")
                for pattern in data['patterns']:
                    report.append(f"- {pattern}")

        # 3.2 使用地点
        report.append("\n3.2 使用地点:")
        locations = analysis_results.get('locations', {})
        for location, data in locations.items():
            report.append(f"\n{location.upper()}:")
            report.append(f"提及次数: {data.get('mention_count', 0)}")
            report.append(f"占比: {data.get('percentage', 0)}%")
            if 'characteristics' in data:
                report.append("地点特征:")
                for char in data['characteristics']:
                    report.append(f"- {char}")

        # 4. 产品维度分析
        report.append("\n4. 产品维度分析:")

        # 4.1 购买动机
        report.append("\n4.1 购买动机:")
        motivations = analysis_results.get('motivations', {})
        for motivation, data in motivations.items():
            report.append(f"\n{motivation.upper()}:")
            report.append(f"提及次数: {data.get('mention_count', 0)}")
            report.append(f"占比: {data.get('percentage', 0)}%")
            if 'key_findings' in data:
                report.append("主要发现:")
                for finding in data['key_findings']:
                    report.append(f"- {finding}")

        # 4.2 使用体验
        report.append("\n4.2 使用体验:")
        experiences = analysis_results.get('experiences', {})
        for exp_type, data in experiences.items():
            report.append(f"\n{exp_type.upper()}:")
            report.append(f"提及次数: {data.get('mention_count', 0)}")
            report.append(f"满意度: {data.get('satisfaction_score', 0):.2f}")
            if 'key_feedback' in data:
                report.append("主要反馈:")
                for feedback in data['key_feedback']:
                    report.append(f"- {feedback}")

        # 4.3 设计期望
        report.append("\n4.3 设计期望:")
        expectations = analysis_results.get('design_expectations', {})
        for exp_type, data in expectations.items():
            report.append(f"\n{exp_type.upper()}:")
            report.append(f"提及次数: {data.get('mention_count', 0)}")
            report.append(f"优先级: {data.get('priority', 0)}")
            if 'suggestions' in data:
                report.append("改进建议:")
                for suggestion in data['suggestions']:
                    report.append(f"- {suggestion}")

        # 5. 情感分析
        report.append("\n5. 情感分析:")
        sentiment = analysis_results.get('sentiment', {})

        # 5.1 整体情感倾向
        report.append("\n5.1 整体情感倾向:")
        overall = sentiment.get('overall', {})
        report.append(f"正面评价: {overall.get('positive', 0)}%")
        report.append(f"中性评价: {overall.get('neutral', 0)}%")
        report.append(f"负面评价: {overall.get('negative', 0)}%")

        # 5.2 各维度情感分布
        report.append("\n5.2 各维度情感分布:")
        dimensions = sentiment.get('dimensions', {})
        for dim, scores in dimensions.items():
            report.append(f"\n{dim}:")
            report.append(f"情感得分: {scores.get('score', 0):.2f}")
            report.append(f"正面占比: {scores.get('positive', 0)}%")
            report.append(f"负面占比: {scores.get('negative', 0)}%")

        # 5.3 关键词情感分析
        report.append("\n5.3 关键词情感分析:")
        keywords = sentiment.get('keywords', {})
        for keyword, data in keywords.items():
            report.append(f"\n{keyword}:")
            report.append(f"情感倾向: {data.get('sentiment', '')}")
            report.append(f"提及次数: {data.get('count', 0)}")

        # 6. 改进建议
        report.append("\n6. 改进建议:")
        recommendations = analysis_results.get('recommendations', {})

        # 6.1 用户群体建议
        report.append("\n6.1 用户群体建议:")
        for user_group, recs in recommendations.get('user_groups', {}).items():
            report.append(f"\n目标群体: {user_group}")
            report.append(f"发现: {recs.get('finding', '')}")
            report.append(f"建议: {recs.get('suggestion', '')}")
            report.append(f"优先级: {recs.get('priority', '')}")

        # 6.2 产品功能建议
        report.append("\n6.2 产品功能建议:")
        for feature, recs in recommendations.get('features', {}).items():
            report.append(f"\n功能: {feature}")
            report.append(f"问题: {recs.get('issue', '')}")
            report.append(f"建议: {recs.get('suggestion', '')}")
            report.append(f"优先级: {recs.get('priority', '')}")

        # 6.3 设计改进建议
        report.append("\n6.3 设计改进建议:")
        for design, recs in recommendations.get('design', {}).items():
            report.append(f"\n设计方面: {design}")
            report.append(f"现状: {recs.get('current_state', '')}")
            report.append(f"建议: {recs.get('suggestion', '')}")
            report.append(f"优先级: {recs.get('priority', '')}")

        # 6.4 营销策略建议
        report.append("\n6.4 营销策略建议:")
        for strategy, recs in recommendations.get('marketing', {}).items():
            report.append(f"\n策略方向: {strategy}")
            report.append(f"机会点: {recs.get('opportunity', '')}")
            report.append(f"建议: {recs.get('suggestion', '')}")
            report.append(f"预期效果: {recs.get('expected_impact', '')}")

        return '\n'.join(report)

    def generate_excel_report(
            self,
            analysis_results: Dict[str, Any],
            output_name: str = None
    ) -> str:
        """生成Excel格式的分析报告"""
        if output_name is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_name = f'analysis_report_{timestamp}'

        excel_path = os.path.join(self.output_dir, f'{output_name}.xlsx')

        with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
            # 首先生成分析维度统计表
            self._generate_analysis_dimension_sheet(writer, analysis_results)

            # 生成其他sheet
            self._generate_summary_sheet(writer, analysis_results)
            self._generate_user_dimension_sheet(writer, analysis_results)
            self._generate_time_space_sheet(writer, analysis_results)
            self._generate_product_dimension_sheet(writer, analysis_results)
            self._generate_sentiment_sheet(writer, analysis_results)
            self._generate_recommendations_sheet(writer, analysis_results)

        return excel_path

    def _generate_summary_sheet(self, writer: pd.ExcelWriter, analysis_results: Dict):
        """生成概述sheet"""
        metadata = analysis_results.get('metadata', {})
        summary_data = {
            '分析维度': ['基础信息', '用户维度', '时空维度', '产品维度', '情感分析'],
            '样本数量': [
                metadata.get('total_reviews', 0),
                len(analysis_results.get('user_features', {})),
                len(analysis_results.get('timing', {})) + len(analysis_results.get('locations', {})),
                len(analysis_results.get('motivations', {})) + len(analysis_results.get('experiences', {})),
                len(analysis_results.get('sentiment', {}).get('keywords', {}))
            ],
            '可信度': [
                metadata.get('confidence_score', 0),
                metadata.get('user_dimension_confidence', 0),
                metadata.get('time_space_confidence', 0),
                metadata.get('product_dimension_confidence', 0),
                metadata.get('sentiment_confidence', 0)
            ]
        }

        pd.DataFrame(summary_data).to_excel(writer, sheet_name='概述', index=False)

    def _generate_user_dimension_sheet(self, writer: pd.ExcelWriter, analysis_results: Dict):
        """生成用户维度sheet"""
        # 用户特征
        user_features_data = []
        for feature, data in analysis_results.get('user_features', {}).items():
            user_features_data.append({
                '特征类型': feature,
                '提及次数': data.get('mention_count', 0),
                '占比': f"{data.get('percentage', 0)}%",
                '主要特征': '\n'.join(data.get('characteristics', [])),
                '代表性评论': '\n'.join(data.get('representative_comments', [])[:2])
            })

        # 使用目的
        purposes_data = []
        for purpose, data in analysis_results.get('purposes', {}).items():
            purposes_data.append({
                '目的类型': purpose,
                '提及次数': data.get('mention_count', 0),
                '占比': f"{data.get('percentage', 0)}%",
                '主要观点': '\n'.join(data.get('key_points', []))
            })

        # 使用场景
        scenarios_data = []
        for scenario, data in analysis_results.get('scenarios', {}).items():
            scenarios_data.append({
                '场景类型': scenario,
                '提及次数': data.get('mention_count', 0),
                '占比': f"{data.get('percentage', 0)}%",
                '场景描述': '\n'.join(data.get('descriptions', []))
            })

        # 写入Excel
        pd.DataFrame(user_features_data).to_excel(writer, sheet_name='用户特征', index=False)
        pd.DataFrame(purposes_data).to_excel(writer, sheet_name='使用目的', index=False)
        pd.DataFrame(scenarios_data).to_excel(writer, sheet_name='使用场景', index=False)

    def _generate_time_space_sheet(self, writer: pd.ExcelWriter, analysis_results: Dict):
        """生成时空维度sheet"""
        # 使用时间
        timing_data = []
        for time_type, data in analysis_results.get('timing', {}).items():
            timing_data.append({
                '时间类型': time_type,
                '提及次数': data.get('mention_count', 0),
                '占比': f"{data.get('percentage', 0)}%",
                '时间模式': '\n'.join(data.get('patterns', []))
            })

        # 使用地点
        location_data = []
        for location, data in analysis_results.get('locations', {}).items():
            location_data.append({
                '地点类型': location,
                '提及次数': data.get('mention_count', 0),
                '占比': f"{data.get('percentage', 0)}%",
                '地点特征': '\n'.join(data.get('characteristics', []))
            })

        # 写入Excel
        pd.DataFrame(timing_data).to_excel(writer, sheet_name='使用时间', index=False)
        pd.DataFrame(location_data).to_excel(writer, sheet_name='使用地点', index=False)

    def _generate_product_dimension_sheet(self, writer: pd.ExcelWriter, analysis_results: Dict):
        """生成产品维度sheet"""
        # 购买动机
        motivation_data = []
        for motivation, data in analysis_results.get('motivations', {}).items():
            motivation_data.append({
                '动机类型': motivation,
                '提及次数': data.get('mention_count', 0),
                '占比': f"{data.get('percentage', 0)}%",
                '主要发现': '\n'.join(data.get('key_findings', []))
            })

        # 使用体验
        experience_data = []
        for exp_type, data in analysis_results.get('experiences', {}).items():
            experience_data.append({
                '体验类型': exp_type,
                '提及次数': data.get('mention_count', 0),
                '满意度': data.get('satisfaction_score', 0),
                '主要反馈': '\n'.join(data.get('key_feedback', []))
            })

        # 设计期望
        expectation_data = []
        for exp_type, data in analysis_results.get('design_expectations', {}).items():
            expectation_data.append({
                '期望类型': exp_type,
                '提及次数': data.get('mention_count', 0),
                '优先级': data.get('priority', 0),
                '改进建议': '\n'.join(data.get('suggestions', []))
            })

        # 写入Excel
        pd.DataFrame(motivation_data).to_excel(writer, sheet_name='购买动机', index=False)
        pd.DataFrame(experience_data).to_excel(writer, sheet_name='使用体验', index=False)
        pd.DataFrame(expectation_data).to_excel(writer, sheet_name='设计期望', index=False)

    def _generate_sentiment_sheet(self, writer: pd.ExcelWriter, analysis_results: Dict):
        """生成情感分析sheet"""
        sentiment = analysis_results.get('sentiment', {})

        # 整体情感
        overall_sentiment = sentiment.get('overall', {})
        overall_data = [{
            '评价类型': '正面评价',
            '占比': f"{overall_sentiment.get('positive', 0)}%"
        }, {
            '评价类型': '中性评价',
            '占比': f"{overall_sentiment.get('neutral', 0)}%"
        }, {
            '评价类型': '负面评价',
            '占比': f"{overall_sentiment.get('negative', 0)}%"
        }]

        # 维度情感
        dimension_sentiment = []
        for dim, scores in sentiment.get('dimensions', {}).items():
            dimension_sentiment.append({
                '维度': dim,
                '情感得分': scores.get('score', 0),
                '正面占比': f"{scores.get('positive', 0)}%",
                '负面占比': f"{scores.get('negative', 0)}%"
            })

        # 关键词情感
        keyword_sentiment = []
        for keyword, data in sentiment.get('keywords', {}).items():
            keyword_sentiment.append({
                '关键词': keyword,
                '情感倾向': data.get('sentiment', ''),
                '提及次数': data.get('count', 0)
            })

        # 写入Excel
        pd.DataFrame(overall_data).to_excel(writer, sheet_name='整体情感', index=False)
        pd.DataFrame(dimension_sentiment).to_excel(writer, sheet_name='维度情感', index=False)
        pd.DataFrame(keyword_sentiment).to_excel(writer, sheet_name='关键词情感', index=False)

    def _generate_analysis_dimension_sheet(self, writer: pd.ExcelWriter, analysis_results: Dict):
        """生成分析维度统计sheet"""
        # 准备维度统计数据
        dimension_stats = []

        # 基础维度统计
        dimensions = {
            '用户维度': analysis_results.get('user_analysis', {}),
            '时空维度': analysis_results.get('timing', {}),
            '场景维度': analysis_results.get('scenarios', {}),
            '目的维度': analysis_results.get('purposes', {}),
            '动机维度': analysis_results.get('motivations', {}),
            '体验维度': analysis_results.get('experiences', {}),
            '期望维度': analysis_results.get('design_expectations', {})
        }

        for dimension_name, data in dimensions.items():
            # 计算样本数和可信度
            total_mentions = sum(
                item.get('mention_count', 0)
                for item in data.values()
                if isinstance(item, dict)
            )

            # 计算维度得分
            dimension_score = sum(
                item.get('score', 0)
                for item in data.values()
                if isinstance(item, dict)
            ) / len(data) if data else 0

            dimension_stats.append({
                '分析维度': dimension_name,
                '样本数量': total_mentions,
                '可信度': round(min(total_mentions / 100, 1), 2) if total_mentions > 0 else 0
            })

        # 写入Excel
        df = pd.DataFrame(dimension_stats)
        df.to_excel(writer, sheet_name='分析维度', index=False)

    def _generate_recommendations_sheet(self, writer: pd.ExcelWriter, analysis_results: Dict):
        """生成改进建议sheet"""
        recommendations = analysis_results.get('recommendations', {})

        # 用户群体建议
        user_recommendations = []
        for user_group, recs in recommendations.get('user_groups', {}).items():
            user_recommendations.append({
                '目标群体': user_group,
                '发现': recs.get('finding', ''),
                '建议': recs.get('suggestion', ''),
                '优先级': recs.get('priority', '')
            })

        # 产品功能建议
        feature_recommendations = []
        for feature, recs in recommendations.get('features', {}).items():
            feature_recommendations.append({
                '功能': feature,
                '问题': recs.get('issue', ''),
                '建议': recs.get('suggestion', ''),
                '优先级': recs.get('priority', '')
            })

        # 设计改进建议
        design_recommendations = []
        for design, recs in recommendations.get('design', {}).items():
            design_recommendations.append({
                '设计方面': design,
                '现状': recs.get('current_state', ''),
                '建议': recs.get('suggestion', ''),
                '优先级': recs.get('priority', '')
            })

        # 营销策略建议
        marketing_recommendations = []
        for strategy, recs in recommendations.get('marketing', {}).items():
            marketing_recommendations.append({
                '策略方向': strategy,
                '机会点': recs.get('opportunity', ''),
                '建议': recs.get('suggestion', ''),
                '预期效果': recs.get('expected_impact', '')
            })

        # 写入Excel
        pd.DataFrame(user_recommendations).to_excel(writer, sheet_name='用户群体建议', index=False)
        pd.DataFrame(feature_recommendations).to_excel(writer, sheet_name='产品功能建议', index=False)
        pd.DataFrame(design_recommendations).to_excel(writer, sheet_name='设计改进建议', index=False)
        pd.DataFrame(marketing_recommendations).to_excel(writer, sheet_name='营销策略建议', index=False)

    def generate_report(self, analysis_results: Dict, insights: Dict, output_name: str = None) -> str:
        """
        生成完整的分析报告，包括文本报告和Excel报告

        参数:
            analysis_results: 分析结果
            insights: 洞察结果
            output_name: 输出文件名（可选）
        返回:
            str: Excel报告的文件路径
        """
        # 合并分析结果和洞察
        full_results = {
            **analysis_results,
            'insights': insights
        }

        # 生成文本报告
        text_report = self.generate_text_report(full_results)

        # 保存文本报告
        if output_name is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_name = f'analysis_report_{timestamp}'

        text_path = os.path.join(self.output_dir, f'{output_name}.txt')
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(text_report)

        # 生成Excel报告
        excel_path = self.generate_excel_report(full_results, output_name)

        return excel_path
