from django.urls import path
from . import views

# アプリ名（URL逆引き用）
app_name = 'myapp'

# =====================
# アプリ内URLパターン定義
# =====================
urlpatterns = [
    # ダッシュボード（トップページ）
    path('', views.dashboard, name='dashboard'),
    
    # 日記関連
    path('diary/', views.diary_list, name='diary_list'),  # 日記一覧
    path('diary/<int:diary_id>/', views.diary_detail, name='diary_detail'),  # 日記詳細
    path('diary/create/', views.diary_create, name='diary_create'),  # 日記作成
    
    # 行動ログ関連
    path('actions/', views.action_log_list, name='action_log_list'),  # 行動ログ一覧
    path('actions/create/', views.action_log_create, name='action_log_create'),  # 行動ログ作成
    path('actions/<int:action_id>/edit/', views.action_log_edit, name='action_log_edit'),  # 行動ログ編集
    
    # 目標関連
    path('goals/', views.goal_list, name='goal_list'),  # 目標一覧
    path('goals/create/', views.goal_create, name='goal_create'),  # 目標作成
    path('goals/<int:goal_id>/edit/', views.goal_edit, name='goal_edit'),  # 目標編集
    
    # AI提案関連
    path('ai-recommendations/', views.ai_recommendations, name='ai_recommendations'),  # AI提案一覧
    path('ai-recommendations/<int:recommendation_id>/', views.ai_recommendation_detail, name='ai_recommendation_detail'),  # AI提案詳細
    
    # 分析・統計
    path('analytics/', views.analytics, name='analytics'),  # 分析・統計ページ
    
    # プロフィール
    path('profile/', views.profile, name='profile'),  # プロフィール設定
]
