#!/usr/bin/env python
# makepretty.py -- make a nice diagram on the github website.

from pymendez import auth
import github
from github import Github
import datetime
import calendar


def create_tree(repo, tree):
  params = dict(
    base_tree='6b232b45d106c0afb9e7cc4214b25322350bd063',
    tree=[tree]
  )
  headers, data = repo._requester.requestJsonAndCheck(
              "POST",a
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

def setup():
  username, password, token, reponame = auth('github', 
                                   ('username','password','token','reponame'))
  # api = Github(username, password)
  api = Github(tokin)
  user = api.get_user()
  repo = user.get_repo(reponame)
  
  # first test -- build a blob to commit
  cdate = datetime.date.today() - datetime.timedelta(days=1)
  data = u'BLOB: {}'.format(cdate)
  blob = repo.create_git_blob(data, 'utf-8')
  
  # Create a tree
  t = dict(
    path='data.txt',
    mode='100644',
    type='blob',
    sha=blob.sha,
  )
  tree = create_tree(repo, t)
  
  
  master = repo.get_git_ref('heads/master')
  message = 'Commit: {}'.format(cdate)
  parents = master.raw_data['object']['sha']
  # commit = repo.create_git_commit(message, tree, parents)
  commit = create_commit(user, repo, message, tree.sha, parents, cdate)
  
  # update headds
  master.edit(sha=commit.sha)



CHARMAP = {
  'H':['10001', '10001', '11111', '10001', '10001'],
  'E':['11111', '10000', '11100', '10000', '11111'],
  'L':['10000', '10000', '10000', '10000', '11111'],
  'O':['11111', '10001', '10001', '10001', '11111'],
  'W':['10001', '10001', '10001', '10101', '01010'],
  'R':['11100', '10010', '11100', '10010', '10001'],
  'D':['11100', '10010', '10010', '10010', '11100'],
  ' ':['00000', '00000', '00000', '00000', '00000'],
}




def convert_text(text):
  width = 6 # 5 wide + space
  nchar = len(text)
  nrows = width*nchar
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