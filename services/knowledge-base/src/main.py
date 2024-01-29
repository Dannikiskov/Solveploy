import messageQueue
import database
import time
if __name__ == '__main__':
    messageQueue.rmq_init()
    max_attempts = 5
    attempts = 0
    while attempts < max_attempts:
        try:
            database.database_init()
            break
        except Exception as e:
            attempts += 1
            print(f"Attempt {attempts} failed: {str(e)}")
            time.sleep(1)
    else:
        print("Max attempts reached. Exiting...")
        exit(1)
    
    messageQueue.consume()
