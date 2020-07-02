#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/4 14:15
# @Author  : Marrion
#
import functools,inspect
def check(fn):
    @functools.wraps(fn)
    def warp(*args,**kwargs):
        sig = inspect.signature(fn)
        parms = inspect.signature(fn).parameters

        for k,v in kwargs.items():
            parm_type = parms[k].annotation
            if parm_type != inspect._empty and not isinstance(v,parm_type):
                raise TypeError('parameter {} required {},but {}'.format(k,parms[k].annotation,type(v)))
        for idx,v in enumerate(args):
            parm = list(parms.values())[idx]
            if parm.annotation != inspect._empty and not isinstance(v,parm.annotation):
                raise TypeError('parameter {} required {},but {}'.format(parm.name, parm.annotation,type(v)))
        return fn(*args,**kwargs)
    return warp
@check
def add(x,y:int)->int:
   return x + y
print(add(3,4))