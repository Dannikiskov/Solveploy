import messageQueue

if __name__ == '__main__':
    messageQueue.rmq_init()
    messageQueue.consume()
