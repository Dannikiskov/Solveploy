import messageQueue
import database
if __name__ == '__main__':
    messageQueue.rmq_init()
    database.database_init()
    messageQueue.consume()
