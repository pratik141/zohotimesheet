#!/usr/bin/env python

"""
  Author name : Pratik Anand
  Authon Email: pratik.anand@mobiliya.com
  Description : ZOHO timesheet 

"""
from termcolor import colored ,cprint  ## fro colored output
import requests  
import json
import sys 

baseUrl = "https://projectsapi.zoho.com/restapi"
print(colored("   Enter 'ooo' or 'OOO' for exit \n \
  'reconf' for reconfigure ", 'red' ,attrs=['bold']))
""" utils """
def warn(val):
  print(colored( "%s" %(val), 'yellow'))

def error(val):
  print(colored( "%s" %(val), 'red', attrs=['bold']))
  exit()

def info(val):
  print(colored( "%s" %(val), 'cyan'))

def question(val):
  cprint( "%s" %(val), 'magenta', end=' ') 

def getKey(l,i):
   for k, v in l.items():
    if v == i:
      return k

""" validate input """

def takeInput(msg,required,append=False):
  question(msg)
  if sys.version_info[0] < 3:
    ans = raw_input()
  else:
    ans = input()

  if not ans:
      warn("You entered nothing...!")
      return takeInput(msg,required,append=append) 

    ###  Exit keyword ###
  elif ans in ['ooo', 'OOO']:
    error("Closing instance.")


  elif ans in ['reconf', 'RECONF']:
    warn("Removing config file")
    import os
    try:
      os.remove('config.yml')
    except OSError as e:
      warn(e)
    return PostTimeLog()

  else:
    if append:
      ans += ','

    if ans.isdigit():
      current = 'int'
    elif set('[~!@#$%^&*()_+{}":/\']+$').intersection(ans):
      current = 'other'
    elif sys.version_info[0] > 3 and isinstance(ans,basestring):
      current = 'str'
    elif sys.version_info[0] < 3 or isinstance(ans,str): ## python 3
      current = 'str'
    else:
      current = 'none'

  if required == current :
    return ans
  else:
    if 'required' in  msg :
      return takeInput(msg,required,append=append)
    else:  
      return takeInput(msg+'(required: %s)' %required,required,append=append)

### util ends ###

class GetDetails(object):
  """docstring for getDetails"""

  def getAuthToken(self):

    info(""" 
        Please enter your Auth token like: b72e53c9fdfr5s43rgs3b4c0f0sw2s31828
        To generate the Auth Token, you need to send an authentication request to Zoho Accounts using the URL format below :
        
        Important Notes :
    
          * The Auth Token is user-specific and is a permanent token.
          * The Auth Token of a user's account becomes invalid if the user account is removed or regenerated.
          * You must be logged into your Zoho Projects account to use the Browser Mode.
    
        URL Format
          Browser Mode :
              "https://accounts.zoho.com/apiauthtoken/create?SCOPE=ZohoProjects/projectsapi,ZohoPC/docsapi"
        """)

    self.authToken = takeInput('Auth token:','str')

    ## Validate ## 
    self.params = {"authtoken": self.authToken }
    url = baseUrl+'/portals/'
    self.r = requests.get(url, params = self.params);
    
    if self.r.status_code == 200:
      return "Authenticated"
    else:
      warn("Invalid Token")
      return self.getAuthToken()

  def getportalId(self):
    
    self.getAuthToken()

    url = baseUrl  + '/portals/'
    portalJsonList = requests.get(url, params = self.params).content
    self.portalId  = json.loads(str(portalJsonList.decode('utf-8')))['portals'][0]['id']
    return self.portalId

  def getProjectId(self):
    self.getportalId()  
    
    url = baseUrl + '/portal/' + str(self.portalId) + '/projects/'
    projectList = requests.get(url, params = self.params).content;
    projectDic  = {}; i=0; projectId=[]; tempList = []
    
    for item in json.loads(str(projectList.decode('utf-8')))['projects']:
      info('[' + str(i) + ']' + ':' + item.get('name'))
      projectDic[item.get('name')] = item.get('id') 
      tempList.append(item.get('name')) ##  temp list of project name ## 
      i += 1

    while projectId == [] :
      
      pid = takeInput('Enter your project id :','str', append=True).strip(',')
      for x in pid.split(','):
        if ( int(x) >= int(i) ):
          warn("Out of range.")
        else:
          """ geting value from templist for project dict name list
              and assigning val to projectId """
          projectId.append(projectDic[tempList[int(x)]])
        
    self.projectId  = projectId
    self.projectDic = json.dumps(projectDic)
    return projectId

  def getTaskId(self):

    self.getProjectId()
    
    taskIdDic = {}
    taskDic   = {}
    
    for projectId in self.projectId:

      print(colored("please select the task for", 'yellow'), colored("""%s ...!
            """% (getKey(json.loads(self.projectDic), projectId)) , 'blue'))
      url = baseUrl + '/portal/' + str(self.portalId) + '/projects/' + str(projectId) + '/tasks/'
      taskList = requests.get(url, params = self.params).content;
      i=0; taskId=[]; tempList = []; revTaskdic ={}
      
      for item in json.loads(str(taskList.decode('utf-8')))['tasks']:
        info('[' + str(i) + ']' + ':' + item.get('name'))
        taskDic[item.get('name')] = item.get('id')
        tempList.append(item.get('name'))
        i += 1

      while taskId == [] :

        tid = takeInput('Enter your task id : ','str', append=True).strip(',')
        for x in tid.split(','):
          if ( int(x) >= int(i) ):
            warn("Out of range.")
          else:
            """ geting value from templist for dic namlist and assign val to projectId """

            val = taskDic[tempList[int(x)]]
            taskId.append(val)
      taskIdDic[projectId] = taskId
      
    self.project = taskIdDic
    self.taskDic = json.dumps(taskDic)
    
    return taskIdDic

  def createConfig(self):

    import yaml as yml
    import os
    if os.path.isfile('config.yml'):
      try:
        data=yml.load(open('config.yml','r'))
        self.authToken  = data.get('authToken')
        self.portalId   = data.get('portalId')
        self.project    = data.get('project')
        self.projectDic = data.get('projectDic')
        self.taskDic    = data.get('taskDic')

      except Exception as e:
        error("Unable to load config.yml ") 

    else:
      self.getTaskId()
      ans= takeInput('Hey! Do you want to save this config for future use ? ' , 'str')
      if ans in ['y', 'Y' 'yes' 'YES']:

        warn("Writing to config.yml. Do not delete it...!")

        zohoDic = {}
        zohoDic['authToken']  = self.authToken
        zohoDic['portalId']   = self.portalId
        zohoDic['project']    = self.project
        zohoDic['projectDic'] = self.projectDic
        zohoDic['taskDic']    = self.taskDic
        try:
          import yaml

          f = open("config.yml", "a")
          f.write(yml.dump(zohoDic, indent=2 ,default_flow_style=False,explicit_start=True))
          f.close()
        except Exception as e:
          os.remove('config.yml')
          error("Unable to write config.yml ")
          
  def getDate(self):

    from datetime import date ,timedelta
    import datetime
    currentDay = date.today();
    today = currentDay.weekday()

    if today in [4, 5, 6] :
      wk = 'current'
    else:
      wk = 'last'
    ans = takeInput("Do want to fill for %s week ?[y/any]" %wk ,'str')
    
    if today is 0:  # Monday
      if ans in ['y','Y']:
        sSub = 7
        eSub = 3
      else:
        sSub = 0
        eSub = 0
    
    elif today is 1:  # Tuesday
      
      if ans in ['y','Y']:
        sSub = 8
        eSub = 4
      else:
        sSub = 1
        eSub = 0
    
    elif today is 2:  #  Wednesday 
      if ans in ['y','Y']:
        sSub = 9
        eSub = 5
      else:
        sSub = 2
        eSub = 0

    elif today is 3:   # Thursday
      if ans in ['y','Y']:
        sSub = 10
        eSub = 6
      else:
        sSub = 3
        eSub = 0

    elif today is 4:    # Friday  ## current True
      if ans in ['y','Y']:
        sSub = 4
        eSub = 0
      else:
        sSub = 11
        eSub = 7

    elif today is 5:    # Saturday ## current True
      if ans in ['y','Y']:
        sSub = 5
        eSub = 1
      else:
        sSub = 12
        eSub = 8
    
    elif today is 6:  # Sunday  ## current True
      if ans in ['y','Y']:
        sSub = 6
        eSub = 2
      else:
        sSub = 13
        eSub = 9

    self.startDay = currentDay - timedelta(days=sSub)
    self.endDay   = currentDay - timedelta(days=eSub)
    warn('Filling timesheet from %s to %s ' %(self.startDay,self.endDay))

  def __init__(self):
    pass
    # super(self.createConfig, self).__init__()


##################################################


class PostTimeLog(object):

  """docstring for PostTimeLog"""

  def configTimeLog(self):  
    _diff_time_log = False
    
    from datetime import date ,timedelta

    info("Do you want to enter datewise or average ?")
    timeAns = takeInput("'d' for date and 'c' for common :[d/c]",'str') 

    if timeAns in ['c','C']:
      self.timeLog = takeInput('Enter the time common time: ','int')
    else:
      _diff_time_log = True

    diff = abs((self.gd.endDay - self.gd.startDay).days)    
    t = 0
    tList = []; pList = [];confir = ''

    """  Mutltiple project multiple or single task  """ 
    if len(self.gd.project) > 1 or _diff_time_log:
      for key in self.gd.project:
        for item in self.gd.project[key]:
          info ('%d: %s --> %s' % (t, getKey(json.loads(self.gd.projectDic),key), getKey(json.loads(self.gd.taskDic),item)))
          tList.append(item) ## temp list of task id ## 
          t += 1

      for single_date in (self.gd.startDay + timedelta(n) for n in range(diff + 1)):
        if timeAns in ['c','C']:
          hrs = self.timeLog 
        else:
          hrs = takeInput("Enter the hour for date %s: " %single_date ,'int')
        if len(tList) > 1:
          ans = takeInput("Enter the project id for %s :" %single_date ,'int')
        else:
          ans = 0

        tid = int(tList[int(ans)])
        pid = next(iter({k for k, v in self.gd.project.items() if tid in v}))  
        
        if confir not in ['n','N','']:
          info("OK")
          # self.commitTimeLog(single_date.strftime('%m-%d-%Y'),hrs,pid,tid)
        else:
          warn("Filling timesheet for date %s project %s task %s " %(single_date,getKey(json.loads(self.gd.projectDic),pid), getKey(json.loads(self.gd.taskDic),tid)))
          confir = takeInput("Press any key to confirm:", 'str')
          if confir not in ['n','N',''] :
            info("OK")
            # self.commitTimeLog(single_date.strftime('%m-%d-%Y'),hrs,pid,tid)
  

    # """ single project multiple task """
    else:
      for key in self.gd.project:
        for item in self.gd.project[key]:
          info ('%d: %s --> %s' % (t, getKey(json.loads(self.gd.projectDic),key), getKey(json.loads(self.gd.taskDic),item)))
          
          tList.append(item) ## temp list of task id ## 
          t += 1

      """ Recursive date count """
      for single_date in (self.gd.startDay + timedelta(n) for n in range(diff + 1)):
        if timeAns in ['c','C']:
          hrs = self.timeLog 
        else:
          hrs = takeInput("Enter the hour for date %s: " %single_date ,'int')
        if len(tList) > 1:
          ans = takeInput("Enter the project id for %s :" %single_date ,'int')
        else:
          ans = 0

        tid = int(tList[int(ans)])
        pid = next(iter({k for k, v in self.gd.project.items() if tid in v}))
    
        if confir not in ['n','N','']:
          info("OK")
          # self.commitTimeLog(single_date.strftime('%m-%d-%Y'),hrs,pid,tid)
        else:
          warn("Filling timesheet for date %s project %s task %s " %(single_date,getKey(json.loads(self.gd.projectDic),pid), getKey(json.loads(self.gd.taskDic),tid)))
          confir = takeInput("Press any key to confirm:", 'str')
          if confir not in ['n','N','']:
            info("OK")
            # self.commitTimeLog(single_date.strftime('%m-%d-%Y'),hrs,pid,tid)

  """ Post time """
  def commitTimeLog(self,date,hrs,pid,tid):

    params = {
              "authtoken": self.gd.authToken,
              "date": str(date),
              "notes": "..",
              "bill_status": "Billable",
              "hours": str(hrs)
            }

    url = baseUrl + '/portal/' + str(self.gd.portalId) + '/projects/' + str(pid) + '/tasks/'+ str(tid) + '/logs/'
    timeLog  = requests.post(url, params = params);
    proj = getKey(json.loads(self.gd.projectDic),pid)
    info('')
    if timeLog.status_code == 200 or timeLog.status_code == 201 :
      info("Time %s hrs added for project %s date %s. " %(hrs,proj,date))
    else:
      error("""
      Unable to updade time log on project '%s' for date '%s'.
      Error code : %s""" %(proj,date,timeLog.content))

  def __init__(self):
    super(PostTimeLog, self).__init__()
    self.gd = GetDetails()
    self.gd.createConfig()
    self.gd.getDate()
    self.configTimeLog()

ptl = PostTimeLog()