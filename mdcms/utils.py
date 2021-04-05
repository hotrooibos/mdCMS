# -*- mode: python ; coding: utf-8 -*-
import time

'''

STRING UTILS


'''

def replacemany(__string: str,
                __old: tuple,
                __new: str,
                __count: int = -1) -> str:
    '''
    Replaces many different strings with another specified string.

    Strings to replace are specified in the tuple argument.

    Works as an extension of replace().
    '''
    newstr = __string
    
    for i in __old:
        newstr = newstr.replace(i,
                                __new,
                                __count)
    
    return newstr




'''

TIME UTILS


'''

def to_epoch(__datetime: str,
             __datetime_format: str = '%Y-%m-%d %H:%M:%S',
             __epoch_format: str = 'float'):
    '''
    Return an UNIX epoch time from a given datetime string

    Default source format is '%Y-%m-%d %H:%M:%S'

    Default epoch returned format is float. Can be 'int'.
    '''
    __epoch = time.strptime(__datetime,
                            __datetime_format)
    __epoch = time.mktime(__epoch)

    if __epoch_format == 'float':
        return __epoch
    else:
        return int(__epoch)



def to_datestr(__epoch,
               __datestr_format: str = '%Y-%m-%d %H:%M:%S') -> str:
    '''
    Return a datetime string from a given UNIX epoch time

    Default source format is '%Y-%m-%d %H:%M:%S'

    Default epoch returned format is integer. Can be 'float'.
    '''
    __datestr = time.ctime(__epoch)
    __datestr = time.strptime(__datestr)
    __datestr = time.strftime(__datestr_format,
                              __datestr)
    return __datestr



def datestr_convert(__old: str,
                    __old_format: str,
                    __new_format: str):
    '''
    Convert a date string to another date string format
    '''
    __datestr = time.strptime(__old,
                              __old_format)
    __datestr = time.strftime(__new_format,
                              __datestr)
    
    return __datestr