# -*- coding: UTF-8 -*-
import hashlib
def md5(p):
    m = hashlib.md5()
    m.update(str(p).encode("utf-8"))
    return m.hexdigest()