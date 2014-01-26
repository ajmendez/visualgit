#!/usr/bin/env python
# makepretty.py -- make a nice diagram on the github website.

from pymendez import auth
import github
import datetime
import calendar


def create_tree(repo, tree, parent):
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
  
  # create the commit
  # commit = repo.create_git_commit(message, tree, parents)
  commit = create_commit(user, repo, message, tree.sha, parent, date)
  
  # update headds
  master.edit(sha=commit.sha)



def setup():
  token, reponame = auth('github', ('token','reponame'))
  # api = Github(username, password)
  api = github.Github(token)
  user = api.get_user()
  repo = user.get_repo(reponame)
  
  # first test -- build a blob to commit
  # cdate = datetime.date.today() - datetime.timedelta(days=1)
  text = 'HELLO WORLD'
  for date in convert_text(text):
    
    # if date > datetime.date(2013,5,24):
    print date
    pixel(user, repo, date)
  








def gen_reverse_date(year):
  '''Generates either a None -- new week, or a day of the week.'''
  cal = calendar.Calendar(6)
  for month in reversed(cal.yeardatescalendar(year,1)): 
    for week in reversed(month[0]):
      yield None # for the new week
      
      for day in reversed(week):
        yield day
      
def get_dates(ndate):
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
        # out[-1].append(day)
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
      raise ValueError('Why are you going back in time?!')
  return out


CHARMAP = {
  'H':['10010', '10010', '11110', '10010', '10010' ],
  
  'O':['11110', '10010', '10010', '10010', '11110'],
  'R':['11100', '10010', '11100', '10010', '10010'],
  'D':['11100', '10010', '10010', '10010', '11100' ],
  'E':['1110', '1000', '1100', '1000', '1110'],
  'L':['1000', '1000', '1000', '1000', '1110' ],
  ' ':['000', '000', '000', '000', '000'],
  'W':['100010', '100010', '100010', '101010', '010100'],
}




def convert_text(text):
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
    
    # if k < len(text)-1:
    #   for i in range(7):
    #     rows[j][i] = None
    #   j -= 1
#     pprint(rows)
  # return rows
  return out

def debug_text(text):
  for c in text:
    for row in CHARMAP[c.upper()]:
      for col in row:
        print ('#' if col=='1' else ' '),
      print
    print



if __name__ == '__main__':
  from pysurvey import util
  util.setup_stop
  
  
  setup()