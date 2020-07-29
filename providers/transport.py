import functools
import os
import uuid
from collections import namedtuple
from abc import ABC

import inject
import requests
import telegram


class NotValidNumberOrVin(Exception):
    pass


class CarPlatesApiError(Exception):
    pass


class OpenData:
    def __init__(self):
        pass

    @functools.lru_cache(1024)
    def get_open_data(self, number):
        pass


class AuctionUrlProviderBase(ABC):
    def get_auction_url(self, vin: str) -> str:
        raise NotImplementedError()


class BidfaxGoogleUrlProvider(AuctionUrlProviderBase):
    TEMPLATE_URL = "https://www.google.com/search?q=site%3Abidfax.info+{}&sclient=img&tbm=isch"

    def get_auction_url(self, vin: str) -> str:
        return self.TEMPLATE_URL.format(vin)


class AutoAStat(AuctionUrlProviderBase):
    def __init__(self):
        pass

    def get_auction_url(self, vin: str):
        raise NotImplementedError()


CarPlatesResponse = namedtuple("CarPlatesResponse", ["number", "vin", "auction"])


class CarPlates:
    """Use it to validate that vin/number is correct and get some info"""
    API_NUMBER = "https://api.carplates.app/ua/summary"
    API_VIN = "https://api.carplates.app/vin/summary"
    POST_KEYS = {
        8: "_get_by_number",
        17: "_get_by_vin"
    }

    def __init__(self, api_key=None, auth=None):
        self.api_key = api_key or os.getenv("CAR_PLATES_KEY")
        self.auth = auth or os.getenv("CAR_PLATES_AUTH")

    def _get_headers(self):
        return {
            "Content-Type": "application/json",
            "API-Key": str(self.api_key),
            "Authorization": str(self.auth),
            "UUID": str(uuid.uuid4())
        }

    def get_data(self, number_or_vin: str) -> CarPlatesResponse:
        number = number_or_vin.upper().replace(" ", "")
        request_key = self.POST_KEYS.get(len(number))
        if request_key is None:
            raise NotValidNumberOrVin()
        return getattr(self, request_key)(number)

    def _get_by_vin(self, vin: str) -> CarPlatesResponse:
        response = requests.post(self.API_VIN, json={"vin": vin},
                                 headers=self._get_headers())
        if response.status_code != 200:
            raise CarPlatesApiError()

        json_data = response.json()
        if json_data.get("success") and json_data.get("plate_en"):
            plate = json_data.get("plate_en")
            vin = json_data.get("vin")
            was_at_auction = bool(any(
                (record.get("id", "") == "was_at_auction" for record in json_data.get("unicards", []) if
                 isinstance(record, dict))))
            response = CarPlatesResponse(plate, vin, was_at_auction)
            return response
        raise CarPlatesApiError()

    def _get_by_number(self, number: str) -> CarPlatesResponse:
        response = requests.post(self.API_NUMBER, json={"number": number},
                                 headers=self._get_headers())
        if response.status_code != 200:
            raise CarPlatesApiError()

        json_data = response.json()
        if json_data.get("success"):
            plate = json_data.get("plate_en")
            vin = None
            was_at_auction = bool(any(
                (record.get("id", "") == "was_at_auction" for record in json_data.get("unicards", []) if
                 isinstance(record, dict))))
            response = CarPlatesResponse(plate, vin, was_at_auction)
            return response
        raise CarPlatesApiError()


class Transport:
    car_plates = inject.attr(CarPlates)
    auction_provider = inject.attr(AuctionUrlProviderBase)

    def find_vin_by_number(self):
        pass

    def get_auction_url_by_vin(self, vin):
        return self.auction_provider.get_auction_url(vin)

    def get_auction_url_by_number(self, number):
        pass

    def handle(self, bot, update):
        vin_or_number = update.message.text[7:]
        try:
            data = self.car_plates.get_data(vin_or_number)
        except NotValidNumberOrVin:
            with open("media/pulp_fiction.jpg", "rb") as fh:
                bot.send_photo(update.message.chat_id, fh, caption="Чекни вин или номер",
                               reply_to_message_id=update.message.message_id)
            return
        except CarPlatesApiError:
            bot.send_message(update.message.chat_id, "Походу такой тачки нет",
                             reply_to_message_id=update.message.message_id, parse_mode=telegram.ParseMode.MARKDOWN)
            return
        auction_url = ""
        if data.auction and data.vin:
            auction_url = self.get_auction_url_by_vin(data.vin)
        message = (f"{update.message.from_user.name}\n"
                   f"Вот что найдено:\n"
                   f"Гос. номер: {data.number}\n"
                   f"VIN: {data.vin if data.vin else 'Не найден'}\n"
                   f"Аукцион: {auction_url}")
        if data.vin is None:
            message = (f"Поиск VIN'а по Гос номеру WIP.\n"
                       f"Вин можно найти через @OpenDataUABot или на https://policy-web.mtsbu.ua")
        bot.send_message(update.message.chat_id, message, parse_mode=telegram.ParseMode.MARKDOWN)
