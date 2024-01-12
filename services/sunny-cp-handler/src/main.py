import messageQueue
from make_pfolio import MakePfolio
import sunny_cp_starter


if __name__ == '__main__':
    print("MAKING PFOLIO")
    MakePfolio.main()
    print("STARTING SUNNY CP")
    sunny_cp_starter.main(['test.mzn'])
    #result_queue = messageQueue.SolverResultQueue()
    #result_queue.consume()