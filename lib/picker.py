#!/usr/bin/env python
import sys
import os
import multiprocessing
import numpy

import lib.firepool as firepool

class Picker(object):
    """Object which pickes items from given dirs (and subdirs)"""
    def __init__(self, directories, filetype):
        for directory in directories:
            if not os.path.isdir(directory):
                raise RuntimeError('Error: no such directory - "'+directory+'"')

        if len(filetype) == 0 or not filetype[0] == '.' or len(filetype) == 1:
            raise RuntimeError('Error: unacceptable filetype - "'+filetype+'"')
        self.directories = directories
        self.filetype = filetype
        self.makelist()

    # Returns a list of files with correct filetype in given path
    def listonlyfiletype(self, path):
        contents = os.listdir(path)
        return [os.path.join(path, name) for name in contents if os.path.isfile(os.path.join(path, name)) and name.endswith(self.filetype)]

    # Function to be called by Firepool
    def parallel_makelist(self, path, itemlist):
        itemlist.extend(self.listonlyfiletype(path))

    # Returns list of tuples, each tuple corresponding to
    # parameters of parallel_makelist
    def arg_generator(self, itemlist):
        args = []
        for directory in self.directories:
            args.append((directory,itemlist,))
        return args

    # Makes a list (self.itemlist) of all user-defined apks
    def makelist(self):
        pool = firepool.Firepool()
        itemlist = multiprocessing.Manager().list()
        

        args = self.arg_generator(itemlist)

        pool.fire(self.parallel_makelist, args)
        print('Found '+str(len(itemlist))+' "'+self.filetype+'"\'s')
        self.itemlist = itemlist

    # Pick items at random out of the list
    def pick(self, samplesize):
        return numpy.random.choice(self.itemlist, samplesize, replace=False)

    def __str__(self):
        return self.itemlist