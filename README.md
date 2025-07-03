# election
視線の滞留を用いて投票を行うためのGUI
## Setup & Run
Windows11, Python 3.11.9で動作確認をしています
```PowerShell
#PowerShell
git clone https://github.com/shiba0627/election.git
cd election
python -m venv venv_election
.\venv_election\Scripts\activate 
python -m pip install -r requirements.txt 

python main.py
```

## システム構成(編集中)
#### ハードウェア
- ノートPC

- 視線検出装置

- 高さ調整可能テーブル

#### ソフトウェア
- Windows11 Pro
- Python 3.11.9以上

## GUI仕様
編集中
## コマンドメモ
```PowerShell
#パッケージ一覧の出力
python -m pip freeze > requirements.txt 
```