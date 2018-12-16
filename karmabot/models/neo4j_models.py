from dataclasses import dataclass


@dataclass
class User:
    user_id: str
    user_name: str
    # TODO: add first/last


@dataclass
class Chat:
    chat_id: str
    chat_name: str


@dataclass
class Message:
    message_id: str
    chat_id: str
    author_user_id: str
    message_text: str
