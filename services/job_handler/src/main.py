import messageQueue as mq
from solverK8Job import k8s_namespace_init

if __name__ == '__main__':
    k8s_namespace_init()
    mq.rmq_init()
    mq.consume()
