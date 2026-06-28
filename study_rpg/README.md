# 資格攻略RPG Dashboard

応用情報技術者試験と危険物取扱者甲種の勉強を、XP・レベル・スタンプ・攻略率で可視化する Streamlit アプリです。

## 起動方法

```bash
pip install -r requirements.txt
streamlit run study_rpg/app.py
```

初回起動時に `study_rpg/data/study_rpg.sqlite3` が自動作成されます。

## 画面

- トップページ
  - 総XP
  - 現在レベル
  - 今日の学習状況
  - 連続学習日数
  - 応用情報 攻略率
  - 危険物甲種 攻略率
  - 最近の学習ログ
- 応用情報ページ
  - 過去問道場へのリンク
  - 午前問題100問完了
  - 午後問題1問完了
  - 今日のスタンプ
  - 分野別攻略率
- 危険物甲種ページ
  - 問題演習完了
  - 化学物質図鑑
  - 化学物質追加フォーム
  - 図鑑レベルアップ
  - 類別ごとの攻略率

## XPルール

| 行動 | XP |
| --- | ---: |
| 応用情報 午前100問完了 | 1000 |
| 応用情報 午後1問完了 | 300 |
| 危険物 問題演習1セット完了 | 800 |
| 化学物質図鑑に1件追加 | 200 |
| 図鑑レベルアップ | 100 |

## レベル

| Level | 必要XP |
| --- | ---: |
| Lv1 | 0 |
| Lv2 | 500 |
| Lv3 | 1500 |
| Lv4 | 3000 |
| Lv5 | 5000 |
| Lv6 | 8000 |
| Lv7 | 12000 |
| Lv8 | 17000 |
| Lv9 | 23000 |
| Lv10 | 30000 |

## ファイル構成

```text
study_rpg/
  app.py
  db.py
  xp.py
  pages/
    applied_info.py
    hazardous_materials.py
  data/
    study_rpg.sqlite3  # 初回起動時に自動作成
  README.md
```
