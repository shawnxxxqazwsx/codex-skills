"""Immutable paper forecast/outcome records. No exchange or network access."""
import argparse
import hashlib
import json
import math
from datetime import datetime
from pathlib import Path

def dt(value):
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('Timezone required')
    return parsed

def number(d, key):
    v=d[key]
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):
        raise ValueError('Finite number required: '+key)
    return v

def write_new(path,data):
    with path.open('x') as f:
        json.dump(data,f,ensure_ascii=False,indent=2,allow_nan=False)
        f.write('\n')

def freeze(data,directory):
    for k in ('decision_id','mode','action','forecast_basis','cost_assumptions','input_hashes','reviewer_verdict'):
        if not data.get(k): raise ValueError('Missing '+k)
    if data['mode'] not in ('LOCAL_PAPER','EXCHANGE_DEMO','RESEARCH_ONLY'):
        raise ValueError('Only paper/research records supported')
    if data['mode']=='RESEARCH_ONLY' and data['action']!='NO_NEW_POSITION':
        raise ValueError('Research-only mode cannot record an investment action')
    if data.get('evaluation_rule') not in ('fixed_horizon','close_or_deadline'):
        raise ValueError('Declare fixed_horizon or close_or_deadline before action')
    if not dt(data['frozen_at_utc']) <= dt(data['effective_after_utc']) < dt(data['evaluation_at_utc']):
        raise ValueError('Forecast must precede decision and evaluation')
    lo=number(data,'scenario_low_usdt'); hi=number(data,'scenario_high_usdt')
    expected=number(data,'expected_net_pnl_usdt')
    if not lo <= expected <= hi: raise ValueError('Expected PnL outside scenarios')
    if number(data,'baseline_equity_usdt')<=0 or number(data,'mismatch_tolerance_usdt')<0:
        raise ValueError('Invalid equity/tolerance')
    if data['action'] not in ('NO_NEW_POSITION','HOLD','EXIT','REDUCE','ENTRY','ADD'):
        raise ValueError('Invalid action')
    if data['action'] in ('ENTRY','ADD') and data['reviewer_verdict']!='ACCEPT_FOR_PAPER':
        raise ValueError('Entry requires independent paper acceptance')
    directory.mkdir(parents=True,exist_ok=True)
    write_new(directory/'forecast.json',data)
    return {'status':'frozen'}

def settle(data,directory):
    p=directory/'forecast.json';raw=p.read_bytes();f=json.loads(raw)
    if data['decision_id']!=f['decision_id']: raise ValueError('Decision id mismatch')
    if data.get('final') is not True or data.get('costs_reconciled') is not True or not data.get('evidence_paths'):
        raise ValueError('Final reconciled evidence required')
    if data.get('measurement_basis') not in ('realized_net_pnl','horizon_liquidation_pnl'):
        raise ValueError('Invalid measurement basis')
    observed=dt(data['observed_at_utc'])
    if observed<dt(f['effective_after_utc']): raise ValueError('Outcome precedes decision')
    early_close=f['evaluation_rule']=='close_or_deadline' and data['measurement_basis']=='realized_net_pnl'
    if observed<dt(f['evaluation_at_utc']) and not early_close and data.get('early_risk_breach') is not True:
        raise ValueError('Evaluation horizon not reached')
    actual=number(data,'actual_net_pnl_usdt');error=actual-f['expected_net_pnl_usdt']
    outside=not f['scenario_low_usdt']<=actual<=f['scenario_high_usdt']
    result=dict(outcome=data,forecast_sha256=hashlib.sha256(raw).hexdigest(),
        signed_error_usdt=error,absolute_error_usdt=abs(error),outside_scenario=outside,
        retrospective_required=abs(error)>f['mismatch_tolerance_usdt']+1e-9 or outside or data.get('early_risk_breach') is True)
    write_new(directory/'outcome.json',result)
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['freeze','settle'])
    parser.add_argument('input',type=Path);parser.add_argument('directory',type=Path)
    a=parser.parse_args();result=globals()[a.action](json.loads(a.input.read_text()),a.directory)
    print(json.dumps(result,ensure_ascii=False,allow_nan=False))
