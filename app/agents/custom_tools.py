from agno.tools import Toolkit

class TestToolHelloWorldToName(Toolkit):

    def __init__(self):
        super().__init__(name="HelloToUserName")
        self.register(self.CustomHelloToUserName)

    def CustomHelloToUserName(self, username: str) -> str:
        """
        Generates a flashy personalized welcome message.

        Args:
            username (str): The name of the user.

        Returns:
            str: A colorful ASCII welcome message.
        """

        return f"""
╔══════════════════════════════════════════════╗
║                                              ║
║       ✨  WELCOME TO THE SYSTEM!  ✨         ║
║                                              ║
║          🚀 HELLO, {username.upper():<25}║
║                                              ║
║       ┌──────────────────────────┐           ║
║       │  STATUS: ONLINE 🟢       │           ║
║       │  ACCESS: GRANTED 🔓      │           ║
║       │  USER: {username:<21}│           ║
║       └──────────────────────────┘           ║
║                                              ║
║     "Great things start with a hello!"      ║
║                                              ║
╚══════════════════════════════════════════════╝
"""