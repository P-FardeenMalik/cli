"""
Command Handler Module
Handles parsing and execution of terminal commands
"""

import os
import shutil
import subprocess
import platform
import psutil
from pathlib import Path
from typing import List, Dict, Any, Optional
import glob


class CommandHandler:
    """Handles command parsing and execution"""
    
    def __init__(self):
        self.current_directory = os.getcwd()
        self.supported_commands = {
            'ls': self._list_directory,
            'dir': self._list_directory,  # Windows alias
            'pwd': self._print_working_directory,
            'cd': self._change_directory,
            'mkdir': self._make_directory,
            'rmdir': self._remove_directory,
            'rm': self._remove_file,
            'del': self._remove_file,  # Windows alias
            'touch': self._create_file,
            'cat': self._show_file_content,
            'type': self._show_file_content,  # Windows alias
            'clear': self._clear_screen,
            'cls': self._clear_screen,  # Windows alias
            'help': self._show_help,
            'ps': self._show_processes,
            'whoami': self._whoami,
            'date': self._show_date,
            'echo': self._echo,
            'cp': self._copy_file,
            'copy': self._copy_file,  # Windows alias
            'mv': self._move_file,
            'move': self._move_file,  # Windows alias
            'find': self._find_files,
            'grep': self._grep_files,
            'top': self._show_system_info,
            'exit': self._exit,
            'quit': self._exit
        }
    
    def execute_command(self, command_line: str) -> Dict[str, Any]:
        """
        Execute a command and return the result
        
        Args:
            command_line: The full command line string
            
        Returns:
            Dict containing success status, output, and error information
        """
        try:
            if not command_line.strip():
                return {"success": True, "output": "", "error": ""}
            
            parts = self._parse_command(command_line)
            command = parts[0].lower()
            args = parts[1:]
            
            if command in self.supported_commands:
                result = self.supported_commands[command](args)
                return result
            else:
                # Try to execute as system command
                return self._execute_system_command(command_line)
                
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": f"Error executing command: {str(e)}"
            }
    
    def _parse_command(self, command_line: str) -> List[str]:
        """Parse command line into command and arguments"""
        # Simple parsing - can be enhanced for complex cases
        return command_line.strip().split()
    
    def _list_directory(self, args: List[str]) -> Dict[str, Any]:
        """List directory contents (ls/dir command)"""
        try:
            path = args[0] if args else self.current_directory
            path = self._resolve_path(path)
            
            if not os.path.exists(path):
                return {
                    "success": False,
                    "output": "",
                    "error": f"Path '{path}' does not exist"
                }
            
            if not os.path.isdir(path):
                return {
                    "success": False,
                    "output": "",
                    "error": f"'{path}' is not a directory"
                }
            
            items = []
            try:
                entries = os.listdir(path)
                for entry in sorted(entries):
                    full_path = os.path.join(path, entry)
                    if os.path.isdir(full_path):
                        items.append(f"[DIR]  {entry}")
                    else:
                        size = os.path.getsize(full_path)
                        items.append(f"[FILE] {entry} ({size} bytes)")
            except PermissionError:
                return {
                    "success": False,
                    "output": "",
                    "error": f"Permission denied accessing '{path}'"
                }
            
            output = "\n".join(items) if items else "Directory is empty"
            return {"success": True, "output": output, "error": ""}
            
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}
    
    def _print_working_directory(self, args: List[str]) -> Dict[str, Any]:
        """Print current working directory (pwd command)"""
        return {
            "success": True,
            "output": self.current_directory,
            "error": ""
        }
    
    def _change_directory(self, args: List[str]) -> Dict[str, Any]:
        """Change directory (cd command)"""
        try:
            if not args:
                # Go to home directory
                if platform.system() == "Windows":
                    target = os.path.expanduser("~")
                else:
                    target = os.path.expanduser("~")
            else:
                target = args[0]
            
            target = self._resolve_path(target)
            
            if not os.path.exists(target):
                return {
                    "success": False,
                    "output": "",
                    "error": f"Directory '{target}' does not exist"
                }
            
            if not os.path.isdir(target):
                return {
                    "success": False,
                    "output": "",
                    "error": f"'{target}' is not a directory"
                }
            
            self.current_directory = os.path.abspath(target)
            os.chdir(self.current_directory)
            
            return {
                "success": True,
                "output": f"Changed directory to: {self.current_directory}",
                "error": ""
            }
            
        except PermissionError:
            return {
                "success": False,
                "output": "",
                "error": f"Permission denied accessing directory"
            }
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}
    
    def _make_directory(self, args: List[str]) -> Dict[str, Any]:
        """Create directory (mkdir command)"""
        try:
            if not args:
                return {
                    "success": False,
                    "output": "",
                    "error": "mkdir: missing directory name"
                }
            
            for dirname in args:
                path = self._resolve_path(dirname)
                if os.path.exists(path):
                    return {
                        "success": False,
                        "output": "",
                        "error": f"Directory '{path}' already exists"
                    }
                
                os.makedirs(path, exist_ok=False)
            
            return {
                "success": True,
                "output": f"Created directory(s): {', '.join(args)}",
                "error": ""
            }
            
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}
    
    def _remove_directory(self, args: List[str]) -> Dict[str, Any]:
        """Remove directory (rmdir command)"""
        try:
            if not args:
                return {
                    "success": False,
                    "output": "",
                    "error": "rmdir: missing directory name"
                }
            
            for dirname in args:
                path = self._resolve_path(dirname)
                if not os.path.exists(path):
                    return {
                        "success": False,
                        "output": "",
                        "error": f"Directory '{path}' does not exist"
                    }
                
                if not os.path.isdir(path):
                    return {
                        "success": False,
                        "output": "",
                        "error": f"'{path}' is not a directory"
                    }
                
                # Check if directory is empty
                if os.listdir(path):
                    return {
                        "success": False,
                        "output": "",
                        "error": f"Directory '{path}' is not empty. Use 'rm -r' to remove non-empty directories"
                    }
                
                os.rmdir(path)
            
            return {
                "success": True,
                "output": f"Removed directory(s): {', '.join(args)}",
                "error": ""
            }
            
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}
    
    def _remove_file(self, args: List[str]) -> Dict[str, Any]:
        """Remove file or directory (rm/del command)"""
        try:
            if not args:
                return {
                    "success": False,
                    "output": "",
                    "error": "rm: missing file/directory name"
                }
            
            recursive = "-r" in args or "-rf" in args
            force = "-f" in args or "-rf" in args
            
            # Filter out flags
            files = [arg for arg in args if not arg.startswith("-")]
            
            if not files:
                return {
                    "success": False,
                    "output": "",
                    "error": "rm: missing file/directory name"
                }
            
            removed_items = []
            for filename in files:
                path = self._resolve_path(filename)
                
                if not os.path.exists(path) and not force:
                    return {
                        "success": False,
                        "output": "",
                        "error": f"File/directory '{path}' does not exist"
                    }
                
                if os.path.isdir(path):
                    if recursive:
                        shutil.rmtree(path)
                        removed_items.append(f"directory '{filename}' and its contents")
                    else:
                        return {
                            "success": False,
                            "output": "",
                            "error": f"'{path}' is a directory. Use -r flag to remove directories"
                        }
                else:
                    os.remove(path)
                    removed_items.append(f"file '{filename}'")
            
            return {
                "success": True,
                "output": f"Removed: {', '.join(removed_items)}",
                "error": ""
            }
            
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}
    
    def _resolve_path(self, path: str) -> str:
        """Resolve relative path to absolute path"""
        if os.path.isabs(path):
            return path
        return os.path.join(self.current_directory, path)
    
    def _create_file(self, args: List[str]) -> Dict[str, Any]:
        """Create empty file (touch command)"""
        try:
            if not args:
                return {
                    "success": False,
                    "output": "",
                    "error": "touch: missing filename"
                }
            
            for filename in args:
                path = self._resolve_path(filename)
                Path(path).touch()
            
            return {
                "success": True,
                "output": f"Created file(s): {', '.join(args)}",
                "error": ""
            }
            
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}
    
    def _show_file_content(self, args: List[str]) -> Dict[str, Any]:
        """Show file content (cat/type command)"""
        try:
            if not args:
                return {
                    "success": False,
                    "output": "",
                    "error": "cat: missing filename"
                }
            
            filename = args[0]
            path = self._resolve_path(filename)
            
            if not os.path.exists(path):
                return {
                    "success": False,
                    "output": "",
                    "error": f"File '{path}' does not exist"
                }
            
            if os.path.isdir(path):
                return {
                    "success": False,
                    "output": "",
                    "error": f"'{path}' is a directory"
                }
            
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            return {"success": True, "output": content, "error": ""}
            
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}
    
    def _clear_screen(self, args: List[str]) -> Dict[str, Any]:
        """Clear screen (clear/cls command)"""
        return {"success": True, "output": "\033[2J\033[H", "error": ""}
    
    def _show_help(self, args: List[str]) -> Dict[str, Any]:
        """Show help information"""
        help_text = """
Available Commands:
==================
File Operations:
  ls, dir          - List directory contents
  pwd             - Print working directory
  cd <path>       - Change directory
  mkdir <name>    - Create directory
  rmdir <name>    - Remove empty directory
  rm <file>       - Remove file (use -r for directories, -f to force)
  touch <file>    - Create empty file
  cat <file>      - Show file content
  cp <src> <dst>  - Copy file
  mv <src> <dst>  - Move/rename file

System Commands:
  ps              - Show running processes
  top             - Show system information
  whoami          - Show current user
  date            - Show current date/time
  clear, cls      - Clear screen

Utilities:
  echo <text>     - Print text
  find <pattern>  - Find files matching pattern
  grep <pattern>  - Search for text in files
  help            - Show this help
  exit, quit      - Exit terminal

Examples:
  ls -l           - List with details
  cd ..           - Go to parent directory
  mkdir test      - Create 'test' directory
  rm -rf folder   - Remove folder and contents
        """
        return {"success": True, "output": help_text.strip(), "error": ""}
    
    def _show_processes(self, args: List[str]) -> Dict[str, Any]:
        """Show running processes (ps command)"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    processes.append(f"{proc.info['pid']:>6} {proc.info['name']:<30} {proc.info['cpu_percent']:>6.1f}%")
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            header = f"{'PID':>6} {'NAME':<30} {'CPU%':>6}"
            output = header + "\n" + "-" * 50 + "\n" + "\n".join(processes[:20])  # Limit to first 20
            return {"success": True, "output": output, "error": ""}
            
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}
    
    def _whoami(self, args: List[str]) -> Dict[str, Any]:
        """Show current user"""
        try:
            import getpass
            return {"success": True, "output": getpass.getuser(), "error": ""}
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}
    
    def _show_date(self, args: List[str]) -> Dict[str, Any]:
        """Show current date and time"""
        try:
            from datetime import datetime
            return {"success": True, "output": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "error": ""}
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}
    
    def _echo(self, args: List[str]) -> Dict[str, Any]:
        """Echo text (echo command)"""
        return {"success": True, "output": " ".join(args), "error": ""}
    
    def _copy_file(self, args: List[str]) -> Dict[str, Any]:
        """Copy file (cp/copy command)"""
        try:
            if len(args) < 2:
                return {
                    "success": False,
                    "output": "",
                    "error": "cp: missing source or destination"
                }
            
            src = self._resolve_path(args[0])
            dst = self._resolve_path(args[1])
            
            if not os.path.exists(src):
                return {
                    "success": False,
                    "output": "",
                    "error": f"Source '{src}' does not exist"
                }
            
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
            
            return {
                "success": True,
                "output": f"Copied '{args[0]}' to '{args[1]}'",
                "error": ""
            }
            
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}
    
    def _move_file(self, args: List[str]) -> Dict[str, Any]:
        """Move/rename file (mv/move command)"""
        try:
            if len(args) < 2:
                return {
                    "success": False,
                    "output": "",
                    "error": "mv: missing source or destination"
                }
            
            src = self._resolve_path(args[0])
            dst = self._resolve_path(args[1])
            
            if not os.path.exists(src):
                return {
                    "success": False,
                    "output": "",
                    "error": f"Source '{src}' does not exist"
                }
            
            shutil.move(src, dst)
            
            return {
                "success": True,
                "output": f"Moved '{args[0]}' to '{args[1]}'",
                "error": ""
            }
            
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}
    
    def _find_files(self, args: List[str]) -> Dict[str, Any]:
        """Find files matching pattern"""
        try:
            if not args:
                return {
                    "success": False,
                    "output": "",
                    "error": "find: missing pattern"
                }
            
            pattern = args[0]
            search_path = args[1] if len(args) > 1 else self.current_directory
            search_path = self._resolve_path(search_path)
            
            matches = []
            for root, dirs, files in os.walk(search_path):
                for file in files:
                    if pattern.lower() in file.lower():
                        matches.append(os.path.join(root, file))
            
            if not matches:
                return {"success": True, "output": "No files found matching pattern", "error": ""}
            
            return {"success": True, "output": "\n".join(matches), "error": ""}
            
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}
    
    def _grep_files(self, args: List[str]) -> Dict[str, Any]:
        """Search for text in files"""
        try:
            if not args:
                return {
                    "success": False,
                    "output": "",
                    "error": "grep: missing pattern"
                }
            
            pattern = args[0]
            files = args[1:] if len(args) > 1 else ["*"]
            
            matches = []
            for file_pattern in files:
                file_path = self._resolve_path(file_pattern)
                if "*" in file_pattern:
                    file_list = glob.glob(file_path)
                else:
                    file_list = [file_path] if os.path.exists(file_path) else []
                
                for filepath in file_list:
                    if os.path.isfile(filepath):
                        try:
                            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                                for line_num, line in enumerate(f, 1):
                                    if pattern.lower() in line.lower():
                                        matches.append(f"{filepath}:{line_num}:{line.strip()}")
                        except:
                            continue
            
            if not matches:
                return {"success": True, "output": "No matches found", "error": ""}
            
            return {"success": True, "output": "\n".join(matches), "error": ""}
            
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}
    
    def _show_system_info(self, args: List[str]) -> Dict[str, Any]:
        """Show system information (top command)"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            info = f"""System Information:
CPU Usage: {cpu_percent}%
Memory: {memory.percent}% ({memory.used // 1024 // 1024}MB / {memory.total // 1024 // 1024}MB)
Disk Usage: {disk.percent}% ({disk.used // 1024 // 1024}MB / {disk.total // 1024 // 1024}MB)

Top Processes by CPU:"""
            
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append((proc.info['cpu_percent'], proc.info))
                except:
                    continue
            
            processes.sort(reverse=True)
            for cpu, proc_info in processes[:10]:
                info += f"\n{proc_info['pid']:>6} {proc_info['name']:<20} {cpu:>6.1f}% {proc_info['memory_percent']:>6.1f}%"
            
            return {"success": True, "output": info, "error": ""}
            
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}
    
    def _exit(self, args: List[str]) -> Dict[str, Any]:
        """Exit the terminal"""
        return {"success": True, "output": "exit", "error": ""}
    
    def _execute_system_command(self, command_line: str) -> Dict[str, Any]:
        """Execute system command if not in supported commands"""
        try:
            result = subprocess.run(
                command_line,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.current_directory,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.stderr else ""
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": "Command timed out after 30 seconds"
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": f"Command not found: {str(e)}"
            }