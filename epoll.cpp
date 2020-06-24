//
// Created by Jason.Z on 2020/6/24.
//

#include "epoll.h"
#include "threadpool.h"
#include "util.h"
#include <sys/epoll.h>
#include <cerrno>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <iostream>
#include <cassert>
#include <sys/socket.h>
#include <netinet/in.h>
#include <cstring>
#include <queue>
#include <deque>



epoll_event *Epoll::events;
int Epoll::epoll_fd = 0;

// epoll  初始化(创建事件表+事件队列)
int Epoll::epoll_init(int max_events, int listen_num) {
    // 创建epoll事件表
    epoll_fd = epoll_create(listen_num+1);
    if(epoll_fd == -1){
        return -1;
    }
    events = new epoll_event[max_events];
    return 0;
}

// 注册新描述符
int Epoll::epoll_add(int fd, __uint32_t events) {
    // 创建事件
    struct epoll_event event{};
    event.data.fd = fd; // 事件从属目标文件符
    event.events = events;

    // 加入事件
    if(epoll_ctl(epoll_fd, EPOLL_CTL_ADD, fd, &event) == -1){
        perror("epoll_add error");
        return -1;
    }
    return 0;
}

// 修改描述符状态
int Epoll::epoll_mod(int fd, __uint32_t events) {
    // 创建事件
    struct epoll_event event{};
    event.data.fd = fd;
    event.events = events;
    if(epoll_ctl(epoll_fd, EPOLL_CTL_MOD, fd, &event) < 0)
    {
        perror("epoll_mod error");
        return -1;
    }
    return 0;
}

// 从epoll中删除描述符
int Epoll::epoll_del(int fd, __uint32_t events) {
    struct epoll_event event{};
    event.data.fd = fd;
    event.events = events;
    if(epoll_ctl(epoll_fd, EPOLL_CTL_DEL, fd, &event) < 0)
    {
        perror("epoll_del error");
        return -1;
    }
    return 0;
}

// 轮询
// @var timeout 等待毫秒数
int Epoll::zjx_epoll_wait(int listen_fd, int max_event, int timeout) {
    // 返回值事件存在 events 里面
    int event_count = epoll_wait(epoll_fd, events, max_event, timeout);
    if (event_count < 0){
        perror("epoll wait error");
        return -1;
    }
    return event_count;
}


// accept封装
void Epoll::acceptConnection(int listen_fd, int epoll_fd) {
    struct sockaddr_in client_addr;
    memset(&client_addr, 0, sizeof(struct sockaddr_in));
    socklen_t client_addr_len = sizeof(client_addr);
    int accept_fd = 0;
    printf("acceptConnection Entered && len  = %d\n", client_addr_len);
    int th = 0;

//    accept_fd = accept(listen_fd, (struct sockaddr*)&client_addr, &client_addr_len);
//    assert(accept_fd>=0);

    while ((accept_fd = accept(listen_fd, (struct sockaddr*)&client_addr, &client_addr_len)) > 0){
        // listen_fd 非阻塞了， 一直监听到没有活动为止
        assert(accept_fd>=0);
//        std::cout << inet_addr(reinterpret_cast<const char *>(client_addr.sin_addr.s_addr)) << std::endl;
//        std::cout << ntohs(client_addr.sin_port) << std::endl;
        printf("%d th accept\n", th++);
        // 将新的socket 设为非阻塞
        if(setSocketNonBlocking(accept_fd) == -1){
            perror("Set non block failed");
            continue;
        }
        // 将新的socket 加入事件监听队列
        if(Epoll::epoll_add(accept_fd, EPOLLIN | EPOLLET | EPOLLONESHOT) == -1){
            continue;
        }
    }

}


