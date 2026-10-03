import subprocess
from pathlib import Path
ROOT = Path(__file__).parent
PROBES = ['.env','production.env','secrets/jwt.key','tokens.txt','credentials.json','.claude/settings.json','CLAUDE.md','AGENTS.md']

def check():
    for probe in PROBES:
        if subprocess.run(['git','check-ignore','--no-index','-q',probe],cwd=ROOT).returncode:
            raise RuntimeError(f'Not ignored: {probe}')
    tracked = subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    for name in filter(None,tracked):
        if subprocess.run(['git','check-ignore','--no-index','-q',name],cwd=ROOT).returncode == 0:
            raise RuntimeError(f'Forbidden tracked file: {name}')
    return len(PROBES)
if __name__ == '__main__':
    print(f'{check()} ignore probes passed; no forbidden tracked paths')
