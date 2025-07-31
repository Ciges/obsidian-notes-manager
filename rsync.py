import argparse
import os
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
        # Perform synchronization using dirsync
        # sync(sourcedir, targetdir, action, **options)
        sync(
            source,                    # Source directory
            destination,               # Destination directory  
            'sync',                    # Action: 'sync' synchronizes directories
            purge=True,                # Remove files in target that don't exist in source
            verbose=args.verbose,      # Verbose output
            dryrun=args.test,         # Test mode - don't actually make changes
            create=True,              # Create target directory if it doesn't exist
            exclude=[],               # List of patterns to exclude (empty for now)
            only=[],                  # List of patterns to include only (empty = all)
            ignore=[]                 # List of patterns to ignore (empty for now)
        )
        
        if args.test:
            print("\nDry run completed. Run without --test to actually perform synchronization.")
        else:
            print("\nSynchronization completed successfully.")
            
    except ImportError:
        print("Error: dirsync module not found.")
        print("Please install it with: pip install dirsync")
        exit(1)
    except Exception as e:
        print(f"Error during synchronization: {e}")
        exit(1)

if __name__ == "__main__":
    main()