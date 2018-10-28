"""Used for formatting the result of db queries
"""
from typing import List, Tuple
from responses import SHOW_KARMA_NO_HISTORY_RESPONSE


def format_show_karma_for_users_in_chat(user_data_rows: List[Tuple[str, str, int]]) -> str:
    """Returns a formatted html message showing the karma for users in a chat
    Takes List of (username, firstname, karma) tuples
    Returns a formatted html message
    """
    #TODO: add optional parameter to output type different than html
    if user_data_rows == []:
        return SHOW_KARMA_NO_HISTORY_RESPONSE

    #TODO: don't modify in place
    user_data_rows.sort(key=lambda user: user[2], reverse=True)
    # use firstname if username not set

    def cleanrow(user):
        """selects desired user attributes to show"""
        if user[0] is None:
            return (user[1], user[2])
        else:
            return (user[0], user[2])
    message_rows = []
    idx = 0
    for user in map(cleanrow, user_data_rows):
        row = f"{user[0]}: {user[1]}"
        if idx == 0:
            row = '🥇' + row
        elif idx == 1:
            row = '🥈' + row
        elif idx == 2:
            row = '🥉' + row
        idx = idx + 1
        message_rows.append(row)
    message = "\n".join(message_rows)
    message = "<b>Username: Karma</b>\n" + message
    return message