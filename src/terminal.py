"""
Main Terminal Interface
Provides the CLI loop with command history and auto-completion
"""

import os
import sys
from typing import List, Optional
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.shortcuts import CompleteStyle
import colorama
from colorama import Fore, Back, Style

# Add the src directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))
from command_handler import CommandHandler


class CommandCompleter(Completer):
    """Auto-completion for commands and file paths"""
    
    def __init__(self, command_handler: CommandHandler):
        self.command_handler = command_handler
        self.commands = list(command_handler.supported_commands.keys())
    
    def get_completions(self, document, complete_event):
        """Get completions for the current input"""
        text = document.text_before_cursor
        words = text.split()
        
        if not words or (len(words) == 1 and not text.endswith(' ')):
            # Complete command names
            current_word = words[0] if words else ''
            for command in self.commands:
                if command.startswith(current_word.lower()):
                    yield Completion(command, start_position=-len(current_word))
        else:
            # Complete file/directory names
            current_word = words[-1] if not text.endswith(' ') else ''
            self._complete_path(current_word, document)
    
    def _complete_path(self, current_word: str, document):
        """Complete file and directory paths"""
        try:
            if current_word.startswith('/') or (len(current_word) > 1 and current_word[1] == ':'):
                # Absolute path
                base_path = os.path.dirname(current_word) if current_word else '/'
                prefix = os.path.basename(current_word) if current_word else ''
            else:
                # Relative path
                base_path = self.command_handler.current_directory
                if current_word:
                    if os.sep in current_word:
                        base_path = os.path.join(base_path, os.path.dirname(current_word))
                        prefix = os.path.basename(current_word)
                    else:
                        prefix = current_word
                else:
                    prefix = ''
            
            if os.path.exists(base_path):
                try:
                    for item in os.listdir(base_path):
                        if item.startswith(prefix):
                            full_path = os.path.join(base_path, item)
                            if os.path.isdir(full_path):
                                completion = item + os.sep
                            else:
                                completion = item
                            
                            yield Completion(completion, start_position=-len(prefix))
                except PermissionError:
                    pass
        except Exception:
            pass


class Terminal:
    """Main terminal class that handles the CLI interface"""
    
    def __init__(self):
        # Initialize colorama for Windows compatibility
        colorama.init(autoreset=True)
        
        self.command_handler = CommandHandler()
        self.history = InMemoryHistory()
        self.completer = CommandCompleter(self.command_handler)
        self.running = True
        
        # Colors
        self.prompt_color = Fore.GREEN
        self.success_color = Fore.WHITE
        self.error_color = Fore.RED
        self.info_color = Fore.CYAN
        
    def run(self):
        """Main terminal loop"""
        try:
            while self.running:
                try:
                    # Create prompt with current directory
                    current_dir = os.path.basename(self.command_handler.current_directory) or self.command_handler.current_directory
                    prompt_text = f"{self.prompt_color}{current_dir}> {Style.RESET_ALL}"
                    
                    # Get user input with history and completion
                    user_input = prompt(
                        prompt_text,
                        history=self.history,
                        completer=self.completer,
                        complete_style=CompleteStyle.READLINE_LIKE
                    )
                    
                    if not user_input.strip():
                        continue
                    
                    # Execute command
                    result = self.command_handler.execute_command(user_input.strip())
                    
                    # Handle special exit command
                    if result.get("output") == "exit":
                        self.running = False
                        print(f"{self.info_color}Goodbye!{Style.RESET_ALL}")
                        break
                    
                    # Display output
                    self._display_result(result)
                    
                except KeyboardInterrupt:
                    print(f"\n{self.info_color}Use 'exit' or 'quit' to leave the terminal{Style.RESET_ALL}")
                    continue
                except EOFError:
                    # Ctrl+D pressed
                    print(f"\n{self.info_color}Goodbye!{Style.RESET_ALL}")
                    break
                    
        except Exception as e:
            print(f"{self.error_color}Fatal error: {e}{Style.RESET_ALL}")
            sys.exit(1)
    
    def _display_result(self, result: dict):
        """Display command execution result"""
        if result["success"]:
            if result["output"]:
                # Handle special formatting for clear command
                if result["output"] == "\033[2J\033[H":
                    os.system('cls' if os.name == 'nt' else 'clear')
                else:
                    print(f"{self.success_color}{result['output']}{Style.RESET_ALL}")
        else:
            if result["error"]:
                print(f"{self.error_color}Error: {result['error']}{Style.RESET_ALL}")
        
        # Show any additional error information
        if result.get("error") and result["success"]:
            print(f"{self.error_color}Warning: {result['error']}{Style.RESET_ALL}")
    
    def get_command_history(self) -> List[str]:
        """Get command history for debugging/testing"""
        return [entry for entry in self.history.get_strings()]
    
    def execute_command_directly(self, command: str) -> dict:
        """Execute a command directly (useful for testing)"""
        return self.command_handler.execute_command(command)