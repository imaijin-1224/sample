from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Count, Sum, Avg, IntegerField
from datetime import date, timedelta
from .models import (
    DailyDiary, ActionLog, Goal, AIRecommendation, 
    HabitCategory, UserProfile
)
from .services import AIHabitCoach
from .forms import DailyDiaryForm, ActionLogForm, GoalForm
from django.db.models.functions import Cast
# =====================
# ダッシュボード（メイン画面）
# =====================
@login_required
def dashboard(request):
    """
    メインダッシュボード。
    今日の日記・行動・AI提案・モチベーション・統計などを表示。
    """
    today = date.today()
    
    # 今日の日記を取得
    today_diary = DailyDiary.objects.filter(
        user=request.user, 
        date=today
    ).first()
    
    # 今日の行動ログを取得
    today_actions = ActionLog.objects.filter(
        user=request.user, 
        date=today
    ).order_by('-created_at')
    
    # 今日のAI提案（なければ生成）
    ai_coach = AIHabitCoach(request.user)
    today_recommendation = ai_coach.generate_daily_recommendation(today)
    
    # 週次振り返り（日曜のみ）
    weekly_reflection = None
    if today.weekday() == 6:  # 日曜
        weekly_reflection = ai_coach.generate_weekly_reflection(today)
    
    # 最近1週間分の日記（気分・エネルギー推移）
    past_week = today - timedelta(days=7)
    recent_diaries = DailyDiary.objects.filter(
        user=request.user,
        date__gte=past_week,
        date__lte=today
    ).order_by('date')
    
    # 習慣カテゴリ別の行動統計
    category_stats = ActionLog.objects.filter(
        user=request.user,
        date__gte=past_week,
        date__lte=today
    ).values('category__name').annotate(
        total_actions=Count('id'),
        completed_actions=Count('id', filter=Q(completed=True))
    )
    
    # モチベーションメッセージ（AIから）
    motivational_message = ai_coach.get_motivational_message()
    
    context = {
        'today_diary': today_diary,
        'today_actions': today_actions,
        'today_recommendation': today_recommendation,
        'weekly_reflection': weekly_reflection,
        'recent_diaries': recent_diaries,
        'category_stats': category_stats,
        'motivational_message': motivational_message,
        'today': today,
    }
    
    return render(request, 'myapp/dashboard.html', context)

# =====================
# 日記関連
# =====================
@login_required
def diary_list(request):
    """
    日記一覧ページ。ユーザーの日記を新しい順で表示。
    """
    diaries = DailyDiary.objects.filter(
        user=request.user
    ).order_by('-date')
    
    return render(request, 'myapp/diary_list.html', {'diaries': diaries})

@login_required
def diary_detail(request, diary_id):
    """
    日記詳細ページ。指定IDの日記を表示。
    """
    diary = get_object_or_404(DailyDiary, id=diary_id, user=request.user)
    return render(request, 'myapp/diary_detail.html', {'diary': diary})

@login_required
def diary_create(request):
    """
    今日の日記を新規作成または編集。
    既にあれば編集フォーム、なければ新規作成フォーム。
    """
    today = date.today()
    diary, created = DailyDiary.objects.get_or_create(
        user=request.user,
        date=today,
        defaults={
            'mood_score': 5,
            'energy_level': 5,
            'content': '',
            'gratitude': ''
        }
    )
    
    if request.method == 'POST':
        form = DailyDiaryForm(request.POST, instance=diary)
        if form.is_valid():
            form.save()
            messages.success(request, '日記を保存しました。')
            return redirect('myapp:dashboard')
    else:
        form = DailyDiaryForm(instance=diary)
    
    return render(request, 'myapp/diary_form.html', {
        'form': form, 
        'diary': diary,
        'is_edit': not created
    })

# =====================
# 行動ログ関連
# =====================
@login_required
def action_log_list(request):
    """
    行動ログ一覧ページ。カテゴリ・日付でフィルタ可能。
    """
    actions = ActionLog.objects.filter(
        user=request.user
    ).order_by('-date', '-created_at')
    

    # カテゴリでフィルタ
    category_filter = request.GET.get('category')
    if category_filter:
        actions = actions.filter(category__name=category_filter)
    
    # 日付でフィルタ
    date_filter = request.GET.get('date')
    if date_filter:
        try:
            filter_date = date.fromisoformat(date_filter)
            actions = actions.filter(date=filter_date)
        except ValueError:
            pass
    
    # 合計時間
    qs = actions.annotate(
        duration_int=Cast('duration_minutes', IntegerField())
    )

    total_duration = qs.aggregate(total=Sum('duration_int'))['total'] or 0
   
    categories = HabitCategory.objects.all()
    
    return render(request, 'myapp/action_log_list.html', {
        'actions': actions,
        'categories': categories,
        'total_duration': total_duration,
    })

@login_required
def action_log_create(request):
    """
    行動ログ新規作成フォーム。
    """
    if request.method == 'POST':
        form = ActionLogForm(request.POST)
        if form.is_valid():
            action = form.save(commit=False)
            action.user = request.user
            action.save()
            messages.success(request, '行動ログを記録しました。')
            return redirect('myapp:action_log_list')
    else:
        form = ActionLogForm(initial={'date': date.today()})
    
    return render(request, 'myapp/action_log_form.html', {'form': form})

@login_required
def action_log_edit(request, action_id):
    """
    行動ログ編集フォーム。
    """
    action = get_object_or_404(ActionLog, id=action_id, user=request.user)
    
    if request.method == 'POST':
        form = ActionLogForm(request.POST, instance=action)
        if form.is_valid():
            form.save()
            messages.success(request, '行動ログを更新しました。')
            return redirect('myapp:action_log_list')
    else:
        form = ActionLogForm(instance=action)
    
    return render(request, 'myapp/action_log_form.html', {
        'form': form,
        'action': action,
        'is_edit': True
    })

# =====================
# 目標関連
# =====================
@login_required
def goal_list(request):
    """
    目標一覧ページ。ユーザーの目標を新しい順で表示。
    """
    goals = Goal.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    return render(request, 'myapp/goal_list.html', {'goals': goals})

@login_required
def goal_create(request):
    """
    目標新規作成フォーム。
    """
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, '目標を作成しました。')
            return redirect('myapp:goal_list')
    else:
        form = GoalForm()
    
    return render(request, 'myapp/goal_form.html', {'form': form})

@login_required
def goal_edit(request, goal_id):
    """
    目標編集フォーム。
    """
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    
    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, '目標を更新しました。')
            return redirect('myapp:goal_list')
    else:
        form = GoalForm(instance=goal)
    
    return render(request, 'myapp/goal_form.html', {
        'form': form,
        'goal': goal,
        'is_edit': True
    })

# =====================
# AI提案関連
# =====================
@login_required
def ai_recommendations(request):
    """
    AI提案一覧ページ。タイプでフィルタ可能。
    """
    recommendations = AIRecommendation.objects.filter(
        user=request.user
    ).order_by('-date', '-created_at')
    
    # タイプでフィルタ
    type_filter = request.GET.get('type')
    if type_filter:
        recommendations = recommendations.filter(recommendation_type=type_filter)
    
    return render(request, 'myapp/ai_recommendations.html', {
        'recommendations': recommendations
    })

@login_required
def ai_recommendation_detail(request, recommendation_id):
    """
    AI提案詳細ページ。評価・実装状況の更新も可能。
    """
    recommendation = get_object_or_404(
        AIRecommendation, 
        id=recommendation_id, 
        user=request.user
    )
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        if rating and rating.isdigit():
            recommendation.feedback_rating = int(rating)
            recommendation.save()
            messages.success(request, 'フィードバックを送信しました。')
            return redirect('myapp:ai_recommendation_detail', recommendation_id)
    
    return render(request, 'myapp/ai_recommendation_detail.html', {
        'recommendation': recommendation
    })

# =====================
# 分析・統計ページ
# =====================
@login_required
def analytics(request):
    """
    分析・統計ページ。気分・エネルギー・行動の推移やカテゴリ別統計を表示。
    """
    today = date.today()
    past_month = today - timedelta(days=30)
    
    # 直近30日分の日記・行動ログ
    monthly_diaries = DailyDiary.objects.filter(
        user=request.user,
        date__gte=past_month,
        date__lte=today
    )
    
    monthly_actions = ActionLog.objects.filter(
        user=request.user,
        date__gte=past_month,
        date__lte=today
    )
    
    # 気分・エネルギーの推移
    mood_trend = monthly_diaries.values('date').annotate(
        avg_mood=Avg('mood_score'),
        avg_energy=Avg('energy_level')
    ).order_by('date')
    
    # カテゴリ別の行動統計
    category_analytics = monthly_actions.values('category__name').annotate(
        total_actions=Count('id'),
        total_duration=Avg('duration_minutes'),
        completion_rate=Count('id', filter=Q(completed=True)) * 100.0 / Count('id')
    )
    
    # 週間ごとの習慣継続率
    weekly_completion = []
    for i in range(4):
        week_start = today - timedelta(days=7 * (i + 1))
        week_end = week_start + timedelta(days=6)
        week_actions = monthly_actions.filter(
            date__gte=week_start,
            date__lte=week_end
        )
        total = week_actions.count()
        completed = week_actions.filter(completed=True).count()
        rate = (completed / total * 100) if total > 0 else 0
        weekly_completion.append({
            'week': f"{week_start.strftime('%m/%d')} - {week_end.strftime('%m/%d')}",
            'rate': rate,
            'total': total
        })
    
    context = {
        'mood_trend': list(mood_trend),
        'category_analytics': list(category_analytics),
        'weekly_completion': weekly_completion,
        'total_diaries': monthly_diaries.count(),
        'total_actions': monthly_actions.count(),
        'avg_mood': monthly_diaries.aggregate(avg=Avg('mood_score'))['avg'] or 0,
        'avg_energy': monthly_diaries.aggregate(avg=Avg('energy_level'))['avg'] or 0,
    }
    
    return render(request, 'myapp/analytics.html', context)

# =====================
# プロフィールページ
# =====================
@login_required
def profile(request):
    """
    ユーザープロフィール設定ページ。
    AI提案頻度・通知・興味カテゴリなどを編集可能。
    """
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # プロフィール更新処理
        profile.bio = request.POST.get('bio', '')
        profile.notification_enabled = request.POST.get('notification_enabled') == 'on'
        profile.ai_feedback_frequency = request.POST.get('ai_feedback_frequency', 'daily')
        
        # 興味のあるカテゴリを更新
        selected_categories = request.POST.getlist('preferred_categories')
        profile.preferred_categories.set(selected_categories)
        
        profile.save()
        messages.success(request, 'プロフィールを更新しました。')
        return redirect('myapp:profile')
    
    categories = HabitCategory.objects.all()
    
    return render(request, 'myapp/profile.html', {
        'profile': profile,
        'categories': categories
    })
