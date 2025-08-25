from django.apps import AppConfig

# このアプリ（myapp）の設定クラス
class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # デフォルト主キー型
    name = 'myapp'  # アプリ名
