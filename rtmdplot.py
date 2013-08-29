#!/usr/bin/python
# -*- coding: utf8 -*-

#from system import *
from struct import *
from collections import *
from math import sqrt
from datetime import *

import os,  stat;
import sys
import getopt


def ExDumpCSV(obj, filename="out.csv", separator=','):
	starttime = obj.startUSecTime + xstart
	dt = datetime.fromtimestamp(starttime / 1000000)
	out = "Start %s.%d" % (dt.strftime("%Y-%m-%d %H:%M:%S"), starttime % 1000000)
	
      
	out = out + " (delta in us)"
	for name in obj.name_td:
	  out = out + "%s%s" % (separator, name)
	  #print obj.name_tdv[name]

	names = [ i for i in obj.name_td ]
	valid = [ len(obj.name_td[i]) for i in obj.name_td ]
	idx =   [ 0 for i in obj.name_td ]
	z = 0
	
	tv =    [ 99999999999999999  for i in names ]
	for i in xrange(len(valid)):
	    if valid[i]:
		tv[i] =  obj.name_tdv[names[i]][0]
	
	while max(valid) > 0:
	    a = 0
	    av = tv[0]
	    for j in xrange(len(tv)):
	      if av > tv[j]:
		av = tv[j]
		a = j
	    
	    out = out + "\n%.3f" % tv[a]  #obj.name_tdv[names[a]][idx[a]]
	    for j in xrange(1+a):
	      out = out + separator
	    out = out + "%.3f" % obj.name_td[names[a]][idx[a]]
	    for j in xrange(len(idx)-a):
	      out = out + separator
	    
	    idx[a] = idx[a] + 1
	    if idx[a] >= len(obj.name_td[names[a]]):
		valid[a] = 0
		tv[a] = 99999999999999999
	    else:
		tv[a] = obj.name_tdv[names[a]][idx[a]]
	
	
	f = open(filename, "w")
	try:
	    f.write(out)
	finally:
	    f.close()


def PreprocessTimeDiff(obj, name, startFrom, dropstime=0, maxvalue=None, skipBad=True):  
	global xstart
        name_td = []
        name_tdv = []
        numplots = 0

	zeroign = 1

	values = []
	for j in xrange(len(obj.name_time[name])):
	    if obj.name_val[name][j] not in values:
		values.append(obj.name_val[name][j])
		
	print "PreprocessTimeDiff:%s -> %s" % (name, values)
	if len(values) < 2:	    
	    return

	tdiffs = [[] for j in xrange(len(values) - zeroign)]
	ttime = [0 for j in xrange(len(values))]
	atime = [0 for j in xrange(len(values))]
	mtime = [0 for j in xrange(len(values))]
	stime = [0 for j in xrange(len(values))]
	
	sttime = []

        start = obj.name_time[name][0]
        #yprev = d.name_val[name][0]
        idx   = 0
        previdx = 0
        doAppend = False
        skip = False
        
        if start >= startFrom:
            sttime.append(start)
            doAppend = True
        
	for j in range(1, len(obj.name_time[name])):
	      idx = (idx + 1) % len(values)
	      v = obj.name_val[name][j]
	      
	      cur = obj.name_time[name][j]
	      
	      if idx == 0:
	      	if cur >= startFrom:
	      	   doAppend = True
	      	   #print "Append %g idx %d" % (obj.name_time[name][j], idx)
		   sttime.append(obj.name_time[name][j])
		   skip = False
	      
	      #sorting and data check
	      if values[idx] != v:  
		  if (j+1 == len(obj.name_time[name])):
		      break
		  
		  if (j+1 < len(obj.name_time[name])) and values[idx] == obj.name_val[name][j+1] and obj.name_time[name][j+1] == obj.name_time[name][j]:
		      #exchange
		      obj.name_val[name][j] = obj.name_val[name][j+1]
		      obj.name_val[name][j+1] = v
		      v = obj.name_val[name][j]   
		  else:
		      cnt = 1
		      while (j+cnt < len(obj.name_time[name])) and obj.name_time[name][j+cnt] == obj.name_time[name][j]:
			  cnt = cnt + 1
		      if cnt > 1:
			  stvals = [obj.name_val[name][j+jj] for jj in xrange(cnt)]
			  #print stvals			  
			  nvals = [-1 for jj in xrange(cnt)]
			  nidx = previdx
			  for jj in xrange(cnt):
			      nidx = (nidx + 1) % len(values)
			      #print values[nidx]
			      if values[nidx] in stvals:
				  nvals[jj] = values[nidx]
			      else:
				  break
			  #print nvals
			  if jj == cnt - 1:
			      for jj in xrange(cnt):
				  obj.name_val[name][j+jj] = nvals[jj]
			      v = obj.name_val[name][j]
			  else:
			      print "NOTICE1: data_prev = %d  data = %d but seq_prev = %d seq = %d on %f" % (obj.name_val[name][j-1], v, values[previdx], values[idx], obj.name_time[name][j] - xstart)
			      return
		      else:
			      print "NOTICE2: data_prev = %d  data = %d but seq_prev = %d seq = %d on %f" % (obj.name_val[name][j-1], v, values[previdx], values[idx], obj.name_time[name][j] - xstart)
			      if not skipBad:
				return
			      else:
				      #sttime.remove(obj.name_time[name][j-1])
				      if doAppend:
					preidx = idx
					previdx = idx = obj.name_val[name][j + 1]
					qqq = sttime.pop()
					#print "Pop %g  idx %d -> %d " % (qqq, preidx, idx)
					skip = True
				      continue
			

	      if doAppend and not skip:
	         if previdx < len(values) - zeroign:
		    tdiffs[previdx].append(cur - start)
		    #print "Append End %g  idx %d" % (cur - start, idx)
		    
	         #total time
	         ttime[previdx] = ttime[previdx] + (cur - start)
	      
	         #max time
	         if (cur - start) >  mtime[previdx]:
		    mtime[previdx] = cur - start
	      
	      start = cur	      
	      previdx = idx

	for j in xrange(len(values)):
	    atime[j] = ttime[j] * 1.0 / len(tdiffs[j if j < len(values) - zeroign else 0])
	
	for jj in xrange(len(values) - zeroign):
	    for j in xrange(len(tdiffs[jj])):
		stime[jj] = stime[jj] + (atime[jj] - tdiffs[jj][j])*(atime[jj] - tdiffs[jj][j])
	
	for j in xrange(len(values) - zeroign):
	    stime[j] = sqrt(stime[j] / len(tdiffs[j]))

        def format_array(ar):
            j = [ "%.3f" % x for x in ar ]
            return "[" + reduce(lambda x, y: x + ", " + y, j) + "]"
	
        print "PreprocessTimeDiff:%s -> %s  Tot %s  Avg %s  Max %s  Sig %s  -> %d" % (
                name, values, format_array(ttime), format_array(atime), format_array(mtime), format_array(stime), len(sttime))
	 
	try:
	    obj.pre_sttime
	except AttributeError:
	    obj.pre_sttime = {}
	    obj.pre_tdiffs = {}
	
	try:
	    obj.stat_ttime
	except AttributeError:
	    obj.stat_ttime = {}
	    obj.stat_atime = {}
	    obj.stat_mtime = {}
	    obj.stat_stime = {}	  

	obj.pre_sttime[i] = sttime
	obj.pre_tdiffs[i] = tdiffs
	
	obj.stat_ttime[i] = ttime
	obj.stat_atime[i] = atime
	obj.stat_mtime[i] = mtime
	obj.stat_stime[i] = stime
      

def SummaryStat(obj, name, doout=1, combine=True):
    stat_names = []
    
    if combine:
        for i in obj.name_time:
            if i.startswith(name):
                stat_names.append(i)
    else:
        stat_names.append(name)

    if len(stat_names) == 0:
	return

    print stat_names
    donext = 1
    while donext:
        try:
	    cnt = len(obj.stat_ttime[stat_names[0]])
	    donext = 0
        except:
	    stat_names.pop(0)
	
    
    for i in stat_names:
	try: 
	  if len(obj.stat_ttime[i])  != cnt:
	      print "ignoring %s in stat" % i
	      stat_names.remove(i)
	except KeyError:
	      stat_names.remove(i)

    names = sorted(stat_names)
       
    ttime = [0 for j in xrange(cnt)]
    atime = [0 for j in xrange(cnt)]
    mtime = [0 for j in xrange(cnt)]
    stime = [0 for j in xrange(cnt)]
    
    for i in names:
        try:
	  for jj in xrange(cnt):
	    ttime[jj] = ttime[jj] + obj.stat_ttime[i][jj]
	    atime[jj] = atime[jj] + obj.stat_atime[i][jj]
	    
	    if mtime[jj] < obj.stat_mtime[i][jj]:
		mtime[jj] = obj.stat_mtime[i][jj]
	    
	    stime[jj] = stime[jj] + obj.stat_stime[i][jj]*obj.stat_stime[i][jj]
	except KeyError:
	    names.remove(i)

	
    for jj in xrange(cnt):
	atime[jj] = atime[jj] * 1.0 / len(names)
	stime[jj] = sqrt(stime[jj] / len(names))
    
    print "Statistics for %s" % name
    string = "Name      "
    for i in xrange(cnt):
	string = string + "Avg%d       " % i
    for i in xrange(cnt):
	string = string + "Sig%d       " % i
    for i in xrange(cnt):
	string = string + "Max%d       " % i
    string = string + "\n" + "-" * (cnt*33 + 11)
    
    for i in names:
      try:
        j = len(obj.pre_tdiffs[i][0])
        print "%s - > %d" % (i,j)
	string = string + "\n%-10s" % i
	for j in xrange(cnt):
	    string = string + "% 10.2f " % obj.stat_atime[i][j]
	for j in xrange(cnt):
	    string = string + "% 10.2f " % obj.stat_stime[i][j]
	for j in xrange(cnt):
	    string = string + "% 10.2f " % obj.stat_mtime[i][j]
      except KeyError:
	    names.remove(i)
	
    if len(stat_names) > 0:
	string = string + "\n" + "-" * (cnt*33 + 11)
	string = string + "\n%-10s" % ("Total" + "_" + name)
	for j in xrange(cnt):
	    string = string + "% 10.2f " % atime[j]
	for j in xrange(cnt):
	    string = string + "% 10.2f " % stime[j]
	for j in xrange(cnt):
	    string = string + "% 10.2f " % mtime[j]

    print string

    f = open("%s/%s.stat" % (dirname, name) , "w")
    try:
	f.write(string)
    finally:
	f.close()
	
    f = open("%s/%s.stat.dat" % (dirname, name) , "w")
    try:
	for i in names:
	  try:
	    numplots = min([len(obj.pre_tdiffs[i][h])  for h in xrange(len(obj.pre_tdiffs[i]))])
	    for j in xrange(numplots):
		string = ""
		for k in xrange(len(obj.pre_tdiffs[i])):
		  string = "%s% 10.2f " % (string, obj.pre_tdiffs[i][k][j])
		f.write(string)
		f.write("\n")
	  except KeyError:
	    names.remove(i)
    finally:
	f.close()



class ParseRTMDMerge:
    def __init__(self, parsed):
	self.filename = "Merged"
	
        self.name_time = {}
        self.name_val  = {}
        
        self.name_td   = {}  # for dump
        self.name_tdv  = {}  # for dump
        self.plottype  = {}  # for dump        
	
	self.startUSecTime = 0

	name_idx = {}
	
	ustm = [parsed[j].startUSecTime for j in xrange(len(parsed))]
	mum = min(ustm)
	self.startUSecTime = mum

        for i in xrange(len(parsed)):
	    ustm[i] = ustm[i] - mum
	    parsed[i].ApllayOffset(ustm[i])
	    
	    for name in parsed[i].name_time:
		if name not in self.name_time:
		    self.name_time[name] = []
		    self.name_val[name]  = []
		    #print "Merging %s" % name
		    
	print ustm

	for name in self.name_time:
	    idx = [0 for j in xrange(len(parsed)) ]
	    avail = [name in parsed[j].name_time  for j in xrange(len(parsed))]
	    
	    print "%32s is %s" % (name, avail)
	    
	    doit = True
	    # Перебор по индексу в массиве
	    while doit:
		minTime = []
		minIdx = 0
		# Перебор по файлам
		for i in xrange(len(idx)):
		    if (avail[i]):
			try:
			    mn = parsed[i].name_time[name][ idx[i] ]
			    if ( len(minTime) == 0):
				minTime.append(mn)
				minIdx = i
			    else:
				if min(mn, minTime[0]) == mn:
				    minTime[0] = mn
				    minIdx = i
			except:
			    avail[i] = False
			    
		if ( len(minTime) == 0):
		    doit = False
		else:
		    self.name_time[name].append(minTime[0])
		    self.name_val[name].append(parsed[minIdx].name_val[name][ idx[minIdx] ])

		    idx[minIdx] = idx[minIdx] + 1

	    #print self.name_time[name]
	    #print self.name_val[name]
		
	#TODO: Add merging system data
        self.sname_time = parsed[0].sname_time
        self.sname_val  = parsed[0].sname_val

    def DumpCSV(self, filename="out.csv", separator=','):
	ExDumpCSV(self, filename, separator)


class ParseRTMD:
    def __init__(self, filename, fmt="="):
        self.filename = filename
        
        self.name_time = {}
        self.name_val  = {}
        self.name_clk  = {}
        
        self.name_td   = {}  # for dump
        self.name_tdv  = {}  # for dump
        self.plottype  = {}  # for dump
        
        # For system variables
        self.sname_time = {}
        self.sname_val  = {}
        self.sname_clk  = {}
        
        f = open("%s.rtmd" % filename , "rb")
        try:
	    ver = None
            while True:
	        clock = 0
	        sec =  0
	        usec = 0
	        line = 0
	        val =  0	      
                ####################################################
                ## Binary reader
                
                chunk = f.read(16)
                if chunk == "":
                    break

                if ver == None and chunk[15] != 0:
		  ver = 1
		elif ver == None:
		  ver = 0

		if (ver == 1):
		  name = chunk[0:15].split("\0")[0]
		  flag = chunk[15]
		else:
		  name = chunk.split("\0")[0]
		
                chunk = f.read(16)
                if ver == 1 and flag == 'I':
		  sec, usec, clock = unpack("%sIIQ" % fmt,  chunk)
		elif ver == 1 and flag == 'C':
		  clock, line, val = unpack("%sQIi" % fmt,  chunk)
		
                sec, usec, line, val = unpack("%sIIii" % fmt,  chunk)
                
                ## End of binary reader
                ####################################################

                # Threaded name fixup
                if flag == 'C' and line < 0 and name[0] != '#':
                    name = name + "@%d" % (-line)
                
                #print '%s \tat %d.%d (%d) :\t %d ' %  (name,  sec, usec, line, val )
                if name[0] == '#':
                    if name not in self.sname_time:                       self.sname_time[name] = []
                    self.sname_time[name].append(sec * 1000000 + usec);
                    
                    if name not in self.sname_val:                        self.sname_val[name] = []
                    self.sname_val[name].append(val);
                    
                    if name not in self.sname_clk:                        self.sname_clk[name] = []
                    self.sname_clk[name].append(clock);
                    
                else:
                    if name not in self.name_time:                       self.name_time[name] = []
                    self.name_time[name].append(sec * 1000000 + usec);
                    
                    if name not in self.name_val:                        self.name_val[name] = []
                    self.name_val[name].append(val)
                    
                    if name not in self.name_clk:                        self.name_clk[name] = []
                    self.name_clk[name].append(clock);
        finally:
    	    f.close()            
                    
	self.startUSecTime = 0
        if "#cycle" in self.sname_clk:
	    self.Cycle()
        if "#init" in self.sname_time:
            self.ParseGran()
        if "#sync_sec" in self.sname_time and "#sync_usec" in self.sname_time:
            self.ParseSync()
            self.sync_present = 1
        else:
            self.sync_present = 0
            
        #self.DumpCSV()

    def Cycle(self):
        mx  = len(self.sname_time["#cycle"]) - 1
        mxe = len(self.sname_time["#cycleend"]) - 1
        #print "S %d -> %d" % (self.sname_time["#cycle"][0], self.sname_clk["#cycle"][0])   
        
        stt = (1.0*self.sname_time["#cycle"][mx] + self.sname_time["#cycle"][0])/2.0
        stc = (self.sname_clk["#cycle"][mx] + self.sname_clk["#cycle"][0])/2
        
        stte = (1.0*self.sname_time["#cycleend"][mxe] + self.sname_time["#cycleend"][0])/2.0
        stce = (self.sname_clk["#cycleend"][mxe] + self.sname_clk["#cycleend"][0])/2
        
        odusec  = stte - stt
        odclock = stce - stc
        
        print "S %d -> %d  SE %d -> %d  => OVERALL (%.6fns, %.3fMHz)" % (stt, stc, stte, stce,   odusec * 1000.0 / odclock,  odclock * 1.0 / odusec)
        
        dusec = self.sname_time["#cycle"][mx] - self.sname_time["#cycle"][0]
        dclock =  self.sname_clk["#cycle"][mx] - self.sname_clk["#cycle"][0]
        dusece = self.sname_time["#cycleend"][mxe] - self.sname_time["#cycleend"][0]
        dclocke =  self.sname_clk["#cycleend"][mxe] - self.sname_clk["#cycleend"][0]
        
	print "D %d -> %d  DE  %d -> %d  " % (dusec, dclock, dusece, dclocke)
	print "Resolution deviation  %.6f nsec (%.3f MHz)  --  %.6f nsec (%.3f MHz) " % ( dusec * 1000.0 / dclock,  dclock * 1.0 / dusec,        dusece * 1000.0 / dclocke,  dclocke * 1.0 / dusece)
	
	print "Start rec: %s.%d" % ((datetime.fromtimestamp(self.sname_time["#cycle"][0] / 1000000)).strftime("%Y-%m-%d %H:%M:%S") , self.sname_time["#cycle"][0] % 1000000)
	
	
			
	self.cycleRes   = ( odusec * 1000.0 / odclock ) #( dusec * 1000.0 / dclock )
	self.cycleFDT   = stt #self.sname_time["#cycle"][0]
	self.cycleCDT   = stc #self.sname_clk["#cycle"][0]
	self.cycleScale = odusec * 1.0 / odclock #dusec * 1.0 / dclock
	
	self.startUSecTime = self.cycleFDT
	
	lx = len(self.sname_time["#cyctst"]) - 1
	dtclock = self.sname_clk["#cyctst"][lx] - self.sname_clk["#cyctst"][0]
	print "Penalty    %.1f nsec (%d clocks)" % (dtclock * 1000.0 * self.cycleScale / lx, dtclock / lx)
	
	for name in self.name_val:
	  print "Shifting %s" % name
	  nlen = len(self.name_val[name]) 
	  for i in xrange(nlen):
	      clck = self.name_clk[name][i]
	      self.name_time[name][i] = (clck - self.cycleCDT) * self.cycleScale
	

    def ParseGran(self):
        deltas = sum([(self.sname_time["#init"][i+1] - self.sname_time["#init"][i])**2 for i in xrange(len(self.sname_time["#init"]) - 1)])
        self.m_sigma = sqrt(deltas / (len(self.sname_time["#init"]) - 1)) 
        self.m_mean = (self.sname_time["#init"][-1] - self.sname_time["#init"][0]) / len(self.sname_time["#init"])

    def ParseSync(self):
        dlen = len(self.sname_val["#sync_sec"])
        #print self.sname_val["#sync_sec"]
        #print dlen
        sync_time = [ i for i in self.sname_time["#sync_sec"] ]
        sync_rtime = [ self.sname_val["#sync_sec"][i]*1000000 + self.sname_val["#sync_usec"][i]
                                for i in xrange(dlen) ]
        
        rttl_d = [ sync_time[i+1] - sync_time[i] for i in xrange(len(sync_time)-1)]
        rttr_d = [ sync_rtime[i+1] - sync_rtime[i] for i in xrange(len(sync_rtime)-1)]
        
        self.rttl_mean =  sum(rttl_d) / dlen 
        self.rttl_sigma = sqrt(sum([i**2 for i in rttl_d])) / ( dlen - 1)
        
        self.rttr_mean =  sum(rttl_d) / dlen 
        self.rttr_sigma = sqrt(sum([i**2 for i in rttr_d])) / ( dlen - 1)
        
        lt_time = sum(sync_time)  / dlen 
        rt_time = sum(sync_rtime) / dlen 
        self.roffset = (lt_time - rt_time)*1000000 - (self.rttl_mean + self.rttr_mean)/4
        
        #print "Local  RTT=%.1f 3Sigma=%.1f" % (self.rttl_mean,  3*self.rttl_sigma)
        #print "Remote RTT=%.1f 3Sigma=%.1f" % (self.rttr_mean,  3*self.rttr_sigma)
        #print " %s: Remote offset = %f Sec" % (self.filename,  self.roffset)
    
    def ApllayOffset(self, timeOffset):
        for n in self.name_time:
            for i in xrange(len(self.name_time[n])):
                self.name_time[n][i] = self.name_time[n][i] + timeOffset
                
        self.startUSecTime = self.startUSecTime - timeOffset
                
    def DumpCSV(self, filename="out.csv", separator=','):
	ExDumpCSV(self, filename, separator)
        
class Settings:
    class Style:
        def __init__(self, style=None):
            self.limit = None
            self.type = "imp"
            self.fullname = style
            
            if style != None:
                vals = style.split(':')
                self.type = vals[0]
                if len(vals) > 1:
                    self.limit = float(vals[1])
                elif self.type == "tdiffms":
                    self.limit = 1000
                elif self.type == "tdiffus":
                    self.limit = 1000

            self.CheckStyle()

        def CheckStyle(self):
             known_types = ("imp", "tdiffms", "auto", "none", "tdiffus")
             if self.type not in known_types:
                print "Unknown type %s!\n" % (self.type)
                sys.exit(-1)
            
    def __init__(self, sysargv=sys.argv):
        self.filenames = []
        self.custom_styles = {}
        self.params = {}
        self.merge = False
        self.le = False
        self.be = False
        self.statAll = False
        #self.ds = "imp"
        self.ds = "auto"
        self.linestyle = "dots"
        self.statNames = None
        self.startFrom  = 0
        
        argv = sysargv[1:]
        if len(argv) < 1:
            print "Usage: %s [--nodots|--cross|--merge|--le|--be|--stat=name1,name2] filename [filename2] [variable=imp|tdiffms|none]\r" % sysargv[0]
            sys.exit(0)
        
        param = 0
        for v in argv:
            s = v.split('=')
            if len(s) == 2:
        	try:
        	    if s[0] == "--stat":
        		print "Will calculate stat for %s" % s[1]
        		self.statNames = s[1].split(',')
        	    elif s[0] == '--from':
        		print "Perform data from %s sec" % s[1]
        		self.startFrom = float(s[1])*1000*1000
        	    else:
        		break
        	except:
        	    print "Incorrect option"
        	    exit -3
            elif len(s) == 1:
		#print v
		try:
		    if v == "--merge":
			self.merge = True
		    elif v == "--stat-all":
			self.statAll = True
		    elif v[0:8] == "--defst-":
			self.ds = v[8:]
			print "> Using default plot style '%s'" % self.ds
                    elif v == "--nodots":
                        self.linestyle = "nodots"
                        print "> Using FILLED CRUVE"
		    elif v == "--cross":
			self.linestyle = ""
			print "> Using CROSES"
		    elif v == "--le" and self.be == False:
			self.le = True
			print "> Using little-endian decoding"
		    elif v == "--be" and self.le == False:
			self.be = True
			print "> Using big-endian decoding"
		    elif v[0:1] == "--":
			print "Incorrect usage of '%s'\r\n" % v
			exit -1
		    else:
			self.filenames.append(v[: -5] )
		except:
		    self.filenames.append(v[: -5] )
            else:
                break
            param = param + 1

        for h in argv[param:]:
            param, value = h.split('=')
            if (param[0] == '-'):
                self.params[param[1:]] = value
            else:
                self.custom_styles[param] = Settings.Style(value)
    

conf = Settings()
fmt = "="
if conf.be: fmt = ">" 
if conf.le: fmt = "<" 
data = [ParseRTMD(f, fmt) for f in conf.filenames]

if conf.merge:
      print "Merging all data..."
      dataMerged = ParseRTMDMerge(data)
      
      #exit (0)
      data = [ dataMerged ]

# Auto sync 2 RTMD files if possible
if (len(data) == 2):
    if data[0].sync_present == 1:
        syncid = 0
    elif data[1].sync_present == 1:
        syncid = 1
    else:
        syncid = None
        
    if syncid != None:
        print "Applaying auto offset to %s (offset = %f Sec)" % (data[1-syncid].filename,  data[syncid].roffset)
        data[1-syncid].ApllayOffset(data[syncid].roffset)


# Default directory and output filenames
filename = os.path.basename(conf.filenames[0])
dirname = "out"
if len(data) == 1:
    dirname = data[0].filename;
try:
    print "Mkdir %s" % dirname
    os.mkdir(dirname)
except OSError:
    pass


# GNUPlot script generating
plots = sum([len(i.name_val) for i in data])


linestyle = "with linespoints"

if conf.linestyle != None:
  if conf.linestyle != "":
    linestyle = "with %s " % conf.linestyle
  else:
    linestyle = ""

print "LINESTYLE=%s" % linestyle

script = ""

def fillHscipt():
    global hscript
    size = "1200,920"
    if "size" in conf.params: size = conf.params["size"]
    
    hscript = "#!/usr/bin/gnuplot\n"
    hscript = hscript + "set terminal png nocrop enhanced font arial 8 size %s\n" % size
    hscript = hscript + "set output '%s.png'\n" % filename
    hscript = hscript + "set multiplot layout %d, 1 \n" % plots #len(name_val) 
    hscript = hscript + "set lmargin 8\n"
    if "xtics" in conf.params:
	hscript = hscript + "set xtics %s\n" %  conf.params["xtics"]

gstart = conf.startFrom

xstart = 0xFFFFFFFFFFFFFFF
xend = 0.0
for j in data:
    for i in j.name_time:
        xstart = min( xstart,  j.name_time[i][0])
        xend = max ( xend,   j.name_time[i][-1])


print "Duration [%f:%f]  (%f sec)\n" % (xstart/1000000.0,  xend/1000000.0,  (xend - xstart)/1000000.0)
script = script + "set xrange [%f:%f] \n"  %  (gstart,  xend - xstart)

k = 1
defstyle = Settings.Style(conf.ds)


    
for d in data:
  try:  
      print " %s: measure error     %.1f + %.1f  uSec (Mean + 3 Sigma)" % (d.filename,  d.m_mean,  3*d.m_sigma)
  except:
      pass
  d.styles = {}
  for i in d.name_time:
    fname = '%s/%s.dat' % (d.filename, i)

    ymin = min(d.name_val[i])
    ymax = max(d.name_val[i])
    
    style = defstyle
    fullstname = "%s@%s" % (i, d)
    if fullstname in conf.custom_styles:
        style = conf.custom_styles[fullstname]    
    elif i in conf.custom_styles:
        style = conf.custom_styles[i]
    
    print "%20s: %6d items  ymin=%4d ymax=%4d \t start=%f  stop=%f  style=%s" % (i, len(d.name_val[i]),  ymin, ymax,  
                                  (d.name_time[i][0]-xstart)/1000000.0, (d.name_time[i][-1]-xstart)/1000000.0,  style.fullname)
    
    if len(data) > 1:
        dataname = "%s@%s" % (i, d.filename)
    else:
        dataname = i
    datafilename = "%s.dat" % (dataname)
    fname = '%s/%s' % (dirname, datafilename)

    tdls = "with filledcurve"
    no_zeroes = 0
    if conf.linestyle == "" or conf.linestyle == "dots":
        no_zeroes = 1
        tdls = linestyle

    if style.type == 'auto':
        if ymin == 0 and ymax == 1:
            style = Settings.Style('tdiffms')
            print "%20s: seems to be time measuring" % i
        else:
            print "%20s: defaulting to value plot" % i
    d.styles[i] = style

    if style.type == 'imp':

        script = script + "plot '%s' t \"%s\" %s lc %d\n" % (datafilename, dataname, tdls, k)
        f = open(fname, "w")
        try:
            yprev = d.name_val[i][0]
            for j in xrange(len(d.name_time[i])):
              if d.name_time[i][j] - xstart > conf.startFrom:
                if not no_zeroes:
                    f.write ('%f\t%d\n' % (d.name_time[i][j] - xstart , yprev ))
                f.write ('%f\t%d\n' % (d.name_time[i][j] - xstart , d.name_val[i][j] ))
                yprev = d.name_val[i][j]
                
        finally:
    	    f.close()
                
    elif style.type == 'tdiffms' or style.type == 'tdiffus':
        try:
            PreprocessTimeDiff(d, i, conf.startFrom)

            d.plottype[i] = style.type

            tdiffms = style.limit
            numplots = 0
            div = 1 if style.type == 'tdiffus' else 1000

            f = open(fname, "w")
            try:
                cnt = len(d.pre_tdiffs[i])
                numplots = min([len(d.pre_tdiffs[i][h])  for h in xrange(cnt)])

                for j in xrange(numplots):
                    oline = [(d.pre_tdiffs[i][h][j]/div)  for h in xrange(cnt)]
                    line = [sum(oline[:h+1])   for h in xrange(cnt)]
                    f.write ("%f\t%s\n" % (d.pre_sttime[i][j]-xstart, reduce(lambda x,y: "%s\t%s" % (x,y), line )))

            finally:
                f.close()

            if numplots > 0:
              if cnt > 1:
                line = ["%s '%s' u 1:%d t \"%s:%d->%d (ms)\" %s lc %d" % ("plot" if j == 0 else "    ",
                                              datafilename, j+2, dataname, j+1, j+2 if j+2<cnt else 0, tdls, k+j) for j in xrange(cnt)  ]
                script = script + reduce(lambda x,y: "%s,\\\n%s" % (x,y), line) + "\n"
              else:
                script = script + "plot '%s' t \"%s (%s, MAX=%d)\" %s lc %d\n" % (
                                             datafilename, dataname,  style.type,  tdiffms, tdls, k)
            else:
                print "No timediff data in %s!" % dataname
                plots = plots - 1
        except:
            print "Error during processing time diff in %s! skipping it" % dataname
            plots = plots - 1

    else: #if style == 'none':    
        script = script + "plot '%s' t \"%s\" %s lc %d\n" % (datafilename, dataname, tdls, k)
        f = open(fname, "w")
        try:
            for j in xrange(len(d.name_time[i])):
                f.write ('%f\t%d\n' % (d.name_time[i][j] - xstart , d.name_val[i][j] ))
                
	finally:
	    f.close()

    k = k + 1



if conf.statAll:
  for d in data:
    for i in d.name_time:
      if d.styles[i].type == 'tdiffms' or d.styles[i].type == 'tdiffus' :
        SummaryStat(d, i, 1, False)
        m = d.stat_atime[i][0] + 2*d.stat_stime[i][0]
        delim = 0.1
        while m / delim > 2000:
            delim = delim * 2
            if m / delim > 2000:
                delim = delim * 2
                if m / delim > 2000:
                    delim = delim * 1.25
                    if m / delim > 2000:
                         delim = delim * 2

        path_as, dummy = os.path.split(os.path.abspath(sys.argv[0]))
        print delim
        scmd = "(cd %s; %s/auto-stat.py -f %s.stat.dat -y %g >> ../stat.log)" % (dirname, path_as, i, delim)
        os.system(scmd)
else:
  if conf.statNames != None:
   for i in conf.statNames:
    print "Calculating stat for %s" % i
    SummaryStat(d, i)
    

fillHscipt()

f = open("%s/%s.rtmd.plt" % (dirname, filename), "w")
try:
    f.write(hscript)
    f.write(script)
finally:
    f.close()


os.chmod("%s/%s.rtmd.plt" % (dirname, filename),
         stat.S_IRWXU or stat.S_IXGRP or stat.S_IRGRP or stat.S_IXOTH or stat.S_IROTH)


os.system("( cd %s; ./%s.rtmd.plt )" % (dirname, filename))

