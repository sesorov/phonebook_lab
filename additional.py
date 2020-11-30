class Text:
    """Container for text formatting codes"""
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    F_LightGreen = "\x1b[92m"
    F_Green = "\x1b[32m"


class GColor:  # Gnome supported
    END = "\x1b[0m"

    # If Foreground is False that means color effect on Background
    @staticmethod
    def RGB(R: int, G: int, B: int, Foreground=True):  # R: 0-255  ,  G: 0-255  ,  B: 0-255
        FB_G = 38  # Effect on foreground
        if not Foreground:
            FB_G = 48  # Effect on background
        return "\x1b[" + str(FB_G) + ";2;" + str(R) + ";" + str(G) + ";" + str(B) + "m"
