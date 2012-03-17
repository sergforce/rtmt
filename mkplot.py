#!/usr/bin/python
# -*- coding: utf8 -*-

#from system import *
from struct import *
from collections import *
from math import sqrt
from datetime import *

import os, stat;
import sys
import re
import getopt

from numpy import *

class StatFile:
    def __init__(self, filename):
      self.data = []
      self.total = 0
      self.filename = filename

      f = open(filename, "r")
      try:
        while True:
          ln = f.readline()
          if isinstance(ln, str):
              string = ln.split()
              if len(string) > 1:
                  self.data.append(int(string[1]))
                  self.total = self.total + int(string[1])
                  self.maxtm = float(string[0])
              else:
                  break
          else:
              break
      finally:
        f.close()

      self.ddata = map(lambda x: float(x) / self.total, self.data);
      self.idata = [ self.ddata[0] ]
      for i in range(1, len(self.ddata)):
          self.idata.append(self.idata[i - 1] + self.ddata[i])

    def __str__(self):
        return "[%s:\tTotal = %d]" % (self.filename, self.total)

    def getval(self, idx):
          if (idx < len(self.ddata)):
              return self.ddata[idx]
          else:
              return 0.0

    def getival(self, idx):
          if (idx < len(self.idata)):
              return self.idata[idx]
          else:
              return 0.0

def fillHscipt(filename, plots, size = "1024,768"):
    hscript = "#!/usr/bin/gnuplot\n"
    hscript = hscript + "set terminal png nocrop enhanced font arial 8 size %s\n" % size
    hscript = hscript + "set output '%s.png'\n" % filename
    hscript = hscript + "set multiplot layout %d, 1 \n" % plots
    hscript = hscript + "set lmargin 8\n"
    hscript = hscript + "set grid\n"

    return hscript

class StFiles:
    def __init__(self, path, flt = ".+\.csv", splitter = '-'):
      self.parts = []
      if splitter != None:
        self.sti = 0
        self.endi = -1
        lst = os.listdir(path)
        print lst
    
        for l in lst:
            if re.match(flt, l):
                parts = l.split(splitter)
                for i, p in enumerate(parts):
                    if i >= len(self.parts):
                        self.parts.append([])
                    if p not in self.parts[i]:
                        self.parts[i].append(p)    
    
        print self.parts
    
        skipm = 0
        for p in xrange(len(parts)):
            i = self.parts[p]
            if skipm == 0 and len(i) == 1:
               self.sti = self.sti + 1
            elif skipm == 0:
               skipm = 1
            elif skipm == 1 and len(i) == 1:
               self.endi = p
    
        if (self.sti > self.endi):
            self.endi = self.sti - 1
            self.sti = self.sti - 3
        if (self.endi - self.sti == 1):
            self.sti = self.sti -1
            
        print "Files search from %d to %d" % (self.sti, self.endi)
        
        self.statdata = []
        j = self.statdata
    
        suffix = splitter + reduce(lambda x, y: x + splitter + y, *self.parts[ self.endi: ])
        prefix = reduce(lambda x, y: str(x) + splitter + str(y), *self.parts[ : self.sti ]) + splitter
    
        print "Parsing '%s*%s'" % (prefix, suffix)

        def fillrecursion(startname, idx, obj):
            if idx == self.endi - 1:
                for i in self.parts[idx]:
                    try:
                      print "Appending %s" %   (startname + i + suffix)
                      obj.append(StatFile(startname + i + suffix))
                    except IOError:
                      print "Unable to open %s" %   (startname + i + suffix)
                      obj.append(None)
            else:
                for i in self.parts[idx]:
                    data = []
                    print "fillrecursion ( %s, %d, ... ) " %   (startname + i + splitter, idx + 1)
                    fillrecursion(startname + i + splitter, idx + 1, data)
                    obj.append(data)

        self.statfiles = []
        fillrecursion(prefix, self.sti, self.statfiles)
    
        self.prefix = prefix
      else:
        self.prefix = ''
        self.parts = [flt, "1"]
        self.sti = 0
        self.endi= 1
        self.statfiles = [StatFile(flt)]
        
      print self.statfiles

    def combine2nd(self, maxst = 10000, delta = 10, maxval = 2000, valtic = 50, endp = 0.990, geometry="1024,768"):
        for inum, ival in enumerate(self.parts[self.sti]):
            print inum
            print ival
            valend = 0
            combined = ""
            header = reduce(lambda x, y: str(x) + ", " + str(y), [j for j in self.parts[self.sti + 1]])            
            
            for i in xrange(maxst):                
                combined = combined + str(reduce(lambda x, y: str(x) + "\t" + str(y), [j.getval(i) if j != None else 0 for j in self.statfiles[inum]]))
                combined = combined + "\t"
                sint = [j.getival(i) if j != None else 0 for j in self.statfiles[inum]]
                if valend == 0 and min(sint) > endp:
                    valend = i
                combined = combined + str(reduce(lambda x, y: str(x) + "\t" + str(y), sint))
                combined = combined + "\n"
    
            #print combined
            filename = self.prefix + ival + "-graph.dat"
            f = open(filename, "w")
            try:
                f.write(combined)
            finally:
                f.close()
    
            while (valend * delta) / valtic > 50:
                valtic = valtic * 10

            if (valend * delta) / valtic < 7:
                valtic = valtic * 0.2
            if (valend * delta) / valtic < 14:
                valtic = valtic * 0.5
            
            print "Tiks %g" % ( (valend * delta) / valtic )
                
            plotxrange = (maxval / delta)
            if valend > 0 and valend < plotxrange:
                plotxrange = valend
                if plotxrange * delta % valtic != 0:
                    plotxrange =  ((plotxrange * delta + valtic)//valtic)*valtic/delta
                   
                    
            scriptname = self.prefix + ival + "-graph.plt"
            script = fillHscipt(scriptname, 2, geometry)            
            script = script + "set xrange [0 : %f]\n" % (plotxrange)
            script = script + "set xtics ( %s )\n" % reduce(lambda x, y: x + ", " + y, [ "\"%g\" %g" % (idx * valtic, idx * valtic / delta) for idx in range(1, int(maxval / valtic)) ])
            script = script + "set title \"%s in [%s]\"\n" % (ival, header)
            script = script + "plot " + reduce(lambda x, y: x + ", " + y, [ "'%s' u %d t \"%s\" with lines " % (filename, 1 + idx, j) for idx, j in enumerate(self.parts[self.sti + 1]) ]) + "\n"
            script = script + "unset title \n"
            script = script + "plot " + reduce(lambda x, y: x + ", " + y, [ "'%s' u %d t \"%s\" with lines " % (filename, 1 + len(self.parts[self.sti + 1]) + idx, j) for idx, j in enumerate(self.parts[self.sti + 1]) ]) + "\n"
    
            f = open(scriptname, "w")
            try:
                f.write(script)
            finally:
                f.close()
            os.chmod(scriptname, stat.S_IRWXU or stat.S_IXGRP or stat.S_IRGRP or stat.S_IXOTH or stat.S_IROTH)
            os.system("pwd; ls -l %s; /usr/bin/gnuplot %s" % (scriptname, scriptname))


def usage():
    print "%s [-y hystdelta] [-t xtick] [-m maxval] [-e endm] [-a maxstat] [-g geometry] [-p path]" %  sys.argv[0]
    
def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "y:t:m:e:a:p:hf:", 
                                    ["hystdelta=", "xtick=", "maxval=", "endporb=", "maxstat=", "path=", "geometry=", "help", "file="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)    

    maxstat = 10000
    hystdelta = 10
    maxval = 2000
    xtick = 50
    endporb = 0.990
    path = "."
    geometry = "1280,1024"
    onefile = None

    for o, a in opts:
        if o in ("-y", "--hystdelta"):
            hystdelta = float(a)
        elif o in ("-t", "--xtick"):
            xtick = float(a)
        elif o in ("-m", "--maxval"):
            maxval = float(a)
        elif o in ("-e", "--endporb"):
            endporb = float(a)
            if endporb <= 0 or endporb > 1.0: assert False, "incorrect endporb value"
        elif o in ("-a", "--maxstat"):
            maxstat = float(a)
        elif o in ("-p", "--path"):
            path = a
        elif o in ("-g", "--geometry"):
            geometry = a
        elif o in ("-f", "--file"):
            onefile = a
        elif o in ("-h", "--help"):
            usage()
            sys.exit()            
        else:
            assert False, "unhandled option"

    if onefile == None:
        sf = StFiles(path)
    else:
        sf = StFiles(path, onefile, None)
    sf.combine2nd(maxstat, hystdelta, maxval, xtick, endporb, geometry)
    print sf.parts[sf.sti:sf.endi]


if __name__ == "__main__":
    main()
    
    
#argv = sys.argv[1:]
#
#sf = StFiles(".")
#if (len(argv) > 0):
#    sf.combine2nd(int(argv[0]))
#else:
#    sf.combine2nd()

#print sf.sti
#print sf.endi
#print sf.parts[sf.sti:sf.endi]

