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
    py_middleware(int fd,PyObject *func);

    void test();
};

class PythonThreadLocker
{
    PyGILState_STATE state;
public:
    PythonThreadLocker() : state(PyGILState_Ensure())
    {}
    ~PythonThreadLocker() {
        PyGILState_Release(state);
    }
};


#endif //SOCKETSERVERCPLUS_PY_MIDDLEWARE_H
