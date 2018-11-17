from dataclasses import dataclass

@dataclass
class User():
    user_id: int
    user_name: str
    karma: int


@dataclass
class Chat():
    chat_id: int
    chat_name: str


@dataclass
class Message():
    message_id: int
    chat_id: str
    author_user_id: int
    message_text: str