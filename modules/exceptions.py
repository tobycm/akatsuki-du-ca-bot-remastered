"""
Custom exceptions for the bot.
"""


class WrongArgumentType(Exception):
    """
    Raised when the type of argument is not the expected one.
    """


class LangNotAvailable(Exception):
    """
    Raised when content isn't available in user language.
    """


class MusicException:
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


class UnknownException(Exception):
    """
    Raised when the bot encounters an unknown error.
    """
