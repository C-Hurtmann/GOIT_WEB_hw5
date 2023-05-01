import subprocess

process = subprocess.run('python3 chat/scripts/exchange.py -d 2 -a GBP', capture_output=True, text=True,  shell=True)

print(process.stdout)