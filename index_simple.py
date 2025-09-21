#!/usr/bin/env python3
"""
Python-Based Command Terminal
Simple, self-contained version for submission
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


class CommandHandler:
    """Simple command handler with all required functionality"""
    
    def __init__(self):
        self.current_directory = os.getcwd()
    
    def execute_command(self, command_line):
        """Execute a command and return the result"""
        if not command_line.strip():
            return {"success": True, "output": "", "error": ""}
        
        parts = command_line.strip().split()
        command = parts[0].lower()
        args = parts[1:]
        
        # Command mapping
        commands = {
            'ls': self._ls, 'dir': self._ls,
            'pwd': self._pwd,
            'cd': self._cd,
            'mkdir': self._mkdir,
            'rmdir': self._rmdir,
            'rm': self._rm, 'del': self._rm,
            'touch': self._touch,
            'cat': self._cat, 'type': self._cat,
            'echo': self._echo,
            'help': self._help,
            'clear': self._clear, 'cls': self._clear,
            'exit': self._exit, 'quit': self._exit,
            'cp': self._cp, 'copy': self._cp,
            'mv': self._mv, 'move': self._mv
        }
        
        if command in commands:
            return commands[command](args)
        else:
            return self._system_command(command_line)
    
    def _ls(self, args):
        """List directory contents"""
        try:
            path = args[0] if args else self.current_directory
            if not os.path.isabs(path):
                path = os.path.join(self.current_directory, path)
            
            if not os.path.exists(path):
                return {"success": False, "output": "", "error": f"Path '{path}' does not exist"}
            
            items = []
            for item in sorted(os.listdir(path)):
                full_path = os.path.join(path, item)
                if os.path.isdir(full_path):
                    items.append(f"[DIR]  {item}")
                else:
                    size = os.path.getsize(full_path)
                    items.append(f"[FILE] {item} ({size} bytes)")
            
            return {"success": True, "output": "\n".join(items) or "Directory is empty", "error": ""}
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}
    
    def _pwd(self, args):
        """Print working directory"""
        return {"success": True, "output": self.current_directory, "error": ""}
    
    def _cd(self, args):
        """Change directory"""
        try:
            if not args:
                target = os.path.expanduser("~")
            else:
                target = args[0]
            
            if not os.path.isabs(target):
                target = os.path.join(self.current_directory, target)
            
            if not os.path.exists(target):
                return {"success": False, "output": "", "error": f"Directory '{target}' does not exist"}
            
            if not os.path.isdir(target):
                return {"success": False, "output": "", "error": f"'{target}' is not a directory"}
            
            self.current_directory = os.path.abspath(target)
            os.chdir(self.current_directory)
            return {"success": True, "output": f"Changed directory to: {self.current_directory}", "error": ""}
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}
    
    def _mkdir(self, args):
        """Create directory"""
        try:
            if not args:
                return {"success": False, "output": "", "error": "mkdir: missing directory name"}
            
            for dirname in args:
                path = os.path.join(self.current_directory, dirname) if not os.path.isabs(dirname) else dirname
                os.makedirs(path, exist_ok=False)
            
            return {"success": True, "output": f"Created directory(s): {', '.join(args)}", "error": ""}
        except FileExistsError:
            return {"success": False, "output": "", "error": "Directory already exists"}
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}
    
    def _rm(self, args):
        """Remove files/directories"""
        try:
            if not args:
                return {"success": False, "output": "", "error": "rm: missing file/directory name"}
            
            recursive = "-r" in args
            files = [arg for arg in args if not arg.startswith("-")]
            
            for filename in files:
                path = os.path.join(self.current_directory, filename) if not os.path.isabs(filename) else filename
                
                if not os.path.exists(path):
                    return {"success": False, "output": "", "error": f"File/directory '{filename}' does not exist"}
                
                if os.path.isdir(path):
                    if recursive:
                        shutil.rmtree(path)
                    else:
                        return {"success": False, "output": "", "error": f"'{filename}' is a directory. Use -r flag"}
                else:
                    os.remove(path)
            
            return {"success": True, "output": f"Removed: {', '.join(files)}", "error": ""}
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}
    
    def _rmdir(self, args):
        """Remove empty directory"""
        try:
            if not args:
                return {"success": False, "output": "", "error": "rmdir: missing directory name"}
            
            for dirname in args:
                path = os.path.join(self.current_directory, dirname) if not os.path.isabs(dirname) else dirname
                os.rmdir(path)
            
            return {"success": True, "output": f"Removed directory(s): {', '.join(args)}", "error": ""}
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}
    
    def _touch(self, args):
        """Create empty file"""
        try:
            if not args:
                return {"success": False, "output": "", "error": "touch: missing filename"}
            
            for filename in args:
                path = os.path.join(self.current_directory, filename) if not os.path.isabs(filename) else filename
                Path(path).touch()
            
            return {"success": True, "output": f"Created file(s): {', '.join(args)}", "error": ""}
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}
    
    def _cat(self, args):
        """Display file contents"""
        try:
            if not args:
                return {"success": False, "output": "", "error": "cat: missing filename"}
            
            filename = args[0]
            path = os.path.join(self.current_directory, filename) if not os.path.isabs(filename) else filename
            
            if not os.path.exists(path):
                return {"success": False, "output": "", "error": f"File '{filename}' does not exist"}
            
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            return {"success": True, "output": content, "error": ""}
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}
    
    def _echo(self, args):
        """Echo text"""
        return {"success": True, "output": " ".join(args), "error": ""}
    
    def _cp(self, args):
        """Copy files"""
        try:
            if len(args) < 2:
                return {"success": False, "output": "", "error": "cp: missing source or destination"}
            
            src = os.path.join(self.current_directory, args[0]) if not os.path.isabs(args[0]) else args[0]
            dst = os.path.join(self.current_directory, args[1]) if not os.path.isabs(args[1]) else args[1]
            
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
            
            return {"success": True, "output": f"Copied '{args[0]}' to '{args[1]}'", "error": ""}
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}
    
    def _mv(self, args):
        """Move/rename files"""
        try:
            if len(args) < 2:
                return {"success": False, "output": "", "error": "mv: missing source or destination"}
            
            src = os.path.join(self.current_directory, args[0]) if not os.path.isabs(args[0]) else args[0]
            dst = os.path.join(self.current_directory, args[1]) if not os.path.isabs(args[1]) else args[1]
            
            shutil.move(src, dst)
            return {"success": True, "output": f"Moved '{args[0]}' to '{args[1]}'", "error": ""}
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}
    
    def _clear(self, args):
        """Clear screen"""
        return {"success": True, "output": "\033[2J\033[H", "error": ""}
    
    def _help(self, args):
        """Show help"""
        help_text = """Available Commands:
==================
File Operations:
  ls, dir          - List directory contents
  pwd              - Print working directory  
  cd <path>        - Change directory
  mkdir <name>     - Create directory
  rmdir <name>     - Remove empty directory
  rm <file>        - Remove file (use -r for directories)
  touch <file>     - Create empty file
  cat <file>       - Show file content
  cp <src> <dst>   - Copy file
  mv <src> <dst>   - Move/rename file

Utilities:
  echo <text>      - Print text
  clear, cls       - Clear screen
  help             - Show this help
  exit, quit       - Exit terminal"""
        
        return {"success": True, "output": help_text, "error": ""}
    
    def _exit(self, args):
        """Exit terminal"""
        return {"success": True, "output": "exit", "error": ""}
    
    def _system_command(self, command_line):
        """Execute system command"""
        try:
            result = subprocess.run(command_line, shell=True, capture_output=True, text=True, 
                                  cwd=self.current_directory, timeout=30)
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.stderr else ""
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "output": "", "error": "Command timed out"}
        except Exception as e:
            return {"success": False, "output": "", "error": f"Command not found: {str(e)}"}


def index():
    """Main function to start the terminal"""
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


# Simple test function that automated systems can discover
def test_terminal():
    """Test basic terminal functionality"""
    handler = CommandHandler()
    
    # Test pwd
    result = handler.execute_command("pwd")
    assert result["success"], "pwd command failed"
    
    # Test echo
    result = handler.execute_command("echo Hello World")
    assert result["success"], "echo command failed"
    assert result["output"] == "Hello World", "echo output incorrect"
    
    # Test ls
    result = handler.execute_command("ls")
    assert result["success"], "ls command failed"
    
    # Test help
    result = handler.execute_command("help")
    assert result["success"], "help command failed"
    assert "Available Commands" in result["output"], "help content incorrect"
    
    print("All basic tests passed!")
    return True


if __name__ == "__main__":
    # If run directly, start the terminal
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_terminal()
    else:
        index()