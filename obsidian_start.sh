#!/bin/bash
# filepath: c:\Users\jmciges\OneDrive - Seresco, S.A\Documentos\Marques-de-Valdecilla\OBSIDIAN\scripts\obsidian_start.sh

# Set UTF-8 environment for Windows
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    # Set UTF-8 locale and encoding
    export LANG=C.UTF-8
    export LC_ALL=C.UTF-8
    export PYTHONIOENCODING=utf-8
    
    # Set console code page to UTF-8 (Windows)
    if command -v chcp >/dev/null 2>&1; then
        chcp 65001 >/dev/null 2>&1
    fi
fi

# Get script directory and paths
SCRIPT_PATH=$(dirname "$(readlink -f "$0")")
OBSIDIAN_VAULT="../.."
SCRIPTS_PATH="${OBSIDIAN_VAULT}/OBSIDIAN/scripts"

# Control file to track last execution date
CONTROL_FILE="${SCRIPT_PATH}/obsidian_start.sh.data"
TODAY=$(date +%Y-%m-%d)

# Function to check if script already ran today
check_already_executed() {
    if [ -f "$CONTROL_FILE" ]; then
        LAST_RUN=$(cat "$CONTROL_FILE" 2>/dev/null)
        if [ "$LAST_RUN" = "$TODAY" ]; then
            return 0  # Already executed today
        fi
    fi
    return 1  # Not executed today
}

# Function to record execution date
record_execution() {
    echo "$TODAY" > "$CONTROL_FILE"
    if [ $? -eq 0 ]; then
        echo "Execution date recorded: $TODAY"
    else
        echo "Warning: Could not record execution date"
    fi
}

# Function to show last execution info
show_execution_info() {
    if [ -f "$CONTROL_FILE" ]; then
        LAST_RUN=$(cat "$CONTROL_FILE" 2>/dev/null)
        if [ -n "$LAST_RUN" ]; then
            echo "Last execution: $LAST_RUN"
        else
            echo "Last execution: Unknown (invalid data file)"
        fi
    else
        echo "Last execution: Never"
    fi
}

# Function to force execution (bypass date check)
force_execution() {
    echo "Force execution requested - bypassing date check"
    run_scripts
}

# Parse command line arguments
FORCE_EXECUTION=false
SHOW_STATUS=false
SHOW_HELP=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--force)
            FORCE_EXECUTION=true
            shift
            ;;
        -s|--status)
            SHOW_STATUS=true
            shift
            ;;
        -h|--help)
            SHOW_HELP=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Show help if requested
if [ "$SHOW_HELP" = true ]; then
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Executes Obsidian daily startup tasks (once per day)"
    echo ""
    echo "Options:"
    echo "  -f, --force     Force execution even if already run today"
    echo "  -s, --status    Show execution status and exit"
    echo "  -v, --verbose   Enable verbose output for Python scripts"
    echo "  -h, --help      Show this help message"
    echo ""
    echo "Tasks performed:"
    echo "  1. Update everyday tasks to 'waiting' state"
    echo "  2. Uncheck all tasks in daily organization note"
    echo ""
    echo "Control file: $CONTROL_FILE"
    exit 0
fi

# Show status if requested
if [ "$SHOW_STATUS" = true ]; then
    echo "Obsidian Start Script Status"
    echo "============================"
    echo "Today: $TODAY"
    show_execution_info
    echo "Control file: $CONTROL_FILE"
    
    if check_already_executed; then
        echo "Status: ✅ Already executed today"
        exit 0
    else
        echo "Status: ⏳ Pending execution for today"
        exit 1
    fi
fi

# Function to run the actual scripts
run_scripts() {
    echo "Starting Obsidian daily tasks..."
    echo "================================="
    
    # Prepare verbose flag if needed
    VERBOSE_FLAG=""
    if [ "$VERBOSE" = true ]; then
        VERBOSE_FLAG="-v"
        echo "Verbose mode enabled"
    fi
    
    echo "1. Updating everyday tasks to 'waiting' state..."
    # Run Python with explicit UTF-8 settings
    PYTHONIOENCODING=utf-8 python -X utf8 "${SCRIPT_PATH}/everyday_tasks.py" -s waiting $VERBOSE_FLAG
    if [ $? -ne 0 ]; then
        echo "Error: Failed to update everyday tasks"
        return 1
    fi
    
    echo "2. Unchecking all tasks in daily organization note..."
    # Run Python with explicit UTF-8 settings
    PYTHONIOENCODING=utf-8 python -X utf8 "${SCRIPT_PATH}/uncheck_all.py" -n "TAREAS/TODOS LOS DÍAS/Organización de la jornada" $VERBOSE_FLAG
    if [ $? -ne 0 ]; then
        echo "Error: Failed to uncheck daily tasks"
        return 1
    fi
    
    echo "================================="
    echo "All tasks completed successfully!"
    record_execution
    return 0
}

# Main execution logic
echo "Obsidian Daily Startup - $TODAY"
echo "==============================="

if [ "$FORCE_EXECUTION" = true ]; then
    force_execution
    exit $?
fi

# Check if already executed today
if check_already_executed; then
    echo "✅ Script already executed today ($TODAY)"
    echo "Last execution: $(cat "$CONTROL_FILE")"
    echo ""
    echo "Use -f or --force to run anyway"
    echo "Use -s or --status to check execution status"
    echo "Use -h or --help for more options"
    exit 0
else
    echo "⏳ Running daily tasks for the first time today..."
    show_execution_info
    echo ""
    run_scripts
    exit $?
fi
