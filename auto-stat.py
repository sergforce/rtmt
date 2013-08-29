#!/usr/bin/python
# -*- coding: utf8 -*-

#from system import *
from struct import *
from collections import *
from math import sqrt
from datetime import *

import os, stat;
import sys
import getopt

from numpy import *

def argmax(iterable): return max((x, i) for i, x in enumerate(iterable))[1]

def arg(iterable, v):
  for i, x in enumerate(iterable):
    if x == v:
      return i

def GetTotalLineFromFile(filename, searchi):
    print "GetTotalLineFromFile: %s" % filename
    f = open(filename, "r")
    try:
      for ln in f.readlines():
          if ln.startswith(searchi):
              return ln
    finally:
      f.close()

def GetWholeFile(filename):
    f = open(filename, "r")
    try:
      string = f.read().split("\n")
    finally:
      f.close()

    for i in xrange(len(string)):
       string[i] = string[i].split()

    return string


def print_h(x, dic_t, dic_c):
    string = "%20s  %s" % (str(dic_t[x[0]] if x[0] in dic_t else ""), reduce(lambda x, y: "%s %22s" % (x, y), [dic_c[h] for h in x[1:]]))
    print string
    return string
    
def print_m(x, dic_t):
    string = "%20s  %s" % (str(dic_t[x[0]] if x[0] in dic_t else ""), reduce(lambda x, y: "%s %20.2f" % (x, y), x[1:]))
    print string
    return string

def print_a(x, trs, prms, dic_c, dic_t):
#  print dic_c
#  print len (x)
  string = ""
  if len(x) == 1:
    string = "%s%s\n" % (string, print_h (x[0][0], dic_t, dic_c))
  for i in range(1, len(trs) + 1):
    if len(x) > 1 and i > 1:
      string = "%s%s\n" % (string, print_h (x[0][0], dic_t, dic_c))
    for k in xrange(prms):
      string = "%s%s\n" % (string, print_m (x[k][i], dic_t))
  return string


def print_af(x, fn):
  f = open("%s.csv" % fn, "w")
  try:
    f.write(print_a(x))
  finally:
    f.close()

def print_mx(x, trs):
  string = ""
  for i in xrange(len(trs) + 1):
      string = "%s%s\n" % (string, print_m(x[i]))
  return string



class AutoStat:
  def __init__(self):
      self.kstp = 1
      self.prms = 1  # count of parameters in step variable 
      self.parse = [ "send" ]
      self.diritem = "Stat"
      self.path = "."  # insert the path to the directory of interest here
      self.hystdelta = 10
      self.onefile = None
                   
  def process(self):
    kstp = self.kstp
    prms = self.prms 
    parse = self.parse
    diritem = self.diritem
    hystdelta = self.hystdelta      
        
    if self.onefile == None:
        dirList = os.listdir(self.path)
    else:
        diritem = ''
        dirList = self.onefile
    # Directories name should be in `diritem`-`trans`-`conn`-`it` format
    
    for parseitem in parse:
      pkt = {}
      hyst = {}
      dic_t  = {}
      dic_c  = {}
      dic_rt = {} # for different files
      dic_rc = {} # for different folders 
      maxconn  = 0
      maxtrans = 0
      if self.onefile == None:
          statfname = parseitem + ".stat"
          searchi = "Total_" + parseitem
      statfolder = "statout-" + parseitem
      print "Directories:"
      print dirList
      for findex,fname in enumerate(dirList):
          if fname.startswith(diritem):
              if self.onefile == None:
                nm = fname.split('-');
                print nm
                try:
                  trans = int(nm[1][0:])
                  conn = int(nm[2][0:])
                  it = int(nm[3][0:])
                except:
                  trans = int(nm[1][1:])
                  conn = int(nm[2][1:])
                  it = int(nm[3][1:])
                if conn not in dic_c:
                    dic_c[conn] = conn
                if trans not in dic_t:
                    dic_t[trans] = trans
              else:
                it = 1
                conn_name, trans_name = os.path.split(self.onefile[findex])
                conn_name = conn_name.replace('/', '_').replace('-','_').replace('.','_')
                trans_name = trans_name.replace(".stat.dat","").replace('/', '_').replace('-','_').replace('.','_')
                if trans_name not in dic_rt:
                    maxtrans = maxtrans + 1
                    dic_rt[trans_name] = maxtrans
                if conn_name not in dic_rc:
                    maxconn = maxconn + 1
                    dic_rc[conn_name] = maxconn
                trans=dic_rt[trans_name]
                conn=dic_rc[conn_name]
                it=1
                if conn not in dic_c:
                    dic_c[conn] = conn_name
                if trans not in dic_t:
                    dic_t[trans] = trans_name
                searchi = "Total_" + self.fileparse[findex]
                  
              print "Trans:%d (%s) Conn:%d (%s) #%d" % (trans, dic_t[trans], conn, dic_c[conn], it)
            
              if trans not in pkt:
                  pkt[trans] = {}
                  hyst[trans] = {}
        
        
              try:
              #if True:
                if self.onefile == None:
                  ln = GetTotalLineFromFile("%s/Merged/%s" % (fname, statfname), searchi).split()
                  st = GetWholeFile("%s/Merged/%s.dat" % (fname, statfname))
                else:
                  ln = GetTotalLineFromFile("%s" % (fname[:-4]), searchi).split()
                  prms = ((len(ln)-1) / 3) - 1
                  st = GetWholeFile("%s" % (fname))
                  
                if conn not in pkt[trans]:
                  pkt[trans][conn] = []
                  hyst[trans][conn] = [ [] for i in xrange(prms) ]
                  
                
                for x in st:
                  for j, v in enumerate(x):
                      hyst[trans][conn][j].append(float(v))
        
                #pkt[trans][conn].append(ln)
        
                vals = [0 for j in xrange(3 * prms)]
                for k in xrange(prms):
                  vals[k] = float(ln[1 + k])
                  vals[prms + k] = float(ln[1 + prms + kstp + k])
                  vals[2 * prms + k] = float(ln[1 + 2 * prms + 2 * kstp + k])
        
                #vals = [ float(ln[i]) for i in [1,2,3,4,  6,7,8,9,  11,12,13,14] ]
        
                failed = 0
                for k in xrange(prms):
                  if vals[prms + k] == 0:
                      failed = 1
                      break
        
                failed = 0
                if not failed:
                  pkt[trans][conn].append(vals)
                  print "T:%4d-%3d-%1d %s" % (trans, conn, it, ln)
                else:
                  print >> sys.stderr, "T:%4d-%3d-%1d BAD SIGMA %s/Merged/%s" % (trans, conn, it, fname, statfname)
        
              #except IndexError:
            #    print >> sys.stderr, "T:%4d-%3d-%1d BAD FILE  %s/Merged/%s" % (trans, conn, it, fname, statfname)
              except IOError:
                print >> sys.stderr, "T:%4d-%3d-%1d NOT FOUND %s/Merged/%s" % (trans, conn, it, fname, statfname)
    
    
      if self.onefile != None:
         searchi="Total"

      trs = [int(t) for t in pkt]
      trs.sort()
      print trs
    
      if len(trs) == 0:
          assert False, "Directories not found!"
    
      cns = [int(c) for c in pkt[trs[0]]]
      for i in xrange(1, len(trs)):
          for c in pkt[trs[i]]:
              if c not in cns:
                  cns.append(c)
      cns.sort()
      print cns
    
    
      avg_ttime = zeros((len(trs) + 1, len(cns) + 1))
      avg_ntime = zeros((len(trs) + 1, len(cns) + 1))
    
      avg_a = zeros((prms, len(trs) + 1, len(cns) + 1))
      avg_s = zeros((prms, len(trs) + 1, len(cns) + 1))
      avg_m = zeros((prms, len(trs) + 1, len(cns) + 1))
      avg_na = zeros((prms, len(trs) + 1, len(cns) + 1))
    
      alpa_2 = zeros((len(trs) + 1, len(cns) + 1))
    
    
    
    
      for i, c in enumerate(cns):
        avg_ttime[0][i + 1] = c
        avg_ntime[0][i + 1] = c
        alpa_2[0][i + 1] = c
    
        for k in xrange(prms):
          avg_a[k][0][i + 1] = c
          avg_s[k][0][i + 1] = c
          avg_m[k][0][i + 1] = c
          avg_na[k][0][i + 1] = c
    
      for i, t in enumerate(trs):
        avg_ttime[i + 1][0] = t
        avg_ntime[i + 1][0] = t
        alpa_2[i + 1][0] = t
    
        for k in xrange(prms):
          avg_a[k][i + 1][0] = t
          avg_s[k][i + 1][0] = t
          avg_m[k][i + 1][0] = t
          avg_na[k][i + 1][0] = t
    
      #print avg_ttime
    
      for t in pkt:
          #print "Transactions: %d" % t
          for c in pkt[t]:
          #print "Connections: %d" % c
              vl = pkt[t][c]
        
              if len(vl) == 0:
                print "NO DATA T:%d C:%d" % (t, c)
                continue
        
              bidx = [ argmax([ vl[j][i] for j in xrange(len(vl))  ])     for i in xrange(len(vl[0])) ]
              btr = [ 0 for i in xrange(len(vl)) ]
              for i in xrange(len(vl[0])):
                  btr[bidx[i]] = btr[bidx[i]] + 1
        
              mxi = -1
              bt = False
              if len(vl) > 2:
                  mx = max(btr)
                  mxi = argmax(btr)
        
                  bt = True
                  for i, v in enumerate(btr):
                      if i != mxi and v + 2 > mx: bt = False
        
                  if bt:
                      vl.pop(mxi)
                      bt = False
        
              for i, v in enumerate(vl):
                if bt and i == mxi:
                  addon = "***"
                else:
                  addon = ""
                #print "> % 8.2f % 8.2f % 8.2f % 8.2f     % 8.2f % 8.2f % 8.2f % 8.2f     % 8.2f % 8.2f % 8.2f % 8.2f%s" % (v[0],v[1],v[2],v[3], v[4],v[5],v[6],v[7], v[8],v[9],v[10],v[11], addon)
        
                for k in xrange(prms):
                  avg_ttime[arg(trs, t) + 1][arg(cns, c) + 1] = avg_ttime[arg(trs, t) + 1][arg(cns, c) + 1] + v[k]
                  avg_a[k][arg(trs, t) + 1][arg(cns, c) + 1] = avg_a[k][arg(trs, t) + 1][arg(cns, c) + 1] + v[k]
                  avg_s[k][arg(trs, t) + 1][arg(cns, c) + 1] = avg_s[k][arg(trs, t) + 1][arg(cns, c) + 1] + v[prms * 1 + k] * v[prms * 1 + k]
                  avg_m[k][arg(trs, t) + 1][arg(cns, c) + 1] = max([avg_m[k][arg(trs, t) + 1][arg(cns, c) + 1] , v[prms * 2 + k]])
        
        
              #gamma = 1.64
              avg_ttime[arg(trs, t) + 1][arg(cns, c) + 1] = avg_ttime[arg(trs, t) + 1][arg(cns, c) + 1] / len(vl)
              avg_ntime[arg(trs, t) + 1][arg(cns, c) + 1] = avg_ttime[arg(trs, t) + 1][arg(cns, c) + 1]
              for k in xrange(prms):
                avg_a[k][arg(trs, t) + 1][arg(cns, c) + 1] = avg_a[k][arg(trs, t) + 1][arg(cns, c) + 1] / len(vl)
                avg_s[k][arg(trs, t) + 1][arg(cns, c) + 1] = sqrt(avg_s[k][arg(trs, t) + 1][arg(cns, c) + 1] / len(vl))
        
                #avg_ntime[arg(trs, t) + 1][arg(cns, c) + 1] = avg_ntime[arg(trs, t) + 1][arg(cns, c) + 1] + gamma * (avg_s[k][arg(trs, t) + 1][arg(cns, c) + 1])        
                #avg_na[k][arg(trs, t) + 1][arg(cns, c) + 1] = avg_a[k][arg(trs, t) + 1][arg(cns, c) + 1] + gamma * avg_s[k][arg(trs, t) + 1][arg(cns, c) + 1]
        
        
        
              for k in xrange(prms):
                  delta = hystdelta
                  ma = max(hyst[t][c][k])
                  a = int((ma + 2 * delta) / delta) * delta
                  hst = histogram(hyst[t][c][k], bins = arange(0, a, delta))
        
                  if k == 2:
                    hst2 = histogram(hyst[t][c][k], bins = [0, 50, 1000000])
                    p0 = hst2[0][0]
                    p1 = hst2[0][1]
            
                    #alpha = 100.0 * p1 / (p0 + p1)
                    #alpa_2[arg(trs, t) + 1][arg(cns, c) + 1] = alpha
        
                  #print hst
        
                  if not os.path.exists(statfolder):
                      os.makedirs(statfolder)
        
                  flstat = "%s/%s-%s-%s-%d.csv" % (statfolder, searchi, dic_t[t], dic_c[c], k)
                  print "Dump to %s MAX=%f" % (flstat , ma)
                  f = open(flstat, "w")
                  try:
                      for i, x in enumerate(hst[0]):
                          f.write("% 5g % 10d\n" % (hst[1][i], x))
                  finally:
                      f.close()
    
      path_as, dummy = os.path.split(os.path.abspath(sys.argv[0]))
      os.system("( cd %s; %s/mkplot.py -y %g -t %g -m %g)" % (statfolder, path_as, self.hystdelta, self.hystdelta * 10, ma))
    
      f = open("stat-all-%s.csv" % searchi, "w")
      try:
        print   "-----AVERAGE--------"
        f.write("-----AVERAGE--------\n")
        f.write(print_a(avg_a, trs, prms, dic_c, dic_t))
        print   "######SIGMAS#######"
        f.write("######SIGMAS#######\n")
        f.write(print_a(avg_s, trs, prms, dic_c, dic_t))
        print   "+++++++MAXS++++++++"
        f.write("+++++++MAXS++++++++\n")
        f.write(print_a(avg_m, trs, prms, dic_c, dic_t))
      finally:
        f.close()


def listDirectory(directory, fileExtList):
     "get list of file info objects for files of particular extensions"
     fileList = [os.path.normcase(f) 
                  for f in os.listdir(directory)]
     fileList = [os.path.join(directory, f) 
                  for f in fileList if f.endswith(fileExtList)]
     return fileList

def usage(): 
    print "%s [-d dir_start] [-n name1,name2,name3] [-y hystus] [-c valcnt] [-s valspace] [-p path]" % sys.argv[0] 
    print " -d, --dirstart=DIR         Search files that starts with this name"
    print " -n, --names=NAME1,NAME2,.. Comma-separated names for plotting"
    print " -y, --hystdelta=TIMEUS     Bar size for hystogram in uS"
    
def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:n:y:c:s:p:hf:z:", 
                                    ["dirstart=", "names=", "hystdelta=", "valcount=", "valspace=", "path=", "help", "file=", "dir="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)    

    autost = AutoStat()

    for o, a in opts:
        if o in ("-d", "--dirstart"):
            autost.diritem = a
        elif o in ("-n", "--names"):
            autost.parse = a.split(',')
        elif o in ("-y", "--hystdelta"):
            autost.hystdelta = float(a)
        elif o in ("-c", "--valcount"):
            autost.prms = int(a)
        elif o in ("-s", "--valspace"):
            autost.kstp = int(a)
        elif o in ("-p", "--path"):
            autost.path = a
        elif o in ("-f", "--file"):
            autost.onefile = a.split(',')
            autost.fileparse  = []
            for ab in autost.onefile:
                path,tmp = os.path.split(ab)
                autost.fileparse.append(tmp.split(".")[0])
            #print autost.fileparse 
            if len(autost.fileparse) > 1:
                autost.parse = ["files"]
            else:
                autost.parse = autost.fileparse
        elif o in ("-z", "--dir"):
            dirs = a.split(',')
            files = [os.path.split(d)[1] for d in listDirectory(dirs[0], ".stat.dat")]
            for e in dirs[1:]:
               files2 = [os.path.split(d)[1] for d in listDirectory(e, ".stat.dat")]
               files = [val for val in files if val in files2]
            print "Found files in dir: "
            print files
            autost.parse = ["dirs"]
            autost.fileparse  = []
            autost.onefile    = []
            for f in files:
               for d in dirs:
                  autost.onefile.append(os.path.join(d, f))
                  autost.fileparse.append(f.split(".")[0])
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        else:
            assert False, "unhandled option"
    
    autost.process();
        
if __name__ == "__main__":
    main()
        


