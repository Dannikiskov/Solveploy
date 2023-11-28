import messageQueue

mq = messageQueue.MessageQueue()
def main():
    job_data = mq.waitForJob()
    print("solver-handler main::", job_data, flush=True)
    mq.sendResult(job_data)


if __name__ == '__main__':
    print("Calling main", flush=True)
    main()