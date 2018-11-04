from dataclasses import dataclass

@dataclass
class User():
    user_id: int
    user_name: str
    karma: int