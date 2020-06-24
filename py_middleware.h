//
// Created by Jason.Z on 2020/6/25.
//

#ifndef SOCKETSERVERCPLUS_PY_MIDDLEWARE_H
#define SOCKETSERVERCPLUS_PY_MIDDLEWARE_H

#include <Python.h>
class py_middleware {
public:
    int _fd;
    PyObject *_func;
public:
    void handle();
    py_middleware(int fd, PyObject *tmp);
};


#endif //SOCKETSERVERCPLUS_PY_MIDDLEWARE_H
