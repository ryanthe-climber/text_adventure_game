import sys
import pexpect
import re
from optparse import OptionParser
from enum import Enum

parser = OptionParser()
parser.add_option("-d", "--debug", action="store_true", dest="debug", help="Dump all the output from the game", default=False)
(opts, args) = parser.parse_args()

PlayProgress = Enum('PlayProgress',[
                 'DIED_DURING_FIRST_COMBAT',
                 'ABORTED_AFTER_FIRST_COMBAT',
                 'DIED_DURING_SECOND_COMBAT',
                 'DIED_DURING_THIRD_COMBAT',
                 'DIED_DURING_FINAL_COMBAT',
                 'WON',
               ]);

def playthrough():
  def watch_battle(child):
    while True:
      child.expect(r'(PLAYER|ENEMY) HEALTH:\s*(-?\d+)');
      who = child.match[1].decode('ASCII')
      health = int(child.match[2])
      if (health < 1): break
      child.expect('Press ENTER to continue.');
      child.send('\n');
    return who
  
  def select_opts(child, opts):
    for opt in opts:
      child.expect(r'-->')
      child.sendline(str(opt))
  
  def cleanup_exit(child, msg):
    child.close()
    print()
    print(msg)
  
  child = pexpect.spawn('python3 Text_Adventure.py')
  if opts.debug is True:
    child.logfile = sys.stdout.buffer
  
  combo=list('????')
  
  child.send('\n')
  select_opts(child, [3,2,2])
  print('Starting first combat')
  select_opts(child, [5])
  who = watch_battle(child)
  if (who=='PLAYER'):
    cleanup_exit(child, 'Player died in first combat')
    return(PlayProgress.DIED_DURING_FIRST_COMBAT)
  
  child.expect(r'Health:\s*(\d+)');
  health = int(child.match[1]);
  if (health < 67):
    cleanup_exit(child, 'Player has too little health ({}) to bother continuing'.format(health))
    return(PlayProgress.ABORTED_AFTER_FIRST_COMBAT)
  #if (health < 67): print('Player has too little health ({}) to bother continuing, but lets try anyway'.format(health))
  
  print('Completed first combat')
  
  select_opts(child, [2,2,3,2])
  
  heal_after_second_combat=True
  if (health <= 75):
    print('Healing after first combat, because health is {}'.format(health))
    select_opts(child, [1,1,1,'x']);
    heal_after_second_combat=False
  
  select_opts(child, [3,3,5,4,2,2])
  print('Starting second combat')
  select_opts(child, [2])
  who = watch_battle(child)
  if (who=='PLAYER'):
    cleanup_exit(child, 'Player died in second combat')
    return(PlayProgress.DIED_DURING_SECOND_COMBAT)
  print('Completed second combat')
  if (heal_after_second_combat):
    print('Healing after second combat')
    select_opts(child, [1,1,1,'x']);
  
  select_opts(child, [5])
  print('Starting third combat')
  select_opts(child, [4])
  who = watch_battle(child)
  if (who=='PLAYER'):
    cleanup_exit(child, 'Player died in third combat')
    return(PlayProgress.DIED_DURING_THIRD_COMBAT)
  
  print('Completed third combat')
  
  print('Collecting combination for shed lock')
  child.expect(r'yellow number (\d)');
  combo[1]=child.match[1].decode('ASCII')[0]
  
  select_opts(child, [2,2,3,2])
  child.expect(r'green number (\d)');
  combo[2]=child.match[1].decode('ASCII')[0]
  
  select_opts(child, [3,4,2,3,2,2,3,4,3,2])
  child.expect(r'blue number (\d)');
  combo[3]=child.match[1].decode('ASCII')[0]
  
  select_opts(child, [4,5,4])
  child.expect(r'\(yes/no\):')
  child.sendline('yes')
  select_opts(child, [3])
  child.expect(r'is the number (\d)');
  combo[0]=child.match[1].decode('ASCII')[0]
  
  print('We now have the full combo, which is '+''.join(combo))
  
  select_opts(child, [1,2,1,'x',2,3,4,1,1,1,'x',2])
  child.expect(r'Enter a four digit combination -->')
  print('Starting final boss combat')
  child.sendline(''.join(combo))
  who = watch_battle(child)
  if (who=='PLAYER'):
    cleanup_exit(child, 'Player died in final boss combat')
    return(PlayProgress.DIED_DURING_FINAL_COMBAT)
  
  print('Completed final boss combat and won the game')
  return(PlayProgress.WON)

histogram={x:0 for x in PlayProgress}
for gamenum in range(0, 100):
  print('\nXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
  print('{:^70}\n'.format(gamenum+1))
  progress=playthrough()
  histogram[progress] = histogram[progress]+1

for x in PlayProgress:
    print('{:>27} : {:3d}'.format(x.name, histogram[x]))
