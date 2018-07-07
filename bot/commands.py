class BotCommandHandler:
    default_handler = None
    _commands = {}

    def __init__(self, default_handler):
        self.default_handler = default_handler

    def handle(self, command, bot, update):
        command = self._commands.get(command)
        if command is None:
            return self.default_handler(bot, update)
        return command(bot, update)

    def add_command(self, command, callback):
        self._commands[command] = callback
