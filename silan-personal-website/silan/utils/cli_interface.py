"""CLI interface utilities for user interaction"""

from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm

from .logger import ModernLogger


class CLIInterface:
    """Interface for CLI interactions and user input"""
    
    def __init__(self, logger: ModernLogger):
        self.logger = logger
        self.console = Console()
    
    def display_info_panel(self, title: str, info: Dict[str, Any]) -> None:
        """Display information in a panel"""
        content = ""
        for key, value in info.items():
            content += f"[bold]{key}:[/bold] {value}\n"
        
        panel = Panel(content.strip(), title=title, title_align="left")
        self.console.print(panel)
    
    def display_success_panel(self, title: str, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Display success message in a panel"""
        content = f"[green]{message}[/green]\n"
        
        if details:
            content += "\n"
            for key, value in details.items():
                content += f"[bold]{key}:[/bold] {value}\n"
        
        panel = Panel(content.strip(), title=f"✅ {title}", title_align="left", border_style="green")
        self.console.print(panel)
    
    def display_error_panel(self, title: str, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Display error message in a panel"""
        content = f"[red]{message}[/red]\n"
        
        if details:
            content += "\n"
            for key, value in details.items():
                content += f"[bold]{key}:[/bold] {value}\n"
        
        panel = Panel(content.strip(), title=f"❌ {title}", title_align="left", border_style="red")
        self.console.print(panel)
    
    def display_table(self, title: str, headers: List[str], rows: List[List[str]]) -> None:
        """Display data in a table"""
        table = Table(title=title, show_header=True, header_style="bold magenta")
        
        for header in headers:
            table.add_column(header)
        
        for row in rows:
            table.add_row(*row)
        
        self.console.print(table)
    
    def confirm(self, message: str, default: bool = True) -> bool:
        """Get user confirmation"""
        return Confirm.ask(message, default=default)
    
    def prompt(self, message: str, default: Optional[str] = None) -> str:
        """Get user input"""
        result = Prompt.ask(message, default=default)
        return result or ""
    
    def prompt_choice(self, message: str, choices: List[str], default: Optional[str] = None) -> str:
        """Get user choice from options"""
        result = Prompt.ask(message, choices=choices, default=default)
        return result or ""
    
    def prompt_password(self, message: str) -> str:
        """Get password input"""
        return Prompt.ask(message, password=True)
    
    def interactive_form(self, fields: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Interactive form for multiple fields"""
        results = {}
        
        for field in fields:
            name = field['name']
            label = field['label']
            field_type = field.get('type', 'string')
            default = field.get('default')
            required = field.get('required', False)
            
            if field_type == 'password':
                value = self.prompt_password(f"{label}: ")
            elif field_type == 'integer':
                while True:
                    try:
                        value_str = self.prompt(f"{label}: ", str(default) if default else None)
                        if not value_str and not required:
                            value = default
                            break
                        value = int(value_str)
                        
                        # Check min/max if specified
                        if 'min' in field and value < field['min']:
                            self.logger.error(f"Value must be at least {field['min']}")
                            continue
                        if 'max' in field and value > field['max']:
                            self.logger.error(f"Value must be at most {field['max']}")
                            continue
                        break
                    except ValueError:
                        self.logger.error("Please enter a valid number")
            else:
                value = self.prompt(f"{label}: ", default)
                if not value and required:
                    self.logger.error(f"{label} is required")
                    continue
            
            results[name] = value
        
        return results