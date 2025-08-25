from django import forms
from .models import DailyDiary, ActionLog, Goal, HabitCategory

# =====================
# 日記フォーム
# =====================
class DailyDiaryForm(forms.ModelForm):
    """
    日記の作成・編集用フォーム。
    気分・エネルギー・内容・感謝を入力。
    """
    class Meta:
        model = DailyDiary
        fields = ['mood_score', 'energy_level', 'content', 'gratitude']
        widgets = {
            # 気分スコア（1-10）をセレクトボックスで表示
            'mood_score': forms.Select(
                choices=[(i, f"{i} - {'😢' if i <= 3 else '😐' if i <= 7 else '😊'}") for i in range(1, 11)],
                attrs={'class': 'form-control'}
            ),
            # エネルギーレベル（1-10）をセレクトボックスで表示
            'energy_level': forms.Select(
                choices=[(i, f"{i} - {'😴' if i <= 3 else '😐' if i <= 7 else '⚡'}") for i in range(1, 11)],
                attrs={'class': 'form-control'}
            ),
            # 日記本文
            'content': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 8,
                    'placeholder': '今日の出来事や感じたことを自由に書いてください...'
                }
            ),
            # 感謝欄
            'gratitude': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': '今日感謝していること、ありがたいと感じたことを書いてください...'
                }
            )
        }
        labels = {
            'mood_score': '今日の気分（1-10）',
            'energy_level': '今日のエネルギーレベル（1-10）',
            'content': '今日の日記',
            'gratitude': '感謝の気持ち'
        }

# =====================
# 行動ログフォーム
# =====================
class ActionLogForm(forms.ModelForm):
    """
    行動ログの作成・編集用フォーム。
    習慣カテゴリ・行動名・時間・完了・メモ・日付を入力。
    """
    class Meta:
        model = ActionLog
        fields = ['category', 'action_name', 'duration_minutes', 'completed', 'notes', 'date']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'action_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '例：30分の散歩、読書、瞑想など'
                }
            ),
            'duration_minutes': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': 1,
                    'max': 1440,
                    'placeholder': '分単位で入力'
                }
            ),
            'completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': '行動についてのメモや感想があれば...'
                }
            ),
            'date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            )
        }
        labels = {
            'category': 'カテゴリ',
            'action_name': '行動名',
            'duration_minutes': '継続時間（分）',
            'completed': '完了',
            'notes': 'メモ',
            'date': '日付'
        }

# =====================
# 目標フォーム
# =====================
class GoalForm(forms.ModelForm):
    """
    目標の作成・編集用フォーム。
    タイトル・詳細・カテゴリ・期限・優先度を入力。
    """
    class Meta:
        model = Goal
        fields = ['title', 'description', 'category', 'target_date', 'priority']
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '例：毎日30分の運動を習慣化する'
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': '目標の詳細や達成したい理由を書いてください...'
                }
            ),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'target_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            ),
            'priority': forms.Select(
                choices=[
                    ('low', '低 - ゆっくり進めたい'),
                    ('medium', '中 - 適度なペースで'),
                    ('high', '高 - 積極的に取り組みたい')
                ],
                attrs={'class': 'form-control'}
            )
        }
        labels = {
            'title': '目標タイトル',
            'description': '目標の詳細',
            'category': 'カテゴリ',
            'target_date': '目標達成日',
            'priority': '優先度'
        }

# =====================
# 習慣カテゴリフォーム
# =====================
class HabitCategoryForm(forms.ModelForm):
    """
    習慣カテゴリの作成・編集用フォーム。
    """
    class Meta:
        model = HabitCategory
        fields = ['name', 'description', 'color']
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '例：運動、学習、健康、趣味など'
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'カテゴリの説明...'
                }
            ),
            'color': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'type': 'color'
                }
            )
        }
        labels = {
            'name': 'カテゴリ名',
            'description': '説明',
            'color': '色'
        }
