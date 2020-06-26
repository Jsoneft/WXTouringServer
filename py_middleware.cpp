//
// Created by Jason.Z on 2020/6/25.
//

#include "py_middleware.h"
#include <iostream>
#include <sys/socket.h>
using namespace std;

const int MAXBUFFER = 8192;


py_middleware::py_middleware(int fd,PyObject *func)
        : _fd(fd),
         _func(func)
{
    cout << "py_middleware constructed" << endl;
}

void py_middleware::test(){
    char buf[MAXBUFFER]={""};
    memset(buf, 0, sizeof(buf));
    int ret = recv(_fd, buf, sizeof(buf), 0);//接收客户端发来的信息
    if (ret > 0) {

        memset(buf, 0, sizeof(buf));
        char* cStr = new char[100];
//        char cStr[MAXBUFFER];
//        memset(cStr, '\0', sizeof(cStr));

        std::cout << "result:" << cStr << std::endl;

//        ret = send(_fd, &"200 ok", strlen(cStr) - 1, 0);//将标准输入的信息发送给客户端
        ret = send(_fd, &"200 ok", 6, 0);//将标准输入的信息发送给客户端
        sleep(2);


        if (ret <= 0) {
            printf("Server:您未输入任何信息，请重新输入!\n");//输入为空的处理
        }

        ret = close(_fd);
        if(ret == -1){
            printf("服务端关闭请求失败\n");
        }
        std::cout << "关闭客户端连接" << std::endl;
    } else if (0 == ret) {
        printf("byebye,客户端已下线!\n");
        close(_fd);
    }else {
        perror("recv ERR");
    }
}

// 带close(fd)
void py_middleware::handle() {

    PythonThreadLocker locker;
    char buf[MAXBUFFER]={""};
    memset(buf, 0, sizeof(buf));
    int ret = recv(_fd, buf, sizeof(buf), 0);//接收客户端发来的信息
    if (ret > 0) {
        PyObject *args = Py_BuildValue("(s)", buf);
        if (args == NULL) {
            printf("restNotifyFunc, Py_BuildValue run OOM.\n");
            return ;
        }
        PyObject *result = PyObject_CallObject(_func, args);
        memset(buf, 0, sizeof(buf));
        char *cStr;
//        char cStr[MAXBUFFER];
//        memset(cStr, '\0', sizeof(cStr));
        cStr = PyUnicode_AsUTF8AndSize(result, NULL);
        std::cout << "result:" << cStr << std::endl;

        ret = send(_fd, cStr, strlen(cStr) - 1, 0);//将标准输入的信息发送给客户端
        if (ret <= 0) {
            printf("Server:您未输入任何信息，请重新输入!\n");//输入为空的处理
        }

        ret = close(_fd);
        if(ret == -1){
            printf("服务端关闭请求失败\n");
        }
        std::cout << "关闭客户端连接" << std::endl;
    } else if (0 == ret) {
        printf("byebye,客户端已下线!\n");
        close(_fd);
    }else {
        perror("recv ERR");
    }
}