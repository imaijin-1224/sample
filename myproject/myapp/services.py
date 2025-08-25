from datetime import date, timedelta
from django.utils import timezone
from django.db import models
from .models import DailyDiary, ActionLog, Goal, AIRecommendation, HabitCategory
import random

# =====================
# AI習慣コーチのロジックをまとめたサービスクラス
# =====================
class AIHabitCoach:
    """
    AI習慣コーチサービス。
    ユーザーの行動・日記データからAI提案や振り返り、モチベーションメッセージを生成。
    """
    
    def __init__(self, user):
        self.user = user  # 対象ユーザー
    
    def generate_daily_recommendation(self, target_date=None):
        """
        日次目標のAI提案を生成（既存があれば再利用）。
        気分・エネルギー・行動傾向を分析し、今日の目標を提案。
        """
        if target_date is None:
            target_date = date.today()
        
        # 既存の提案があれば再利用
        existing = AIRecommendation.objects.filter(
            user=self.user,
            date=target_date,
            recommendation_type='daily_goal'
        ).first()
        
        if existing:
            return existing
        
        # 過去1週間分の日記・行動を分析
        past_week = target_date - timedelta(days=7)
        recent_diaries = DailyDiary.objects.filter(
            user=self.user,
            date__gte=past_week,
            date__lt=target_date
        ).order_by('-date')
        
        recent_actions = ActionLog.objects.filter(
            user=self.user,
            date__gte=past_week,
            date__lt=target_date
        ).order_by('-date')
        
        # 気分・エネルギーの平均値を算出
        avg_mood = recent_diaries.aggregate(avg=models.Avg('mood_score'))['avg'] or 5
        avg_energy = recent_diaries.aggregate(avg=models.Avg('energy_level'))['avg'] or 5
        
        # よく行っている行動カテゴリを集計
        action_frequency = {}
        for action in recent_actions:
            category = action.category.name
            if category not in action_frequency:
                action_frequency[category] = 0
            action_frequency[category] += 1
        
        # 提案を生成
        recommendation = self._create_recommendation(
            target_date, avg_mood, avg_energy, action_frequency
        )
        
        return recommendation
    
    def _create_recommendation(self, target_date, avg_mood, avg_energy, action_frequency):
        """
        気分・エネルギー・行動傾向に基づき、具体的な提案内容を生成
        """
        # 気分・エネルギーの状態で分岐
        if avg_mood < 5:
            if avg_energy < 5:
                title = "心と体を癒す小さな一歩"
                content = "今日は無理をせず、心と体を労わる時間を作りましょう。"
                action_items = [
                    "10分間の深呼吸や瞑想",
                    "お気に入りの音楽を聴く",
                    "軽い散歩（15分程度）"
                ]
            else:
                title = "気分を上げる活動を"
                content = "エネルギーはあるので、楽しいことをして気分を改善しましょう。"
                action_items = [
                    "好きな趣味に没頭する",
                    "友達と連絡を取る",
                    "新しいレシピに挑戦"
                ]
        else:
            if avg_energy < 5:
                title = "エネルギーを蓄える日"
                content = "気分は良いので、無理せずエネルギーを回復させましょう。"
                action_items = [
                    "十分な睡眠を取る",
                    "栄養のある食事を心がける",
                    "リラックスできる時間を作る"
                ]
            else:
                title = "理想的な状態を活かそう"
                content = "気分もエネルギーも良い状態です。目標に向かって進みましょう。"
                action_items = [
                    "重要なタスクに集中",
                    "新しい習慣を始める",
                    "長期的な目標の計画を立てる"
                ]
        
        # 行動頻度が高いカテゴリがあれば追加提案
        if action_frequency:
            most_frequent = max(action_frequency.items(), key=lambda x: x[1])
            if most_frequent[1] >= 3:
                title += f" - {most_frequent[0]}の継続を"
                content += f"\n\n{most_frequent[0]}の習慣が定着しつつあります。今日も継続しましょう。"
                action_items.append(f"{most_frequent[0]}の活動を15分以上行う")
        
        # 提案をDBに保存
        recommendation = AIRecommendation.objects.create(
            user=self.user,
            date=target_date,
            recommendation_type='daily_goal',
            title=title,
            content=content,
            reasoning=f"過去1週間の気分スコア平均: {avg_mood:.1f}, エネルギーレベル平均: {avg_energy:.1f}",
            action_items=action_items,
            priority='medium'
        )
        
        return recommendation
    
    def generate_weekly_reflection(self, target_date=None):
        """
        週次振り返りのAI提案を生成（既存があれば再利用）。
        1週間の行動・日記データから達成率や傾向を分析。
        """
        if target_date is None:
            target_date = date.today()
        
        # 既存の提案があれば再利用
        existing = AIRecommendation.objects.filter(
            user=self.user,
            date=target_date,
            recommendation_type='reflection'
        ).first()
        
        if existing:
            return existing
        
        # 過去1週間分のデータを分析
        past_week = target_date - timedelta(days=7)
        weekly_diaries = DailyDiary.objects.filter(
            user=self.user,
            date__gte=past_week,
            date__lt=target_date
        ).order_by('date')
        
        weekly_actions = ActionLog.objects.filter(
            user=self.user,
            date__gte=past_week,
            date__lt=target_date
        ).order_by('date')
        
        # 行動達成率を計算
        total_actions = weekly_actions.count()
        completed_actions = weekly_actions.filter(completed=True).count()
        completion_rate = (completed_actions / total_actions * 100) if total_actions > 0 else 0
        
        # 気分の変化傾向を分析
        mood_trend = "安定" if len(weekly_diaries) >= 2 else "データ不足"
        if len(weekly_diaries) >= 2:
            first_mood = weekly_diaries.first().mood_score
            last_mood = weekly_diaries.last().mood_score
            if last_mood > first_mood + 1:
                mood_trend = "改善"
            elif last_mood < first_mood - 1:
                mood_trend = "低下"
        
        # 振り返り内容を生成
        if completion_rate >= 80:
            title = "素晴らしい1週間でした！"
            content = f"目標達成率{completion_rate:.1f}%と高い成果を上げています。"
            action_items = [
                "来週も同じペースを維持",
                "さらに高い目標に挑戦",
                "成功の要因を分析して記録"
            ]
        elif completion_rate >= 50:
            title = "良いペースで進んでいます"
            content = f"目標達成率{completion_rate:.1f}%と着実に進歩しています。"
            action_items = [
                "達成できなかった理由を分析",
                "来週の目標を少し調整",
                "成功した習慣を強化"
            ]
        else:
            title = "来週に向けて調整しましょう"
            content = f"目標達成率{completion_rate:.1f}%と課題がありますが、改善の余地があります。"
            action_items = [
                "目標を現実的なレベルに調整",
                "習慣化のルーティンを改善",
                "小さな成功から始める"
            ]
        
        content += f"\n\n気分の傾向: {mood_trend}\n総行動数: {total_actions}件\n完了率: {completion_rate:.1f}%"
        
        # 提案をDBに保存
        recommendation = AIRecommendation.objects.create(
            user=self.user,
            date=target_date,
            recommendation_type='reflection',
            title=title,
            content=content,
            reasoning=f"週次データ分析: 完了率{completion_rate:.1f}%, 気分傾向{mood_trend}",
            action_items=action_items,
            priority='high'
        )
        
        return recommendation
    
    def get_motivational_message(self):
        """
        モチベーション向上メッセージをランダムで取得
        """
        messages = [
            "今日の小さな一歩が、明日の大きな変化につながります。",
            "習慣は第二の天性。継続は力なりです。",
            "完璧を求めず、進歩を求めましょう。",
            "あなたの努力は必ず実を結びます。",
            "今日も自分らしく、一歩ずつ前進しましょう。",
            "習慣の力で、理想の自分に近づけます。",
            "小さな習慣が、人生を変える大きな力になります。",
            "今日の選択が、明日のあなたを作ります。"
        ]
        
        return random.choice(messages)
