#!/bin/bash

# AI Competitive Intelligence Agent Runner
# This script provides easy ways to run the agent with different configurations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
CONFIG_FILE="config.json"
OUTPUT_FILE="digest.html"
DRY_RUN=false
FORCE=false
VERBOSE=false

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show help
show_help() {
    echo "AI Competitive Intelligence Agent Runner"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -c, --config FILE     Configuration file (default: config.json)"
    echo "  -o, --output FILE     Output file (default: digest.html)"
    echo "  -d, --dry-run         Run without sending notifications"
    echo "  -f, --force           Force run even if recently executed"
    echo "  -v, --verbose         Enable verbose logging"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Basic run"
    echo "  $0 --dry-run --verbose               # Test run with detailed logging"
    echo "  $0 --config custom.json --force      # Force run with custom config"
    echo "  $0 --output weekly_report.html       # Save to custom output file"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

# Check if required files exist
if [[ ! -f "$CONFIG_FILE" ]]; then
    print_error "Configuration file not found: $CONFIG_FILE"
    exit 1
fi

if [[ ! -f "main.py" ]]; then
    print_error "main.py not found. Make sure you're in the correct directory."
    exit 1
fi

# Check if .env file exists
if [[ ! -f ".env" ]]; then
    print_warning ".env file not found. Copy .env.example to .env and add your API keys."
fi

# Check if dependencies are installed
print_status "Checking dependencies..."
if ! python3 -c "import aiohttp, openai, tweepy, jinja2, pydantic" 2>/dev/null; then
    print_warning "Some dependencies may be missing. Run: pip install -r requirements.txt"
fi

# Build command
CMD="python3 main.py --config $CONFIG_FILE --output $OUTPUT_FILE"

if [[ "$DRY_RUN" == true ]]; then
    CMD="$CMD --dry-run"
    print_status "Running in dry-run mode (no notifications will be sent)"
fi

if [[ "$FORCE" == true ]]; then
    CMD="$CMD --force"
    print_status "Force mode enabled (ignoring last run time)"
fi

if [[ "$VERBOSE" == true ]]; then
    CMD="$CMD --verbose"
    print_status "Verbose logging enabled"
fi

# Show configuration
print_status "Configuration:"
echo "  Config file: $CONFIG_FILE"
echo "  Output file: $OUTPUT_FILE"
echo "  Dry run: $DRY_RUN"
echo "  Force: $FORCE"
echo "  Verbose: $VERBOSE"
echo ""

# Run the agent
print_status "Starting AI Competitive Intelligence Agent..."
eval $CMD

# Check if the run was successful
if [[ $? -eq 0 ]]; then
    print_status "Agent completed successfully!"
    
    # Show output file info if it exists
    if [[ -f "$OUTPUT_FILE" ]]; then
        FILE_SIZE=$(ls -lh "$OUTPUT_FILE" | awk '{print $5}')
        print_status "Generated digest: $OUTPUT_FILE ($FILE_SIZE)"
    fi
else
    print_error "Agent failed with exit code $?"
    exit 1
fi