#!/usr/bin/env python
import messageQueue

result_queue = messageQueue.SolverResultQueue()

if __name__ == '__main__':
    result_queue.consume()