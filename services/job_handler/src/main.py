import messageQueue as mq
import k8Handler as k8h

if __name__ == '__main__':
    mq.rmq_init()
    k8h.resource_init()
    mq.consume()
