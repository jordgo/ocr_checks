import abc
from dataclasses import dataclass


@dataclass
class SenderCardNumber(abc.ABC):
    sender_card_number: str = None

    @abc.abstractmethod
    def parse_sender_card_number(self):
        return NotImplemented


@dataclass
class SenderName(abc.ABC):
    sender_name: str = None

    @abc.abstractmethod
    def parse_sender_name(self):
        return NotImplemented


@dataclass
class RecipientName(abc.ABC):
    recipient_name: str = None

    @abc.abstractmethod
    def parse_recipient_name(self):
        return NotImplemented


@dataclass
class RecipientPhone(abc.ABC):
    recipient_phone: str = None

    @abc.abstractmethod
    def parse_recipient_phone(self):
        return NotImplemented


@dataclass
class RecipientCardNumber(abc.ABC):
    recipient_card_number: str = None

    @abc.abstractmethod
    def parse_recipient_card_number(self):
        return NotImplemented


@dataclass
class TransactionNumberForRecipient(abc.ABC):
    transaction_number_for_recipient: str = None

    @abc.abstractmethod
    def parse_transaction_number_for_recipient(self):
        return NotImplemented
