#include <iostream>
#define PY_SSIZE_T_CLEAN
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
//int main(){
//    Py_Initialize();
//    if (!Py_IsInitialized())
//    {
//        printf("Python init failed!\n");
//        PyErr_Print();//打印错误信息，库函数
//        return -1;
//    }
//    PyRun_SimpleString("import sys");    //调用python代码
//    PyRun_SimpleString("sys.path.append('./')");    //将当前目录添加到python路径
//    PyObject *pModule = NULL;    //python模块
//
//    if( !(pModule = PyImport_ImportModule("handle") ) ){
//        return -1;
//    }
//    PyObject *dic = PyModule_GetDict(pModule);
//    if(!dic) {
//        printf("错误!\n");
//        return -1;
//    }
//    /* 获得sum函数地址并验证 */
//    PyObject *func = PyDict_GetItemString(dic,"handleRequset");
//    char s[8192] = {R"(GET / HTTP/1.1\r\n\r\n<html><head><title></title></head><body>yours</body></html>\r\n)"};
//    PyObject *args = Py_BuildValue("(s)",s);
//    if (args == NULL) {
//        printf("restNotifyFunc, Py_BuildValue run OOM.\n");
//        return -1;
//    }
//    PyObject *resulet = PyObject_CallObject(func, args);
//    char *cRst;
//    PyArg_Parse(resulet,"s",&cRst);
//    cout<< "cRST:"<<cRst;
//    return 0;
//}

int main(int argc,char* argv[])
{
    Py_Initialize();
    if (!Py_IsInitialized())
    {
        printf("Python init failed!\n");
        PyErr_Print();//打印错误信息，库函数
        return -1;
    }
    PyRun_SimpleString("import sys");    //调用python代码
    PyRun_SimpleString("sys.path.append('./')");    //将当前目录添加到python路径
    PyObject *pModule = NULL;    //python模块

    if( !(pModule = PyImport_ImportModule("handle") ) ){
        printf("ImportModule failed");//打印错误信息，库函数
        return -1;
    }
    PyObject *dic = PyModule_GetDict(pModule);
    if(!dic) {
        printf("Dict obtain err");
        return -1;
    }
    /* 获得handleRequest函数地址并验证 */
    PyObject *func = PyDict_GetItemString(dic,"handleRequest");

    int sfd;
    sfd=socket(AF_INET,SOCK_STREAM,0);//服务器端生成一个socket描述符
    if(-1==sfd)
    {
        perror("socket");
        return -1;
    }
    struct sockaddr_in ser;//该结构体变量存储ip、port等socket信息数据
    memset(&ser,0,sizeof(ser));//清空结构体
    ser.sin_family=AF_INET;//采用ipv4协议
    ser.sin_port=htons(80);//端口号，将主机字节序的port转换为网络字节序的port
    ser.sin_addr.s_addr=inet_addr("0.0.0.0");//ip，将点分十进制ip转换为网络字节序的32位二进制数值
    int ret;
    setsockopt(sfd, SOL_SOCKET, SO_REUSEADDR,(struct sockaddr*)&ser,sizeof(ser) );//允许重用地址
    ret=bind(sfd,(struct sockaddr*)&ser,sizeof(ser));//将socket描述符与服务器的ip、port绑定

    if(-1==ret)
    {
        perror("bind");
        return -1;
    }
    printf("I am here\n");

    listen(sfd,10);
    printf("I am here 2\n");
    //使服务器的这个端口和ip处于监听状态，等待客户机的连接请求;10:同时能处理的最大连接请求数
    int new_fd=-1;
    struct sockaddr_in cli;
    int len=sizeof(cli);
    char buf[8192]={""};
    fd_set rdset;
    fd_set tmpset;//tmpset记录我们要监控的描述符
    FD_ZERO(&tmpset);//清空描述符集
    FD_SET(0,&tmpset);//将标准输入注册为要监控的描述符
    FD_SET(sfd,&tmpset);//将sfd注册为要监控的描述符
    while(1)
    {
        FD_ZERO(&rdset);
        memcpy(&rdset,&tmpset,sizeof(fd_set));//将需要监控的描述符集拷贝到rdset
        ret=select(11,&rdset,NULL,NULL,NULL);//select函数监控rdset描述符集中相关文件的读变化
        if(ret>0)
        {
            if(FD_ISSET(sfd,&rdset))//检查sfd是否发生读变化，即是否侦听到客户端的链接请求
            {
                new_fd=accept(sfd, (struct sockaddr*)&cli, reinterpret_cast<socklen_t *>(&len));
                //接收客户端的连接请求，并返回一个新的socket描述符，用于标识服务器与这个特定客户端的连接
                if(-1==new_fd)
                {
                    perror("accept");
                    return -1;
                }
                FD_SET(new_fd,&tmpset);//将该新的描述符加入监控集
                printf("Server:已成功连接到客户端%s:%d,您可以向客户端发送信息了!\n",inet_ntoa(cli.sin_addr),ntohs(cli.sin_port));
            }
            if(FD_ISSET(new_fd,&rdset))//检查new_fd是否发生读变化，即客户端是否发送信息过来
            {
                memset(buf, 0, sizeof(buf));
                ret = recv(new_fd, buf, sizeof(buf), 0);//接收客户端发来的信息
                if (ret > 0) {
                    PyObject *args = Py_BuildValue("(s)", buf);
                    if (args == NULL) {
                        printf("restNotifyFunc, Py_BuildValue run OOM.\n");
                        return -1;
                    }
                    PyObject *result = PyObject_CallObject(func, args);
                    memset(buf, 0, sizeof(buf));
                    char *cStr;
                    PyArg_Parse(result, "s", &cStr);
                    std::cout << "result:" << cStr << std::endl;

                    ret = send(new_fd, cStr, strlen(cStr) - 1, 0);//将标准输入的信息发送给客户端
                    if (ret <= 0) {
                        printf("Server:您未输入任何信息，请重新输入!\n");//输入为空的处理
                    }
                    close(new_fd);
                    FD_CLR(new_fd, &tmpset);
                    std::cout << "关闭客户端连接" << std::endl;
                } else if (0 == ret) {
                    printf("byebye,客户端已下线!\n");
                    close(new_fd);
                    FD_CLR(new_fd, &tmpset);//从集合当中移除该new_fd
                }
            }
        }
    }
    close(sfd);
}