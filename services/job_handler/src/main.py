import messageQueue as mq

if __name__ == '__main__':
    print("NEW JH", flush=True)
    mq.rmq_init()
    mq.consume()
