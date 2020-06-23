//
// Created by Jason.Z on 2020/6/16.
//

#ifndef SOCKETSERVERCPLUS_UTIL_H
#define SOCKETSERVERCPLUS_UTIL_H
#include <cstdlib>
#include <unistd.h>
ssize_t readn(int fd, void *buff, size_t n);
ssize_t writen(int fd, void *buff, size_t n);
void handle_for_sigpipe();
int setSocketNonBlocking(int fd);

#endif //SOCKETSERVERCPLUS_UTIL_H
