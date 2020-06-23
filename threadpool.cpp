//
// Created by Jason.Z on 2020/6/23.
//

#include "threadpool.h"

/**
 *  @struct threadpool
 *  @brief The threadpool struct
 *
 *  @var notify       Condition variable to notify worker threads.
 *  @var threads      Array containing worker threads ID.
 *  @var thread_count Number of threads
 *  @var queue        Array containing the task queue.
 *  @var queue_size   Size of the task queue.
 *  @var head         Index of the first element.
 *  @var tail         Index of the next element.
 *  @var count        Number of pending tasks
 *  @var shutdown     Flag indicating if the pool is shutting down
 *  @var started      Number of started threads
 */

pthread_mutex_t ThreadPool::lock = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t ThreadPool::notify = PTHREAD_COND_INITIALIZER;
std::vector<pthread_t> ThreadPool::threads;
std::vector<ThreadPoolTask> ThreadPool::queue;
int ThreadPool::thread_count = 0;
int ThreadPool::queue_size = 0;
int ThreadPool::head = 0;
int ThreadPool::tail = 0;
int ThreadPool::count = 0;
int ThreadPool::shutdown = 0;
int ThreadPool::started = 0;

// 创建一个线程池
int ThreadPool::threadpool_create(int _thread_count, int _queue_size) {
    // _thread_count: 多少个线程， _queue_size 最长有多少个
    bool err = false;
    if (_thread_count <= 0 || _thread_count > MAX_THREADS || _queue_size <= 0 || _queue_size > MAX_QUEUE) {
        // 初始化
        _thread_count = 4;
        _queue_size = 1024;
    }
    thread_count = 0;
    queue_size = _queue_size;
    head = tail = count = 0;
    shutdown = started = 0;
    threads.resize(_thread_count);
    queue.resize(_queue_size);
    for (int i = 0; i < _thread_count; i++) {
        if (pthread_create(&threads[i], NULL, threadpool_thread, NULL) != 0) {
            // 创建线程失败
            perror("线程池创建线程失败");
            return -1;
        }
        ++started;
        ++thread_count;

    }
    return 0;
}


// 线程入口函数
void *ThreadPool::threadpool_thread(void *args) {
    while (true) {
        ThreadPoolTask task;
        // 每次执行下一个任务先整到队列里等notify
        pthread_mutex_lock(&lock);
        while (count == 0 && !shutdown) {
            // 解锁之后加入等待队列，触发条件之后又上锁
            pthread_cond_wait(&notify, &lock);
        }
        if ((shutdown == immediate_shutdown) || (shutdown == graceful_shutdown && count == 0)) {
            // 唯一出口
            break;
        }
        task.fun = queue[head].fun;
        task.args = queue[head].args;
        queue[head].fun = NULL;
        queue[head].args.reset();
        head = (head + 1) % queue_size;
        count--;
        pthread_mutex_unlock(&lock);
        // 执行函数
        (task.fun)(task.args);
    }

    started--;
    pthread_mutex_unlock(&lock);
    printf("This threadpool thread finishs!\n");
    pthread_exit(NULL);
}

int ThreadPool::threadpool_add(const std::shared_ptr<void>& args, const std::function<void(std::shared_ptr<void>)> &fun) {
    int next, err = 0;
    if (pthread_mutex_lock(&lock) != 0) {
        return THREADPOOL_LOCK_FAILURE;
    }

    do {

        // 出问题之前先更新next
        next = (tail + 1) % queue_size;

        // 队列满
        if (count == queue_size) {
            err = THREADPOOL_QUEUE_FULL;
            break;
        }

        // 已关闭
        if (shutdown) {
            err = THREADPOOL_SHUTDOWN;
            break;
        }
        queue[tail].fun = fun;
        queue[tail].args = args;
        tail = next;
        count++;

        /* pthread_cond_signal  */
        if (pthread_cond_signal(&notify) != 0) {
            // signal 通知某一个线程
            err = THREADPOOL_LOCK_FAILURE;
            break;
        }

    } while (false);

    if (pthread_mutex_unlock(&lock) != 0) {
        err = THREADPOOL_LOCK_FAILURE;
    }
    return err;
}

// 毁锁
int ThreadPool::threadpool_free() {
    if (started > 0) {
        // 还有线程在跑
        return THREADPOOL_INVALID;
    }

    // 已经没有正在运行的线程
    // 上锁的原因是等其他事务释放锁资源后在删除掉(好像不会有事务占用锁资源，还是写着，显得代码比较健壮)
    pthread_mutex_lock(&lock);

    // 原子操作，不管怎么样这一坨都得执行，不用一个一个判返回
    pthread_mutex_destroy(&lock);
    pthread_cond_destroy(&notify);
    return 0;
}

int ThreadPool::threadpool_destroy(ShutDownOption shutDownOption) {
    printf("Thread pool destroy !\n");
    int i, err = 0;
    if (pthread_mutex_lock(&lock) != 0){
        return THREADPOOL_LOCK_FAILURE;
    }
    do{
        if(shutdown){
            // 正在关ing
            err = THREADPOOL_SHUTDOWN;
            break;
        }
        shutdown = shutDownOption;
        // 先通知所有线程把手头上的事儿整完，把锁给他们
        if(pthread_cond_broadcast(&notify)!=0 || pthread_mutex_unlock(&lock) != 0){
            err = THREADPOOL_LOCK_FAILURE;
            break;
        }

        // 等所有线程shutdown
        for(int i = 0;i<thread_count;++i){
            if(pthread_join(threads[i], NULL) != 0){
                err = THREADPOOL_THREAD_FAILURE;
            }
        }
    }while (false);
    if(!err){
        threadpool_free();
    }
    return err;
}