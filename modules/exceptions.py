class WrongTypeArgument(Exception):
    """
    Raised when the type of argument is not the expected one.
    """
    pass

class MissingGuildPermission(Exception):
    """
    Raised when the user is missing guild permission.
    """
    pass

class MusicException():
    """
    Raised when the music module encounters an error.
    """
    class AuthorNotInVoice(Exception):
        """
        Raised when the author is not in the voice channel.
        """
        pass

    class NoPermissionToConnect(Exception):
        """
        Raised when the bot does not have permission to join the voice channel.
        """
        pass

    class DifferentVoice(Exception):
        """
        Raised when the bot and author in different voice channels.
        """
        pass

