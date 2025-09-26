import requests
import json

# Test drawing commands
response = requests.post(
    'http://localhost:8000/ask',
    json={'query': 'Show me support and resistance levels for NVDA'},
    timeout=30
)

if response.status_code == 200:
    data = response.json()
    commands = data.get('chart_commands', [])
    print('Total Commands:', len(commands))
    print('All Commands:', commands)
    
    # Check for drawing commands
    drawing_cmds = [c for c in commands if any(
        c.startswith(p) for p in ['SUPPORT:', 'RESISTANCE:', 'FIBONACCI:', 'TRENDLINE:', 'ENTRY:', 'TARGET:']
    )]
    
    if drawing_cmds:
        print('\n✅ Drawing Commands Found:')
        for cmd in drawing_cmds:
            print(f'  - {cmd}')
    else:
        print('\n⚠️ No drawing commands found')
        print('Checking for ANALYZE flag...')
        if 'ANALYZE:TECHNICAL' in commands:
            print('  Found ANALYZE:TECHNICAL flag - technical analysis was requested')
    
    # Check tool_results
    tool_results = data.get('tool_results', {})
    if 'technical_analysis' in tool_results:
        print('\n🔬 Technical Analysis Data:')
        ta = tool_results['technical_analysis']
        for key in ['support_levels', 'resistance_levels', 'fibonacci_levels', 'patterns']:
            if key in ta:
                print(f'  - {key}: {ta[key]}')
else:
    print(f'Error: {response.status_code}')