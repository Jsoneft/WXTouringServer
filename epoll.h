//
// Created by Jason.Z on 2020/6/24.
//

#ifndef SOCKETSERVERCPLUS_EPOLL_H
#define SOCKETSERVERCPLUS_EPOLL_H
#include <vector>
#include <unordered_map>
#include <sys/epoll.h>
#include <memory>

/**
 *  @struct Epoll
 *  @brief ZJX's Epoll struct
 *
 *  @var epoll_fd       File descriptor that indicates the event-list
 *  @var events         epoll_events list
 */
class Epoll{
public:
    static epoll_event *events;
    static int epoll_fd;
public:
    static int epoll_init(int max_events, int listen_num);
    static int epoll_add(int fd, __uint32_t events);
    static int epoll_mod(int fd, __uint32_t events);
    static int epoll_del(int fd, __uint32_t events = (EPOLLIN | EPOLLET | EPOLLONESHOT));
    static int zjx_epoll_wait(int listen_fd, int max_event, int timeout);
    static int zjx_deal(int listen_fd, int ready_num);
    static void acceptConnection(int listen_fd, int epoll_fd);
};
#endif //SOCKETSERVERCPLUS_EPOLL_H
