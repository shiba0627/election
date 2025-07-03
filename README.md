# election
視線の滞留を用いて投票を行う
## Setup & Run<初回のみ>
```PowerShell
#git clone https://github.com/shiba0627/copy_Excel.git
cd election
python -m venv venv_election
.\venv_election\Scripts\activate 
python -m pip install -r requirements.txt 
python main.py
```

```PowerShell
#パッケージ一覧
python -m pip freeze > requirements.txt 
```