//
// Created by Jason.Z on 2020/6/25.
//

#include "epoll.h"
#include "threadpool.h"
#include "util.h"
#include "py_middleware.h"
#include <iostream>
#include <Python.h>
#include <pythonrun.h>
#include <csignal>
#include <sys/select.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <cstdio>
#include <netdb.h>
#include <cstring>
#include <sys/types.h>
#include <unistd.h>
#include <cstdlib>


static const int MAXEVENTS = 5000;
static const int LISTENQ = 1024;
const int ZJX_TIMEOUT = 500;
const int THREADPOOL_THREAD_NUM = 4;
const int QUEUE_SIZE = 65535;
const int PORT = 80;
const int MAXBUFFER = 8192;

int socket_bind_listen(int port = PORT){

    // 创建socket(IPv4 + TCP)，返回监听描述符
    int listen_fd = 0;
    if((listen_fd = socket(AF_INET, SOCK_STREAM, 0)) == -1)
        return -1;

    // 消除bind时"Address already in use"错误
    int optval = 1;
    if(setsockopt(listen_fd, SOL_SOCKET,  SO_REUSEADDR, &optval, sizeof(optval)) == -1)
        return -1;

    // 设置服务器IP和Port，和监听描述符绑定
    struct sockaddr_in server_addr{};
    bzero((char*)&server_addr, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    server_addr.sin_port = htons((unsigned short)port);
    int ret = bind(listen_fd, (struct sockaddr *)&server_addr, sizeof(server_addr));
    if(ret < 0)
        return -1;

    // 开始监听，最大等待队列长为LISTENQ
    if(listen(listen_fd, LISTENQ) == -1)
        return -1;


    if(listen_fd == -1)
    {
        close(listen_fd);
        return -1;
    }

    return listen_fd;

}



int main(int argc,char* argv[]) {
    // 忽略sigpipe信号 -> Broken pipe 进程不终止
    handle_for_sigpipe();
    Py_Initialize();
    if (!Py_IsInitialized()) {
        printf("Python init failed!\n");
        PyErr_Print();//打印错误信息，库函数
        return -1;
    }
    PyRun_SimpleString("import sys");    //调用python代码
    PyRun_SimpleString("sys.path.append('./')");    //将当前目录添加到python路径
    PyObject *pModule = NULL;    //python模块

    if (!(pModule = PyImport_ImportModule("handle"))) {
        printf("ImportModule failed");//打印错误信息，库函数
        return -1;
    }
    PyObject *dic = PyModule_GetDict(pModule);
    if (!dic) {
        printf("Dict obtain err");
        return -1;
    }
    /* 获得handleRequest函数地址并验证 */
    PyObject *func = PyDict_GetItemString(dic, "handleRequest");

    /* 初始化Epoll */
    if (Epoll::epoll_init(MAXEVENTS, LISTENQ) < 0) {
        perror("epoll init failed");
        return 1;
    }

    /* 初始化线程池 */
    if (ThreadPool::threadpool_create(THREADPOOL_THREAD_NUM, QUEUE_SIZE) < 0) {
        printf("Threadpool create failed\n");
        return 1;
    }

    int listen_fd = socket_bind_listen(PORT);

    if (listen_fd < 0) {
        perror("socket bind failed");
        return 1;
    }
    if (setSocketNonBlocking(listen_fd) < 0) {
        perror("set socket non block failed");
        return 1;
    }

    if (Epoll::epoll_add(listen_fd, EPOLLIN | EPOLLET) < 0) {
        perror("epoll add error");
        return 1;
    }

    printf("event epoll started\n");
    printf("listen_fd = %d\n", listen_fd);
    int ss = 0;
    while (true) {
        //sleep(10);
        printf("%d th loop\n", ss++);
        printf("有 %d 个待提交的任务\n", ThreadPool::count);
        printf("有 %d 个正在运行的线程\n",ThreadPool::started+1);
        printf("有 %d 个创建了的线程\n", ThreadPool::thread_count);
        int ready_num = Epoll::zjx_epoll_wait(listen_fd, MAXEVENTS, ZJX_TIMEOUT);
        if (ready_num == -1) {
            perror(" wait ended badly");
            break;
        }
        printf("got %d item(s)\n", ready_num);
        for (int i = 0; i < ready_num; i++) {
            int fd = Epoll::events[i].data.fd;
            printf("fd = %d\n", fd);
            if (fd == listen_fd) {
                Epoll::acceptConnection(listen_fd, Epoll::epoll_fd);
                printf("new conn added\n");
            } else {
                // 排除错误事件
                if ((Epoll::events[i].events & EPOLLERR) || (Epoll::events[i].events & EPOLLHUP) ||
                    (!(Epoll::events[i].events & EPOLLIN))) {
                    perror("遇到问题事件");
                    continue;
                }

                // 加入任务至线程池
                std::shared_ptr<py_middleware> tmp(new py_middleware(fd, func));


                if (ThreadPool::threadpool_add(tmp) == -1) {
                    perror("加入线程池失败");
                    assert(0);
                    continue;
                }
                printf("线程池加入成功\n");
                // 删除掉epoll_list 中的 fd
                if (Epoll::epoll_del(fd) == -1) {
                    continue;
                }
            }
        }
    }

    close(listen_fd);
    Epoll::epoll_del(listen_fd);
    ThreadPool::threadpool_destroy();
    return 0;
}