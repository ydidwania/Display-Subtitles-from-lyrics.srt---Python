#!/usr/bin/env python
from datetime import datetime,timedelta,time
from time import sleep
import sys, os, curses
openTime=datetime.now() #stores the time of start of document
w=curses.initscr() 
curses.curs_set(0) #the cursor is hidden
nol=0 #Number of lines after which new subtitle should be displayed

#Each subtitle block is made into a object	
class Subtitle():
	def __init__(self,num,starttime,endtime,sub):
		self.num=num
		self.start=starttime
		self.end=endtime
		self.text=sub
		self.x=0 #coordinates of display of the subtitle
		self.y=0
		self.style=[]

	def displaySub(self):
		movePageEnd() 
		self.addStyle()
		self.cleanText()
		global nol 
		self.y,self.x=w.getyx()
		#check for html tags
		#if('<'in self.text and '>' in self.text): 
		#	style=self.cleanText()
		for i,j in enumerate(self.text):
			
			w.addstr(j,self.style[int(i)]) # Adds the sub to the window object, w
		nol+=self.text.count('\n')+1 
		w.noutrefresh() # updates virtual window
		wait(self.start) # wait for the start time of the sub
		curses.doupdate() # updates the terminal window to display the sub

	def removeSub(self):
		global nol
		w.move(self.y,self.x)	# moves cursor to start coordinates of the sub	
		for i in range(0,self.text.count('\n')+1):
			w.clrtoeol() # erase from cursor to end of line
			moveDown() 
		w.noutrefresh() # updates the virtual window

		# if the current sub was displayed at the bottommost
		# the nol is updated to display the next sub from the start of the current 
		if(nol+1,0==w.getyx):
			nol=self.y

		#wait for the end time of sub to update the terminal window	
		wait(self.end)
		curses.doupdate()

	# Removes all html tags from text 	
	def cleanText(self):
		p=1
		q=0
		while p>-1 and q>-1:
			self.text=self.text[0:p]+self.text[q+1:]
			p=self.text.find('<')
			q=self.text.find('>',p)

			

	def addStyle(self):
		lb=[]
		lu=[]
		i=0
		s=self.text

		while i<len(s):
			f=0
			if(s[i:i+3]=='<b>'):
				lb.append(1)
				i=i+3
				continue
			if(s[i:i+4]=='</b>'):
				lb.pop()
				i=i+4
				continue
			if(s[i:i+3]=='<u>'):
				lu.append(1)
				i=i+3
				continue
			if(s[i:i+4]=='</u>'):
				lu.pop()
				i=i+4
				continue
			if lb:
				f|= curses.A_BOLD
			if lu:
				f|=curses.A_UNDERLINE
			self.style.append(f)
			i=i+1

			







# Converts the time from String to a datetime object
def durtotime(strdur):
	#print strdur
	if(',' in strdur):
		t=strdur.split(',')
	else:
		t=strdur.split('.')
	t[0]=t[0].split(':')
	t[0].append(t[1])
	t=[int(x) for x in t[0]]
	d=timedelta(hours=t[0], minutes=t[1], seconds=t[2], milliseconds=t[3])
	actualTime=openTime+d
	return(actualTime)

# Returns control at time
def wait(time):
	while time>datetime.now():
		sleep(0.001)
	return 

# Executes the events in Queue
# q=[[time,Subtitle.num,start1 or end0],......] 
def displayQueue(q,SubList):
	global nol
	nol=0
	for i in q:
		if(i[2]): 
			SubList[i[1]].displaySub()
		else:
			SubList[i[1]].removeSub()
	w.erase() #Clear window after queue is executed

# Move Cursor to End of Display
def movePageEnd():
	global nol
	w.move(nol,0)

#Move Cursor to start of next line
def moveDown():
	y,x=w.getyx()
	w.move(y+1,0)

if __name__ == "__main__":
	
	f=open("lyrics.srt",'r')
	lines = f.readlines()
	lines=[x.strip() for x in lines]# remove '\n' from each line
	lines[0]=lines[0].replace('\ufeff','') #remove Byte Order Mark from start of File
	pos=[i-1  for i in range(len(lines)) if '-->' in lines[i]] #Stores indices of start of each Sub Block
	pos.append(len(lines)+1) 
	SubList=[] #List of Subtitle objects
	
	#Convert each sub in Subtitle Object and Add to SubList
	for i,j in enumerate(pos[:-1]):
		times=[durtotime(t) for t in lines[j+1].split(' --> ')] #string time to datetime objects 
		text=[lines[x] for x in range(j+2,pos[i+1]-1)] #list of lines in Subtitle text
		text='\n'.join(text) 
		SubList.append(Subtitle(i+1,times[0],times[1],text)) # Subtitle(num,starttime,endtime,subtitle)
		
	i=0

	#Makes a queue of consecutive overlapping Subs and executes the same
	while  i<len(SubList):
		q=[]
		j=SubList[i]

		#Adds current Sub to the queue
		q.append([j.start,i,1])
		q.append([j.end,i,0])

		#Check for Subs overlapping with Subs in Queue and add them
		if i<len(SubList)-1:
			while(SubList[i+1].start<q[-1][0]):
				i=i+1
				j=SubList[i]
				q.append([j.start,i,1])
				q.append([j.end,i,0])

				# Sort the Queue by the times of the events
				q.sort(key=lambda x: x[0]) 

				if i==len(SubList)-1:
					break
		
		displayQueue(q,SubList)
		i=i+1	
	curses.endwin()



		
		
