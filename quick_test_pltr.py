import requests
import time

intervals = ['1m', '5m', '15m', '1h', '1d', '1w', '1mo', '1y', 'ytd', 'max']

for interval in intervals:
    try:
        resp = requests.get('http://localhost:8000/api/pattern-detection',
                           params={'symbol': 'PLTR', 'interval': interval},
                           timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            kl = data.get('key_levels', {})
            btd = kl.get('BTD')
            pdh = kl.get('PDH')
            pdl = kl.get('PDL')
            btd_str = f'${btd:.2f}' if btd is not None else 'null'
            pdh_str = f'${pdh:.2f}' if pdh is not None else 'null'
            pdl_str = f'${pdl:.2f}' if pdl is not None else 'null'
            print(f'{interval:5s} | BTD: {btd_str:>10} | PDH: {pdh_str:>10} | PDL: {pdl_str:>10}')
        else:
            print(f'{interval:5s} | HTTP {resp.status_code}')
    except Exception as e:
        print(f'{interval:5s} | Error: {e}')
    time.sleep(0.5)
