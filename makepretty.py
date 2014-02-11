#!/usr/bin/env python
# makepretty.py -- make a nice diagram on the github website.

from pymendez import auth
import github
import datetime
import calendar


# Pixel map for character to pixel array.
# top to bottom left to right.
CHARMAP = {
  'W':['100010', '100010', '100010', '101010', '010100'],
  'H':['10010', '10010', '11110', '10010', '10010' ],
  'O':['11110', '10010', '10010', '10010', '11110'],
  'R':['11100', '10010', '11100', '10010', '10010'],
  'D':['11100', '10010', '10010', '10010', '11100' ],
  'E':['1110', '1000', '1100', '1000', '1110'],
  'L':['1000', '1000', '1000', '1000', '1110' ],
  ' ':['000', '000', '000', '000', '000'],
}





def create_tree(repo, tree, parent):
  '''Create a tree in a repo object, a tree dictionary, and a parent hash.'''
  params = dict(
    base_tree=parent,
    tree=[tree]
  )
  headers, data = repo._requester.requestJsonAndCheck(
                        "POST",
                        repo.url + "/git/trees",
                        input=params,
                    )
  return github.GitTree.GitTree(repo._requester, headers, data, 
                                completed=True)


def create_commit(user, repo, message, tree, parent, date):
  '''Build a commit.  Uses the user login and email as the commiter, and
  then commits the tree with message to a parrent hash on a date.'''
  date = datetime.datetime.combine(date, 
                                   datetime.datetime.min.time()).isoformat()
  params = dict(
    message=message,
    tree=tree,
    parents=[parent],
    author=dict(
      name=user.login,
      email=user.get_emails()[0],
      date=date,
    )
  )
  headers, data = repo._requester.requestJsonAndCheck(
                        "POST",
                        repo.url + "/git/commits",
                        input=params,
                    )
  return github.GitCommit.GitCommit(repo._requester, headers, data, completed=True)



def pixel(user, repo, date):
  '''Build a pixel commit for each date for a user on a repo.'''
  data = u'BLOB: {}'.format(date)
  blob = repo.create_git_blob(data, 'utf-8')
  
  # Create a tree
  master = repo.get_git_ref('heads/master')
  message = 'Commit: {}'.format(date)
  parent = master.raw_data['object']['sha']
  t = dict(
    path='data.txt',
    mode='100644',
    type='blob',
    sha=blob.sha,
  )
  tree = create_tree(repo, t, parent)
  
  # create the commit -- break out the date from the standard function
  # commit = repo.create_git_commit(message, tree, parents)
  commit = create_commit(user, repo, message, tree.sha, parent, date)
  
  # update headds
  master.edit(sha=commit.sha)




def gen_reverse_date(year):
  '''Generates either a None -- new week, or a day of the week. This goes
  back starting with the last day in a year.'''
  cal = calendar.Calendar(6)
  for month in reversed(cal.yeardatescalendar(year,1)): 
    for week in reversed(month[0]):
      yield None # for the new week
      
      for day in reversed(week):
        yield day
      
def get_dates(ndate):
  '''Generate a list of dates depending on the number of 
  columns that are needed (ndate). '''
  today = datetime.date.today()
  
  out = [[]]
  getDate = False
  year = today.year

  while len(out) < ndate:
    for day in gen_reverse_date(year):
      # A Week has past
      if day is None:
        if getDate:
          if len(out[-1]) == 7:
            out.append([])
        continue
      
      # get previous dates
      if day < today:
        getDate = True
      
      # add to the output
      if getDate and (day.year == year):
        try:
          if day not in out[-2]:
            raise ValueError
        except:
          out[-1].append(day)
      
      # Return if needed
      if len(out) == ndate:
        return out
    
    # Keep going back in time unless we have gone too far
    year -= 1
    if year < 2010:
      raise ValueError('Why are you going this far back in time?!')
  return out






def convert_text(text):
  '''Convert the string into a set of pixel arrays.'''
  nrows = len(''.join( CHARMAP[c.upper()][0] for c in text ) )
  out = []
  yoffset = 1
  xoffset = 2
  rows = get_dates(nrows+xoffset)
  j = len(rows)-1-xoffset
  for k,c in enumerate(text):
    for r in zip(*CHARMAP[c.upper()]):
      for ii,y in enumerate(r,yoffset):
        i = 6-ii
        rows[j][0] = None
        rows[j][-1] = None
        if y == '0':
          rows[j][i] = None
        if y == '1':
          out.append(rows[j][i])
      j -= 1
  return out

def debug_text(text):
  '''Print to the screen to check that the char map looks right'''
  for c in text:
    for row in CHARMAP[c.upper()]:
      for col in row:
        print ('#' if col=='1' else ' '),
      print
    print


def setup(text):
  '''Seup the pixel diagram for a given text string.'''
  token, reponame = auth('github', ('token','reponame'))
  api = github.Github(token)
  user = api.get_user()
  repo = user.get_repo(reponame)
  
  for date in convert_text(text):
    pixel(user, repo, date)


if __name__ == '__main__':
  setup('HELLO WORLD')