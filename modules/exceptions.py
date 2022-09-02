"""
Custom exceptions for the bot.
"""


class WrongTypeArgument(Exception):
    """
    Raised when the type of argument is not the expected one.
    """


class MissingGuildPermission(Exception):
    """
    Raised when the user is missing guild permission.
    """

class NotOwnerLMAO(Exception):
    """
    Raised when user is not owner
    """

class MusicException():
    """
    Raised when the music module encounters an error.
    """
    class AuthorNotInVoice(Exception):
        """
        Raised when the author is not in the voice channel.
        """

    class NoPermissionToConnect(Exception):
        """
        Raised when the bot does not have permission to join the voice channel.
        """

    class DifferentVoice(Exception):
        """
        Raised when the bot and author in different voice channels.
        """
