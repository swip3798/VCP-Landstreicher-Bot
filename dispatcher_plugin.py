from telegram.ext import Dispatcher

class AdvancedDispatcher(Dispatcher):

    def process_update(self, update):
        #pylint: disable=E1101
        if self.preprocessor(update):
            super().process_update(update)