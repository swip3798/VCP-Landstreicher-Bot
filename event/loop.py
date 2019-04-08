import time
import threading
from datetime import datetime

reminder_steps = {
    #Format is [time_offset_in_seconds, description, follow_up_step]
    0: [14*24*3600, "In zwei Wochen", 1],
    1: [7*24*3600, "In einer Woche", 2],
    2: [24*3600, "Morgen", 3],
    3: [3600, "In einer Stunde", 4],
    4: [0, "Jetzt", None]
}

class EventLoop():

    def __init__(self, event_table, bot, logger, wait_time = 60):
        self.events = event_table
        self.bot = bot
        self.wait_time = wait_time
        self.logger = logger

    def trigger_event(self, event, preremember):
        if preremember == 4:
            answer = "Termin Erinnerung (Jetzt):\n\n" + str(event["message"])
            self.events.delete(lambda x: x["id"] == event["id"])
        else:
            step = reminder_steps[preremember]
            timestamp = datetime.fromtimestamp(event["timestamp"])
            answer = "Termin Erinnerung (" + step[1] + ", " + datetime.strftime(timestamp, "%d.%m.%y %H:%M Uhr") + "):\n\n" + str(event["message"])
            event["preremember"] = step[2]
            self.events.update(event)
        self.bot.send_message(event["chat_id"], answer)
    
    def run(self):
        try:
            while True:
                events_to_trigger = self.events.search(lambda x: x["timestamp"] - reminder_steps[x["preremember"]][0] < time.time())
                for i in events_to_trigger:
                    self.logger.info("Started event trigger")
                    thread = threading.Thread(target=self.trigger_event, args=(i,i["preremember"]))
                    thread.start()
                    thread.join()
                    self.logger.info("Finished event")
                time.sleep(self.wait_time)
        except KeyboardInterrupt:
            return 0
