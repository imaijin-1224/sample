from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json

# 習慣カテゴリを管理するモデル
class HabitCategory(models.Model):
    """
    習慣のカテゴリ（例：運動、学習、健康など）を管理
    """
    name = models.CharField(max_length=100, verbose_name="カテゴリ名")  # カテゴリ名
    description = models.TextField(blank=True, verbose_name="説明")      # カテゴリの説明
    color = models.CharField(max_length=7, default="#007bff", verbose_name="色")  # 表示用カラーコード
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")   # 作成日時
    
    class Meta:
        verbose_name = "習慣カテゴリ"
        verbose_name_plural = "習慣カテゴリ"
    
    def __str__(self):
        return self.name

# 日記（1日1件）を管理するモデル
class DailyDiary(models.Model):
    """
    日記モデル。ユーザーごと・日付ごとに1件。
    気分・エネルギー・内容・感謝などを記録。
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="ユーザー")  # 記録ユーザー
    date = models.DateField(default=timezone.now, verbose_name="日付")                 # 日付
    mood_score = models.IntegerField(choices=[(i, str(i)) for i in range(1, 11)], verbose_name="気分スコア")  # 1-10の気分
    energy_level = models.IntegerField(choices=[(i, str(i)) for i in range(1, 11)], verbose_name="エネルギーレベル")  # 1-10のエネルギー
    content = models.TextField(verbose_name="日記内容")                                # 日記本文
    gratitude = models.TextField(blank=True, verbose_name="感謝の気持ち")              # 感謝欄（任意）
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")      # 作成日時
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")          # 更新日時
    
    class Meta:
        verbose_name = "日記"
        verbose_name_plural = "日記"
        unique_together = ['user', 'date']  # 1ユーザー1日1件
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"

# 行動ログ（習慣の実行記録）を管理するモデル
class ActionLog(models.Model):
    """
    行動ログモデル。習慣カテゴリごとに、何を・どれくらい・完了したか等を記録。
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="ユーザー")  # 記録ユーザー
    category = models.ForeignKey(HabitCategory, on_delete=models.CASCADE, verbose_name="カテゴリ")  # 習慣カテゴリ
    action_name = models.CharField(max_length=200, verbose_name="行動名")              # 行動名（例：30分の散歩）
    duration_minutes = models.IntegerField(verbose_name="継続時間（分）")                # 実施時間（分）
    completed = models.BooleanField(default=True, verbose_name="完了")                  # 完了フラグ
    notes = models.TextField(blank=True, verbose_name="メモ")                          # メモ欄
    date = models.DateField(default=timezone.now, verbose_name="日付")                 # 実施日
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")      # 作成日時
    
    class Meta:
        verbose_name = "行動ログ"
        verbose_name_plural = "行動ログ"
    
    def __str__(self):
        return f"{self.user.username} - {self.action_name} ({self.date})"

# 目標（習慣化したいこと）を管理するモデル
class Goal(models.Model):
    """
    目標モデル。ユーザーごとに複数設定可能。
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="ユーザー")  # 記録ユーザー
    title = models.CharField(max_length=200, verbose_name="目標タイトル")               # 目標タイトル
    description = models.TextField(verbose_name="目標の詳細")                           # 目標の詳細
    category = models.ForeignKey(HabitCategory, on_delete=models.CASCADE, verbose_name="カテゴリ")  # 関連カテゴリ
    target_date = models.DateField(verbose_name="目標達成日")                           # 目標の期限
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', '進行中'),
            ('completed', '完了'),
            ('paused', '一時停止'),
            ('cancelled', 'キャンセル')
        ],
        default='active',
        verbose_name="ステータス"
    )
    priority = models.CharField(
        max_length=20,
        choices=[
            ('low', '低'),
            ('medium', '中'),
            ('high', '高')
        ],
        default='medium',
        verbose_name="優先度"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")      # 作成日時
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")          # 更新日時
    
    class Meta:
        verbose_name = "目標"
        verbose_name_plural = "目標"
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"

# AIによる提案（目標・振り返り・モチベーション等）を管理するモデル
class AIRecommendation(models.Model):
    """
    AI提案モデル。日次目標・週次振り返り・モチベーション等を記録。
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="ユーザー")  # 対象ユーザー
    date = models.DateField(default=timezone.now, verbose_name="提案日")               # 提案日
    recommendation_type = models.CharField(
        max_length=50,
        choices=[
            ('daily_goal', '日次目標'),
            ('habit_suggestion', '習慣提案'),
            ('motivation', 'モチベーション'),
            ('reflection', '振り返り')
        ],
        verbose_name="提案タイプ"
    )
    title = models.CharField(max_length=200, verbose_name="提案タイトル")               # 提案タイトル
    content = models.TextField(verbose_name="提案内容")                                # 提案本文
    reasoning = models.TextField(verbose_name="提案理由")                              # AIの根拠
    action_items = models.JSONField(default=list, verbose_name="具体的なアクション")    # アクションリスト
    priority = models.CharField(
        max_length=20,
        choices=[
            ('low', '低'),
            ('medium', '中'),
            ('high', '高')
        ],
        default='medium',
        verbose_name="優先度"
    )
    is_implemented = models.BooleanField(default=False, verbose_name="実装済み")        # 実装済みフラグ
    feedback_rating = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        null=True,
        blank=True,
        verbose_name="フィードバック評価"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")      # 作成日時
    
    class Meta:
        verbose_name = "AI提案"
        verbose_name_plural = "AI提案"
        unique_together = ['user', 'date', 'recommendation_type']  # 1日1タイプ1件
    
    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.date})"

# ユーザープロフィール（AI設定・通知・興味カテゴリ等）を管理するモデル
class UserProfile(models.Model):
    """
    ユーザープロフィールモデル。AIの提案頻度や通知設定、興味カテゴリなどを管理。
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="ユーザー")  # 対象ユーザー
    bio = models.TextField(blank=True, verbose_name="自己紹介")                          # 自己紹介
    preferred_categories = models.ManyToManyField(HabitCategory, blank=True, verbose_name="興味のあるカテゴリ")  # 興味カテゴリ
    notification_enabled = models.BooleanField(default=True, verbose_name="通知有効")     # 通知ON/OFF
    ai_feedback_frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', '毎日'),
            ('weekly', '週1回'),
            ('monthly', '月1回')
        ],
        default='daily',
        verbose_name="AIフィードバック頻度"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")      # 作成日時
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")          # 更新日時
    
    class Meta:
        verbose_name = "ユーザープロフィール"
        verbose_name_plural = "ユーザープロフィール"
    
    def __str__(self):
        return f"{self.user.username}のプロフィール"
