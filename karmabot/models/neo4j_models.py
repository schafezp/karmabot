from dataclasses import dataclass

@dataclass
def User():
    user_id: int
    user_name: str
    karma: int