#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from configparser import ConfigParser
try:
    from git import Repo, InvalidGitRepositoryError
    git_available = True
except ImportError:
    git_available = False


class Vault:
    """Class to represent an Obsidian Vault with its configuration and git information"""
    
    def __init__(self, config_path: str = 'onm/config.ini'):
        """Initialize Vault with configuration file path"""
        self.config = ConfigParser()
        self.config.read(config_path)
        
        # Load vault properties from config
        self.name = self.config.get('Obsidian', 'vault_name')
        self.path = os.path.abspath(self.config.get('Obsidian', 'vault_path'))
        self.description = self.config.get('Obsidian', 'vault_description')
        
        # Get git information
        self.git_remote = self._get_git_remote()
    
    def _get_git_remote(self):
        """Get git remote origin URL if available"""
        if not git_available:
            return "GitPython not available"
        
        try:
            repo = Repo(self.path) # pyright: ignore[reportPossiblyUnboundVariable]
            if repo.remotes:
                return repo.remotes.origin.url
            else:
                return "No remotes configured"
        except InvalidGitRepositoryError: # pyright: ignore[reportPossiblyUnboundVariable]
            return "Not a git repository"
        except Exception as e:
            return f"Error accessing repository ({e})"
    
    def __str__(self):
        """String representation of the vault information"""
        return (f"\nObsidian Vault information:\n"
                f"- Name: {self.name}\n"
                f"- Path: {self.path}\n"
                f"- Description: {self.description}\n"
                f"- Git Remote Origin: {self.git_remote}")
    
    def __repr__(self):
        """Developer representation of the vault"""
        return f"Vault(name='{self.name}', path='{self.path}')"