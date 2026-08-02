"""Check the plan against every rule before publishing.

    python3 check.py
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib'))
from collections import defaultdict
from plan import (PLAN, CAP, STD_SC, STD_LC, CAPACITY, lanes, hours, mornings,
                  env, halves, DAYS, D3, FA, SIZE)
from turnaround import violations

fails = []
def check(label, ok, detail=''):
    print(f'  {label:<42}{"pass" if ok else "FAIL"}   {detail}')
    if not ok: fails.append(label)

print('ROW 2026-27, rule check\n')

u = defaultdict(int); clash = []
for g, ss in PLAN.items():
    for d, r, f in ss:
        for h in halves(r):
            k = f'{d}|{f}|{h}'
            if k not in env: clash.append((g, d, r, 'outside held water')); continue
            n = lanes(g, d, r, f, env[k]['crs'])
            if env[k]['lanes'] - u[(d, f, h)] < n: clash.append((g, d, r, h))
            u[(d, f, h)] += n
check('lanes fit the water we hold', not clash, str(clash[:2]) if clash else '')

v = violations({k: x for k, x in PLAN.items() if k != 'JD2'}, 12 * 60)
check('twelve hours between evening and morning', not v, str(v))

over = [(g, d, r) for g, ss in PLAN.items() for d, r, f in ss
        if len(halves(r)) * 0.5 > CAP[g] + 0.01]
check('maximum session length', not over, str(over))

bad = []
for g, ss in PLAN.items():
    if g == 'RSA': continue
    for d, r, f in ss:
        crs = env[f'{d}|{f}|{halves(r)[0]}']['crs']
        std = STD_LC.get(g, STD_SC.get(g, 6)) if crs == 'LCM' else STD_SC.get(g, 6)
        if SIZE[g] / lanes(g, d, r, f, crs) > std + 0.01: bad.append((g, d, r))
check('swimmers per lane at capacity', not bad, str(bad[:2]))

dbl = [(g, D3[d]) for g, ss in PLAN.items() for d in DAYS
       if sum(1 for x, _, _ in ss if x == d) > 1
       and g not in ('ND 18&U', 'PD 18&U') and not g.startswith('TOPS')]
check('one session a day, ND and PD1 aside', not dbl, str(dbl))

S = [len(PLAN[x]) for x in ('RD 12&U', 'RD 14&U', 'RD 18&U')]
check('Regional sessions rise', all(a < b for a, b in zip(S, S[1:])), str(S))
S2 = [len(PLAN[x]) for x in ('PD 12&U', 'PD 14&U', 'PD 18&U')]
check('Provincial sessions rise', all(a < b for a, b in zip(S2, S2[1:])), str(S2))
H = [hours(x) for x in ('RD 12&U', 'RD 14&U', 'RD 18&U')]
check('Regional hours rise', all(a < b for a, b in zip(H, H[1:])), str(H))
H2 = [hours(x) for x in ('PD 12&U', 'PD 14&U', 'PD 18&U')]
check('Provincial hours rise', all(a < b for a, b in zip(H2, H2[1:])), str(H2))
M = [mornings(x) for x in ('RD 12&U', 'RD 14&U', 'RD 18&U')]
check('Regional mornings never fall', all(a <= b for a, b in zip(M, M[1:])), str(M))
M2 = [mornings(x) for x in ('PD 12&U', 'PD 14&U', 'PD 18&U')]
check('Provincial mornings never fall', all(a <= b for a, b in zip(M2, M2[1:])), str(M2))

rc = [g for g, ss in PLAN.items() for d, r, f in ss
      if f == 'Rec Centre' and not g.startswith('REC')]
check('Rec Centre is Recreation only', not rc, str(rc))
late = sorted({g for g, ss in PLAN.items() for d, r, f in ss if f == 'Cameron Heights'
               and any(h in ('8:00-8:30 pm', '8:30-9:00 pm') for h in halves(r))})
check('Cameron Heights after 8 pm', all(x.startswith('REC') for x in late), str(late))

held = sum(x['lanes'] for x in env.values()) * 0.5
print(f'\n  utilisation {sum(u.values())*0.5:.0f} of {held:.0f} lane-hours '
      f'= {sum(u.values())*0.5/held*100:.0f}%')
print('\n' + ('All rules pass.' if not fails else f'{len(fails)} FAILED: {fails}'))
sys.exit(1 if fails else 0)
