import sys
import pexpect
import re
from optparse import OptionParser
from enum import Enum
from concurrent.futures import ThreadPoolExecutor

parser = OptionParser()
parser.add_option("-d", "--debug", action="store_true", dest="debug", help="Dump all the output from the game", default=False)
parser.add_option("-n", "--num-plays", type="int", dest="plays", help="The number of playthroughs to run", default=10)
parser.add_option("-t", "--num-threads", type="int", dest="threads", help="The number of parallel threads to run in", default=1)
(opts, args) = parser.parse_args()

verbose_progress=True
if (opts.threads > 1):
  opts.debug=False
  verbose_progress=False
if (opts.debug is True):
  verbose_progress=False

PlayProgress = Enum('PlayProgress',[
                 'DIED_DURING_FIRST_COMBAT',
#                 'ABORTED_AFTER_FIRST_COMBAT',
                 'DIED_DURING_SECOND_COMBAT',
                 'DIED_DURING_THIRD_COMBAT',
                 'DIED_DURING_FINAL_COMBAT',
                 'WON',
               ]);

def playthrough(num):
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

  def progress_msg(msg):
    if (verbose_progress):
      print(msg)
  
  def cleanup_exit(child, msg):
    child.close()
    if (verbose_progress):
      print(msg)
    print('Playthrough {} completed'.format(num))
    if (verbose_progress): print()

  print('Playthrough {} starting'.format(num))
  
  child = pexpect.spawn('python3 Text_Adventure.py')
  if opts.debug is True:
    child.logfile = sys.stdout.buffer
  
  combo=list('????')
  
  child.send('\n')
  select_opts(child, [3,2,2])
  progress_msg('Starting first combat')
  select_opts(child, [5])
  who = watch_battle(child)
  if (who=='PLAYER'):
    cleanup_exit(child, 'Player died in first combat')
    return(PlayProgress.DIED_DURING_FIRST_COMBAT)
  
  child.expect(r'Health:\s*(\d+)');
  health = int(child.match[1]);
  #if (health < 67):
  #  cleanup_exit(child, 'Player has too little health ({}) to bother continuing'.format(health))
  #  return(PlayProgress.ABORTED_AFTER_FIRST_COMBAT)
  #if (health < 67): print('Player has too little health ({}) to bother continuing, but lets try anyway'.format(health))
  
  progress_msg('Completed first combat')
  
  food_eaten=0
  food_collected=0
  
  select_opts(child, [2,2,3,2])
  food_collected+=1

  if ((health <= 75) and (food_collected > food_eaten)):
    progress_msg('Healing after first combat, because health is {}'.format(health))
    select_opts(child, [1,1,1,'x']);
    food_eaten+=1
  
  select_opts(child, [3,3,5])
  food_collected+=1

  select_opts(child, [4,2,2])

  progress_msg('Starting second combat')
  select_opts(child, [2])
  who = watch_battle(child)
  if (who=='PLAYER'):
    cleanup_exit(child, 'Player died in second combat')
    return(PlayProgress.DIED_DURING_SECOND_COMBAT)

  child.expect(r'Health:\s*(\d+)');
  health = int(child.match[1]);
  progress_msg('Completed second combat')

  if ((health <= 75) and (food_collected > food_eaten)):
    progress_msg('Healing after second combat, because health is {}'.format(health))
    select_opts(child, [1,1,1,'x']);
    food_eaten+=1
  
  select_opts(child, [5])
  progress_msg('Starting third combat')
  select_opts(child, [4])
  who = watch_battle(child)
  if (who=='PLAYER'):
    cleanup_exit(child, 'Player died in third combat')
    return(PlayProgress.DIED_DURING_THIRD_COMBAT)
  
  progress_msg('Completed third combat')
  
  progress_msg('Collecting combination for shed lock')
  child.expect(r'yellow number (\d)');
  combo[1]=child.match[1].decode('ASCII')[0]
  
  child.expect(r'Health:\s*(\d+)');
  health = int(child.match[1]);

  if ((health <= 75) and (food_collected > food_eaten)):
    progress_msg('Healing after second combat, because health is {}'.format(health))
    select_opts(child, [1,1,1,'x']);
    food_eaten+=1

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
  
  progress_msg('We now have the full combo, which is '+''.join(combo))
  
  select_opts(child, [1,1+(food_collected-food_eaten),1,'x'])
  select_opts(child, [2,3,4,1,1,1,'x',2])
  child.expect(r'Enter a four digit combination -->')
  progress_msg('Starting final boss combat')
  child.sendline(''.join(combo))
  who = watch_battle(child)
  if (who=='PLAYER'):
    cleanup_exit(child, 'Player died in final boss combat')
    return(PlayProgress.DIED_DURING_FINAL_COMBAT)
  
  progress_msg('Completed final boss combat and won the game')
  print('Playthrough {} completed'.format(num))
  if (verbose_progress): print()
  return(PlayProgress.WON)

executor = ThreadPoolExecutor(max_workers=opts.threads)

playthrough_results=[]
for gamenum in range(0, opts.plays):
  playthrough_results.append(executor.submit(playthrough, gamenum))

histogram={x:0 for x in PlayProgress}
for gamenum in range(0, opts.plays):
  progress=playthrough_results[gamenum].result()
  histogram[progress] = histogram[progress]+1

print('\nXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n')
for x in PlayProgress:
  print('{:>27} : {:3d} ({:4.1f}%)'.format(x.name, histogram[x], 100*histogram[x]/opts.plays))

# vim: set ai si sw=2 ts=80:
