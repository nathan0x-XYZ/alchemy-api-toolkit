# PowerShell script to update commit messages for each file

# Ensure we're in the correct directory
Set-Location -Path "c:\Users\ewuxnat\code\Alchemy"

# Define descriptive commit messages for each file
$files = @(
    @{
        "file" = "validate_api_key.py";
        "message" = "Add API key validation utility with regex pattern matching";
    },
    @{
        "file" = "Validate API Key.py";
        "message" = "Add comprehensive API key validator with logging capabilities";
    },
    @{
        "file" = "alchemy_api_debug.py";
        "message" = "Implement Alchemy API debugging tools with error handling and retry logic";
    },
    @{
        "file" = "basic stepup code.py";
        "message" = "Create initial setup code for Alchemy API integration with Web3.py";
    },
    @{
        "file" = "fetch_nft_examples.py";
        "message" = "Consolidate NFT functionality into a single comprehensive file";
    },
    @{
        "file" = "rate_limiter.py";
        "message" = "Add rate limiting implementation to prevent API throttling";
    },
    @{
        "file" = "retry_with_backoff.py";
        "message" = "Implement exponential backoff retry mechanism for API resilience";
    },
    @{
        "file" = "test_network_connection.py";
        "message" = "Add network connectivity test utility for Alchemy API endpoints";
    },
    @{
        "file" = "webhook_validator.py";
        "message" = "Implement webhook signature validation for secure callbacks";
    },
    @{
        "file" = "alchemy-debug-guide.md";
        "message" = "Add comprehensive debugging guide for Alchemy API (Chinese version)";
    },
    @{
        "file" = "alchemy-debug-guide-en.md";
        "message" = "Add comprehensive debugging guide for Alchemy API (English version)";
    }
)

# Create a new commit for each file with a descriptive message
foreach ($item in $files) {
    $file = $item.file
    $message = $item.message
    
    # Check if file exists
    if (Test-Path $file) {
        Write-Host "Creating new commit for $file with descriptive message..."
        
        # Add the file and create a new commit
        git add $file
        git commit -m "$message"
        
        Write-Host "Created new commit for $file"
    } else {
        Write-Host "File $file not found, skipping..."
    }
}

Write-Host "All commits created with descriptive messages. Please review with 'git log'."
