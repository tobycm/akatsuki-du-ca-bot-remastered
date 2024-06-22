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

    class NotConnected(Exception):
        """
        Raised when the bot is not connected to a voice channel.
        """

    class NotPlaying(Exception):
        """
        Raised when the player is not playing.
        """

    class QueueEmpty(Exception):
        """
        Raised when the queue is empty.
        """

    class AlreadyConnected(Exception):
        """
        Raised when the bot is already connected to a voice channel.
        """

    class TrackNotFound(Exception):
        """
        Raised when the bot can't find the track.
        """


class UnknownException(Exception):
    """
    Raised when the bot encounters an unknown error.
    """
