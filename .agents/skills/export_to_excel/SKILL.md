---
name: export-to-excel
description: Export all inspection records from the SQLite database to a formatted Excel report.
---

# Export to Excel Skill

이 스킬은 `safety_records.db`에 저장된 모든 현장 안전점검 및 드론 판독 기록을 깔끔하게 서식화된 Excel 파일(`.xlsx`)로 내보냅니다.

## 실행 방법

터미널에서 아래 Python 스크립트를 실행합니다:

```powershell
.\.venv\Scripts\python.exe -c "
import pandas as pd
import sqlite3
from datetime import datetime

conn = sqlite3.connect('safety_records.db')
df = pd.read_sql_query('SELECT * FROM inspections ORDER BY date DESC', conn)
conn.close()

filename = f'안전점검보고서_{datetime.now().strftime(\"%Y%m%d_%H%M%S\")}.xlsx'
with pd.ExcelWriter(filename, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='점검이력', index=False)
print(f'보고서가 성공적으로 생성되었습니다: {filename}')
"
```
