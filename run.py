#!/usr/bin/env python
import sys
import os

# Checks python version and exits if it is too low
# Must be specified before any lib imports (using v3.3) are done
def check_version():
    if sys.version_info < (3,3):
        print('I am sorry, but this script is for python3.3+ only!')
        exit(1)
check_version()

import lib.picker as picker


# Get absolute path to this script
def get_loc():
    return os.path.abspath(os.path.dirname(sys.argv[0]))

# Maps numbers (starting from 0) to components for user select
def make_optionsdict(components):
    returndict={}
    for number, component in enumerate(components):
        returndict[number] = component
    return returndict


# Returns a list of folders in given path
def listonlydir(path, full_paths=False):
    contents = os.listdir(path)
    if not full_paths:
        return [name for name in contents if os.path.isdir(os.path.join(path, name))]
    else:
        return [os.path.join(path, name) for name in contents if os.path.isdir(os.path.join(path, name))]

def get_all_subdirs(directory):
    return_list= [directory]
    tmp_list = listonlydir(directory, full_paths=True)
    for item in tmp_list:
        return_list.extend(get_all_subdirs(item))
    return return_list

def ask_subdirs(directory):
    choice_list = listonlydir(directory, full_paths=True)
    optionsdict = make_optionsdict(choice_list)
    if len(optionsdict) == 0:
        return [directory]

    while True:
        for item in optionsdict:
            print('\t\t[{0}] - {1}'.format(str(item),os.path.basename(optionsdict[item])))
        print('\t[E]verything')
        choice = input('Please make a choice (or multiple, comma-separated): ').upper()
        chosenarray = []
        words = choice.split(',')
        for word in words:
            if word in ('E', 'EVERYTHING'):
                return_list = []
                for item in choice_list:
                    return_list.extend(get_all_subdirs(item))
                return return_list
            elif word.isdigit() and int(word) in optionsdict:
                chosenarray.append(optionsdict[int(word)])
            else:
                print('Unknown option "'+word+'"')
        if len(chosenarray) > 0:
            tmparray = []
            for option in chosenarray:
                print('Reviewing "{0}"'.format(option))
                tmparray += ask_subdirs(option)
            return tmparray

# Simple method to ask user a yes/no question. Result returned as boolean.
# Returns True if user responded positive, otherwise False
def standard_yesno(question):
    while True:
        choice = input(question+' [Y/n] ').upper()
        if choice in ('Y', 'YES'):
            return True
        elif choice in ('N', 'NO'):
            return False
        else:
            print('Invalid option "'+choice+'"')

# ask user for a directory
# must exist determines wheter it explicitly must or must not exist
def ask_directory(question, must_exist=True):
    while True:
        print(question)
        print('Paths may be absolute or relative to your working directory')
        print('Please specify a directory:')
        choice = input('')
        choice = choice if choice[0]=='/' else os.environ['PWD']+'/'+choice
        choice = os.path.normpath(choice)
        if must_exist:
            if not os.path.isdir(choice):
                print('Error: no such directory - "{0}"'.format(choice))
            else:
                return choice
        else:
            if os.path.isdir(choice):
                print('"{0}" already exists'.format(choice))
                if standard_yesno('continue?'):
                    return choice
            else:
                return choice

# ask user for a directory+filename
def ask_path(question):
    while True:
        print(question)
        print('Paths may be absolute or relative to your working directory')
        print('Please specify a path:')
        choice = input('')
        choice = choice if choice[0]=='/' else os.environ['PWD']+'/'+choice
        choice = os.path.normpath(choice)
        if not os.path.isdir(os.path.dirname(choice)):
            print('Error: no such directory - "{0}"'.format(os.path.dirname(choice)))
        elif os.path.isfile(choice):
            if standard_yesno('"{0}" exists, override?'.format(choice)):
                return choice
        else:
            return choice

# ask user for a filetype to choose from
def ask_filetype():
    while True:
        print('Which filetype do you want to sample from? (e.g. .apk, .csv)')
        choice = input('')
        if len(choice) == 0:
            print('Empty filetype not accepted')
        elif not choice[0] == '.' or len(choice) == 1:
            print('Please specify a filetype!')
        else:
            return choice

# Main function of this simple tool
def main():
    _path = get_loc()
    print('Hello, this tool has been made to select a sample from a dataset')
    print('Your dataset may contain multiple subdirectories.')
    print('If this is the case, specify the root directory of the dataset')
    filetype = ask_filetype()
    directory = ask_directory('Provide a path to your dataset')
    if len(listonlydir(directory)) != 0:
        subdirs = ask_subdirs(directory)
        print('Got {0} directories'.format(str(len(subdirs))))
    else:
        subdirs = [directory]
    pick = picker.Picker(subdirs, filetype)
    if pick.listsize == 0:
        return
    samplesize = pick.ask_samplesize()
    sample_array = pick.pick(samplesize)
    while True:
        print('What do you want with your output?')
        print('[F]ile     - print list to file')
        print('[T]erminal - print list to terminal')
        print('[S]ymlink  - Give directory, convert list to symlinks')
        print('[Q]uit     - You are done now')
        choice = input('Please make a choice (or multiple, comma-separated): ').upper()
        for word in choice.split(','):
            if word in ('F', 'FILE'):
                output_path = ask_path('Please specify a path for output')
                with open(output_path, 'w') as conf:
                    for item in sample_array:
                        conf.write(item+'\n')
            elif word in ('T', 'TERMINAL'):
                for item in sample_array:
                    print(item)
            elif word in ('S', 'SYMLINK'):
                output_directory = ask_directory('Please specify a directory for output', must_exist=False)
                os.makedirs(output_directory, exist_ok=True)
                for item in sample_array:
                    link_position = os.path.join(output_directory, os.path.basename(item))
                    if os.path.exists(link_position):
                        shutil.rmtree(link_position)
                    os.symlink(item,link_position)
            elif word in ('Q', 'QUIT', 'B', 'BACK', 'BYE'):
                return
            else:
                print('Unknown option "'+word+'"')

if __name__ == '__main__':
    main()