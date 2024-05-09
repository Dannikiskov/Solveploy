import messageQueue as mq
import k8sHandler as k8s

if __name__ == '__main__':
    mq.rmq_init()
    k8s.resource_init()
    mq.consume()
