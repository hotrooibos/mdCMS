# -*- mode: python ; coding: utf-8 -*-
import time

'''

STRING UTILS


'''

def replacemany(string: str,
                old: tuple,
                new: str,
                count: int=-1) -> str:
    '''Replaces many different strings with another specified string.

    Strings to replace are specified in the tuple argument.

    Works as an extension of replace().
    '''
    newstr = string
    
    for i in old:
        newstr = newstr.replace(i,
                                new,
                                count)
    
    return newstr




'''

TIME UTILS


'''

def to_epoch(datetime: str,
             datetime_format: str='%Y-%m-%d %H:%M:%S',
             epoch_format: str='float'):
    '''Return an UNIX epoch time from a given datetime string

    Default source format is '%Y-%m-%d %H:%M:%S'

    Default epoch returned format is float. Can be 'int'.
    '''
    epoch = time.strptime(datetime,
                          datetime_format)
    epoch = time.mktime(epoch)

    if epoch_format == 'float':
        return epoch
    else:
        return int(epoch)



def to_datestr(epoch,
               out_format: str='%Y-%m-%d %H:%M:%S') -> str:
    '''Return a datetime string from a given UNIX epoch time

    Default source format is '%Y-%m-%d %H:%M:%S'

    Default epoch returned format is integer. Can be 'float'.
    '''
    datestr = time.ctime(epoch)
    datestr = time.strptime(datestr)
    datestr = time.strftime(out_format,
                            datestr)
    return datestr



def datestr_convert(old: str,
                    old_format: str,
                    new_format: str):
    '''Convert a date string to another date string format
    '''
    datestr = time.strptime(old,
                            old_format)
    datestr = time.strftime(new_format,
                            datestr)
    
    return datestr