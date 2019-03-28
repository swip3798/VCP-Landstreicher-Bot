import time
import threading

class EventLoop():

    def __init__(self, event_table, bot, logger, wait_time = 60):
        self.events = event_table
        self.bot = bot
        self.wait_time = wait_time
        self.logger = logger

    def trigger_event(self, event, preremember):
        self.bot.send_message(event["chat_id"], "Termin Erinnerung:\n\n" + str(event["message"]))
        if not preremember:
            self.events.delete(lambda x: x["id"] == event["id"])
        else:
            event["preremember"] = True
            self.events.update(event)
    
    def run(self):
        try:
            while True:
                onDueItems = self.events.search(lambda x: x["timestamp"] < time.time() and x["preremember"])
                onDueItems_pre = self.events.search(lambda x: x["timestamp"] < time.time() + (3600*24) and not x["preremember"])
                for i in onDueItems:
                    self.logger.info("Started event trigger")
                    thread = threading.Thread(target=self.trigger_event, args=(i,False))
                    thread.start()
                    thread.join()
                    self.logger.info("Finished event")
                for i in onDueItems_pre:
                    self.logger.info("Started pre_event trigger")
                    thread = threading.Thread(target=self.trigger_event, args=(i,True))
                    thread.start()
                    thread.join()
                    self.logger.info("Finished event")
                time.sleep(self.wait_time)
        except KeyboardInterrupt:
            return 0
