//
// Created by Jason.Z on 2020/6/16.
//

#include "util.h"
#include <fcntl.h>
#include <csignal>
#include <cerrno>
#include <cstring>

ssize_t /* Read n bytes from file descriptor. */
readn(int fd, void *buff, size_t n){
    size_t nleft = n;
    ssize_t nread = 0;
    ssize_t readSum = 0;
    char *ptr = (char*) buff;
    while (nleft > 0){
        if((nread = read(fd, ptr, nleft)) < 0){
            // 读入出错
            if (errno == EINTR)
                nread = 0;
            else if (errno == EAGAIN){
                return readSum;
            } else return -1;
        }else if(nread == 0)
            break;
        readSum += nread;
        nleft -= nread;
        // 偏移量
        ptr += nread;
    }
    return  readSum;
}


ssize_t /* Write n bytes to a descriptor. */
writen(int fd, void *buff, size_t n){
    size_t nleft = n;
    ssize_t nwritten = 0;
    ssize_t writeSum = 0;
    char *ptr = (char *)buff;
    while (nleft>0){
        if((nwritten = write(fd, ptr, nleft)) < 0){
            if(errno == EINTR || errno == EAGAIN){
                nwritten = 0;
            } else return -1;
        }
        writeSum += nwritten;
        nleft -= nwritten;
        ptr += nwritten;
    }
    return writeSum;
}

// 写一个读端已经被关闭的管道, 产生信号SIGPIPE. 如果已经忽略改信号或者捕捉该信号并从该处理程序返回, 则write 返回-1, errno 设置为 EPIPE
void handle_for_sigpipe()
{
    struct sigaction sa{};
    memset(&sa, '\0', sizeof(sa));
    sa.sa_handler = SIG_IGN;
    sa.sa_flags = 0;
    if(sigaction(SIGPIPE, &sa, NULL))
        return;
}

int setSocketNonBlocking(int fd)
{
    int flag = fcntl(fd, F_GETFL, 0);
    if(flag == -1)
        return -1;
    if(fcntl(fd, F_SETFL, flag | O_NONBLOCK) == -1)
        return -1;
    return 0;
}
