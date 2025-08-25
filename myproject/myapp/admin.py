from django.contrib import admin
from .models import (
    HabitCategory, DailyDiary, ActionLog, Goal, 
    AIRecommendation, UserProfile
)

# =====================
# 管理画面：習慣カテゴリ
# =====================
@admin.register(HabitCategory)
class HabitCategoryAdmin(admin.ModelAdmin):
    # 一覧表示項目
    list_display = ['name', 'description', 'color', 'created_at']
    # 検索対象
    search_fields = ['name', 'description']
    # フィルタ項目
    list_filter = ['created_at']

# =====================
# 管理画面：日記
# =====================
@admin.register(DailyDiary)
class DailyDiaryAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'mood_score', 'energy_level', 'created_at']
    list_filter = ['date', 'mood_score', 'energy_level', 'created_at']
    search_fields = ['user__username', 'content']
    date_hierarchy = 'date'  # 日付階層ナビ

# =====================
# 管理画面：行動ログ
# =====================
@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'action_name', 'duration_minutes', 'completed', 'date']
    list_filter = ['category', 'completed', 'date', 'created_at']
    search_fields = ['user__username', 'action_name', 'notes']
    date_hierarchy = 'date'

# =====================
# 管理画面：目標
# =====================
@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'category', 'target_date', 'status', 'priority', 'created_at']
    list_filter = ['status', 'priority', 'category', 'target_date', 'created_at']
    search_fields = ['user__username', 'title', 'description']
    date_hierarchy = 'target_date'

# =====================
# 管理画面：AI提案
# =====================
@admin.register(AIRecommendation)
class AIRecommendationAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'recommendation_type', 'title', 'priority', 'is_implemented', 'feedback_rating']
    list_filter = ['recommendation_type', 'priority', 'is_implemented', 'date', 'created_at']
    search_fields = ['user__username', 'title', 'content']
    date_hierarchy = 'date'

# =====================
# 管理画面：ユーザープロフィール
# =====================
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'ai_feedback_frequency', 'notification_enabled', 'created_at']
    list_filter = ['ai_feedback_frequency', 'notification_enabled', 'created_at']
    search_fields = ['user__username', 'bio']
    filter_horizontal = ['preferred_categories']  # 多対多カテゴリを横並びUIで選択可
