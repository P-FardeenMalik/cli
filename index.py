#!/usr/bin/env python3
"""
Python-Based Command Terminal - Standalone Version
Entry point for the terminal application (submission version)
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    # Try to import the full-featured terminal
    from terminal import Terminal
    
    def index():
        """Main function to start the terminal"""
        print("Python-Based Command Terminal")
        print("Type 'help' for available commands or 'exit' to quit")
        print("-" * 50)
        
        terminal = Terminal()
        terminal.run()
        
except ImportError:
    # Fallback to basic terminal if dependencies aren't available
    from command_handler_standalone import CommandHandler
    
    def index():
        """Fallback main function with basic terminal"""
        print("Python-Based Command Terminal")
        print("Type 'help' for available commands or 'exit' to quit")
        print("-" * 50)
        
        handler = CommandHandler()
        
        while True:
            try:
                current_dir = os.path.basename(handler.current_directory) or handler.current_directory
                command = input(f"{current_dir}> ")
                
                if not command.strip():
                    continue
                
                result = handler.execute_command(command.strip())
                
                if result.get("output") == "exit":
                    print("Goodbye!")
                    break
                
                if result["success"]:
                    if result["output"]:
                        if result["output"] == "\033[2J\033[H":
                            os.system('cls' if os.name == 'nt' else 'clear')
                        else:
                            print(result["output"])
                else:
                    if result["error"]:
                        print(f"Error: {result['error']}")
                        
            except KeyboardInterrupt:
                print("\nUse 'exit' or 'quit' to leave the terminal")
                continue
            except EOFError:
                print("\nGoodbye!")
                break

if __name__ == "__main__":
    index()