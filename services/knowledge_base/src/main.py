import messageQueue as mq
import database
import time
if __name__ == '__main__':
    mq.rmq_init()

    while True:
        try:
            database.database_init()
            break
        except Exception as e:
            print(f"Attempt failed: {str(e)}\n retryin in 5 seconds...")
            time.sleep(5)
    
    mq.consume()
