import sys
import pexpect
import re
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-d", "--debug", action="store_true", dest="debug", help="Dump all the output from the game", default=False)
(opts, args) = parser.parse_args()

child = pexpect.spawn('python3 Text_Adventure.py')
if opts.debug is True:
  child.logfile = sys.stdout.buffer

def watch_battle():
  while True:
    child.expect(r'(PLAYER|ENEMY) HEALTH:\s*(-?\d+)');
    who = child.match[1].decode('ASCII')
    health = int(child.match[2])
    if (health < 1): break
    child.expect('Press ENTER to continue.');
    child.send('\n');
  return who

def select_opts(opts):
  for opt in opts:
    child.expect(r'-->')
    child.sendline(str(opt))

def cleanup_exit(msg):
  child.close()
  print()
  print(msg)
  exit()

combo=list('????')

child.send('\n')
select_opts([3,2,2,5])
who = watch_battle()
if (who=='PLAYER'): cleanup_exit('Player died in first combat')

child.expect(r'Health:\s*(\d+)');
health = int(child.match[1]);
if (health < 67): cleanup_exit('Player has too little health to bother continuing')

print('Completed first combat')

select_opts([2,2,3,2])

heal_after_second_combat=True
if (health <= 75):
  select_opts([1,1,1,'x']);
  heal_after_second_combat=False

select_opts([3,3,5,4,2,2,2])
who = watch_battle()
if (who=='PLAYER'): cleanup_exit('Player died in second combat')
if (heal_after_second_combat):
  select_opts([1,1,1,'x']);

print('Completed second combat')

select_opts([5,4])
who = watch_battle()
if (who=='PLAYER'): cleanup_exit('Player died in third combat')

print('Completed third combat')

child.expect(r'yellow number (\d)');
combo[1]=child.match[1].decode('ASCII')[0]

select_opts([2,2,3,2])
child.expect(r'green number (\d)');
combo[2]=child.match[1].decode('ASCII')[0]

select_opts([3,4,2,3,2,2,3,4,3,2])
child.expect(r'blue number (\d)');
combo[3]=child.match[1].decode('ASCII')[0]

select_opts([4,5,4])
child.expect(r'\(yes/no\):')
child.sendline('yes')
select_opts([3])
child.expect(r'is the number (\d)');
combo[0]=child.match[1].decode('ASCII')[0]

print('We now have the full combo, which is '+''.join(combo))

select_opts([1,2,1,'x',2,3,4,1,1,1,'x',2])
child.expect(r'Enter a four digit combination -->')
child.sendline(''.join(combo))
who = watch_battle()
if (who=='PLAYER'): cleanup_exit('Player died in final boss combat')

print('Completed final boss combat and won the game')
