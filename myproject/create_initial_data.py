#!/usr/bin/env python
import os
import sys
import django

# Djangoの設定を読み込み
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myapp.models import HabitCategory
from django.contrib.auth.models import User

def create_initial_data():
    """初期データを作成"""
    
    # 習慣カテゴリを作成
    categories = [
        {
            'name': '運動・フィットネス',
            'description': '身体の健康を保つための運動やフィットネス活動',
            'color': '#28a745'
        },
        {
            'name': '学習・スキルアップ',
            'description': '新しい知識やスキルを身につけるための学習活動',
            'color': '#17a2b8'
        },
        {
            'name': '健康・ウェルネス',
            'description': '心身の健康を保つための活動（食事、睡眠、瞑想など）',
            'color': '#ffc107'
        },
        {
            'name': '仕事・キャリア',
            'description': '仕事やキャリアに関連する活動やスキル開発',
            'color': '#6f42c1'
        },
        {
            'name': '趣味・娯楽',
            'description': '楽しみやリラックスのための趣味活動',
            'color': '#fd7e14'
        },
        {
            'name': '人間関係・コミュニケーション',
            'description': '家族、友人、同僚との関係構築やコミュニケーション',
            'color': '#e83e8c'
        },
        {
            'name': '家事・生活管理',
            'description': '日常生活の管理や家事に関する活動',
            'color': '#6c757d'
        },
        {
            'name': '創造性・アート',
            'description': '創造的な活動やアート、DIYなど',
            'color': '#20c997'
        }
    ]
    
    created_categories = []
    for cat_data in categories:
        category, created = HabitCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'description': cat_data['description'],
                'color': cat_data['color']
            }
        )
        if created:
            print(f"カテゴリを作成しました: {category.name}")
        else:
            print(f"カテゴリは既に存在します: {category.name}")
        created_categories.append(category)
    
    print(f"\n合計 {len(created_categories)} 個のカテゴリが利用可能です。")
    
    # サンプルユーザーを作成（テスト用）
    try:
        test_user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'テスト',
                'last_name': 'ユーザー'
            }
        )
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            print(f"\nテストユーザーを作成しました: {test_user.username}")
            print("ログイン情報: username=testuser, password=testpass123")
        else:
            print(f"\nテストユーザーは既に存在します: {test_user.username}")
    except Exception as e:
        print(f"テストユーザーの作成でエラーが発生しました: {e}")
    
    print("\n初期データの作成が完了しました！")

if __name__ == '__main__':
    create_initial_data()

