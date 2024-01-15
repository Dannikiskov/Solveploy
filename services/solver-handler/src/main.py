import messageQueue


if __name__ == '__main__':
    result_queue = messageQueue.SolverResultQueue()
    result_queue.consume()