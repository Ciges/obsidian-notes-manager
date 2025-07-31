import argparse
import os
from typing import Set, Any, cast
from dirsync import sync # type: ignore

def main():
    # Configure command line arguments
    parser = argparse.ArgumentParser(
        description='Python directory synchronization using dirsync',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python rsync.py -s /source/folder -d /dest/folder
  python rsync.py -s C:\\source -d C:\\dest --test --verbose
  python rsync.py --source ./src --destination ./backup -t -v

Note: You need to install dirsync first:
  pip install dirsync
        """
    )
    
    parser.add_argument('-s', '--source',
                        type=str,
                        required=True,
                        help='Source directory to sync from')
    
    parser.add_argument('-d', '--destination',
                        type=str,
                        required=True,
                        help='Destination directory to sync to')
    
    parser.add_argument('-t', '--test',
                        action='store_true',
                        help='Test mode - show what would be done without making changes')
    
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='Verbose output - show detailed information')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Validate source directory
    if not os.path.exists(args.source):
        print(f"Error: Source directory '{args.source}' does not exist.")
        exit(1)
    
    if not os.path.isdir(args.source):
        print(f"Error: Source '{args.source}' is not a directory.")
        exit(1)
    
    # Normalize paths
    source = os.path.abspath(args.source)
    destination = os.path.abspath(args.destination)
    
    if args.verbose:
        print(f"Source: {source}")
        print(f"Destination: {destination}")
        print(f"Test mode: {'ON' if args.test else 'OFF'}")
        print("-" * 50)
    
    try:
        if args.test:
            # Test mode: Use dirsync's --diff option to show differences
            print("Running in test mode - analyzing differences...\n")
            
            # Use 'diff' action to show what would be different
            sync(
                source,                    # Source directory
                destination,               # Destination directory  
                'diff',                    # Action: 'diff' shows differences only
                verbose=args.verbose,      # Verbose output
                create=True,              # Allow checking against non-existent target
            )
            
            print("\nDifferences analysis completed.")
            print("Use --verbose (-v) to see detailed differences.")
            # Uncomment the following line if you want to handle cases where no differences are found
            # print("No differences found - directories are already synchronized.")
            
            print("\nTo actually perform the synchronization, run without --test flag")
            
        else:
            # Normal synchronization mode
            try:
                result: Set[Any] = cast(Set[Any], sync(
                    source,                    # Source directory
                    destination,               # Destination directory  
                    'sync',                    # Action: 'sync' synchronizes directories
                    verbose=args.verbose,      # Verbose output
                    purge=True,                # Remove files in target that don't exist in source (--purge)
                    create=True,              # Create target directory if it doesn't exist (--create)
                    force=True,               # Force file permissions changes (--force)
                    twoway=False,             # Only sync from source to target (not bidirectional)
                    exclude=[],               # Regex patterns to exclude (empty for now)
                    only=[],                  # Regex patterns to include only (empty = all)
                    ignore=[]                 # Regex patterns to ignore (empty for now)
                ))
                
                if result:
                    print(f"\nSynchronization completed successfully. {len(result)} files processed.")
                else:
                    print("\nSynchronization completed successfully.")
                    
            except PermissionError as e:
                print(f"Warning: Permission issue encountered: {e}")
                print("Some files may not have been synchronized due to permission restrictions.")
                print("Synchronization completed with warnings.")
            except OSError as e:
                if "permission" in str(e).lower() or "access" in str(e).lower():
                    print(f"Warning: File access issue: {e}")
                    print("Some files may not have been synchronized due to access restrictions.")
                    print("Synchronization completed with warnings.")
                else:
                    # Re-raise if it's not a permission-related OSError
                    raise
            
    except ImportError:
        print("Error: dirsync module not found.")
        print("Please install it with: pip install dirsync")
        exit(1)
    except Exception as e:
        print(f"Error during synchronization: {e}")
        exit(1)

if __name__ == "__main__":
    main()