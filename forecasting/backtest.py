"""New historical backtest; not a reproduction of dissertation experiments."""
from pathlib import Path
import csv,json,math
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
ROOT=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((ROOT/'reports/sector_totals_ktoe.csv').open()))
y=np.array([float(r['All final users']) for r in rows]);years=[int(r['year']) for r in rows]
assert years==list(range(1970,2025)) and np.isfinite(y).all()
results=[]
for horizon in [1,3,5]:
 for origin in range(32,len(y)-horizon):
  train=list(range(2,origin-horizon+1));assert max(i+horizon for i in train)<=origin
  X=np.array([[y[i],y[i-1],y[i-2]] for i in train]);target=np.array([y[i+horizon] for i in train])
  query=np.array([[y[origin],y[origin-1],y[origin-2]]])
  models={'Persistence':None,'Ridge':make_pipeline(StandardScaler(),Ridge(alpha=1.0)), 'Random forest':RandomForestRegressor(n_estimators=100,max_depth=3,min_samples_leaf=3,random_state=42)}
  for name,model in models.items():
   prediction=float(y[origin]) if model is None else float(model.fit(X,target).predict(query)[0])
   results.append({'origin_year':years[origin],'target_year':years[origin+horizon],'horizon':horizon,'model':name,'actual_ktoe':float(y[origin+horizon]),'predicted_ktoe':prediction,'last_training_target_year':years[max(i+horizon for i in train)]})
summary=[]
for horizon in [1,3,5]:
 for name in ['Persistence','Ridge','Random forest']:
  group=[r for r in results if r['horizon']==horizon and r['model']==name];e=[r['predicted_ktoe']-r['actual_ktoe'] for r in group]
  summary.append({'horizon':horizon,'model':name,'origins':len(e),'mae_ktoe':sum(abs(x) for x in e)/len(e),'rmse_ktoe':math.sqrt(sum(x*x for x in e)/len(e))})
with (ROOT/'forecasting/backtest_predictions.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
(ROOT/'forecasting/backtest_metrics.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,indent=2))
