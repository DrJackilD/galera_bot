import re

from telegram.ext.filters import BaseFilter


class MentionFilter(BaseFilter):
    """
    Filter for messages, which is targeted to specific contact
    """
    name = 'filters.BotContact'

    def __init__(self, contact_name: str):
        self.contact_name = contact_name

    def filter(self, message):
        mention_pattern = re.compile(f'@{self.contact_name} .+')
        return mention_pattern.match(message.text)

