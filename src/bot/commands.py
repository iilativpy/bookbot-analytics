"""
Command definitions and routing for the Telegram bot.
"""

from typing import Dict, Callable


class BotCommands:
    """
    Command registry for the bot.
    Maps command names to descriptions.
    """
    
    COMMANDS = {
        "start": "Start the bot and show welcome message",
        "help": "Show available commands and usage examples",
        "stats": "Get current month booking statistics",
        "compare": "Compare booking data between periods",
        "predict": "Generate booking predictions",
        "trends": "Analyze booking trends",
        "cancellations": "View cancellation statistics",
        "returns": "View return customer statistics",
        "menu": "Show main menu with quick actions",
    }
    
    @classmethod
    def get_command_list(cls) -> str:
        """
        Get formatted list of commands.
        
        Returns:
            Formatted string with all commands
        """
        commands = []
        for cmd, desc in cls.COMMANDS.items():
            commands.append(f"/{cmd} - {desc}")
        return "\n".join(commands)
    
    @classmethod
    def get_bot_commands(cls) -> list:
        """
        Get commands in format for Telegram BotCommand.
        
        Returns:
            List of (command, description) tuples
        """
        return [(cmd, desc) for cmd, desc in cls.COMMANDS.items()]
    
    @classmethod
    def is_valid_command(cls, command: str) -> bool:
        """
        Check if command is valid.
        
        Args:
            command: Command name (without /)
            
        Returns:
            True if valid
        """
        return command in cls.COMMANDS


class CommandRouter:
    """Route commands to appropriate handlers."""
    
    def __init__(self):
        """Initialize command router."""
        self.handlers: Dict[str, Callable] = {}
    
    def register(self, command: str, handler: Callable):
        """
        Register a command handler.
        
        Args:
            command: Command name
            handler: Handler function
        """
        self.handlers[command] = handler
    
    def route(self, command: str) -> Callable:
        """
        Get handler for a command.
        
        Args:
            command: Command name
            
        Returns:
            Handler function or None
        """
        return self.handlers.get(command)
    
    def has_handler(self, command: str) -> bool:
        """
        Check if command has a handler.
        
        Args:
            command: Command name
            
        Returns:
            True if handler exists
        """
        return command in self.handlers
