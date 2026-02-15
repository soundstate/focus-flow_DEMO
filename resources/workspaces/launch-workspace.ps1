# Enhanced Workspace Launcher for js-codebase
param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("app", "func", "sql", "web", "docs", "azure", "root")]
    [string]$Workspace = "root",
    
    [Parameter(Mandatory=$false)]
    [switch]$WithProfile = $false
)

# Set the base directory
$baseDir = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))

# Define workspace configurations (aligned with VS Code profiles)
$workspaces = @{
    "app" = @{
        "file" = "power-apps.code-workspace"
        "profile" = "ui"
        "description" = "Power Apps development and UI work - Uses 'ui' profile"
    }
    "func" = @{
        "file" = "python-functions.code-workspace"
        "profile" = "code"
        "description" = "Python functions and shared packages - Uses 'code' profile"
    }
    "sql" = @{
        "file" = "sql-data.code-workspace"
        "profile" = "data" 
        "description" = "SQL queries, data pipeline, and analytics - Uses 'data' profile"
    }
    "web" = @{
        "file" = "web-development.code-workspace"
        "profile" = "web"
        "description" = "Web applications and frontend code - Uses 'web' profile"
    }
    "docs" = @{
        "file" = "../resources"
        "profile" = "docs"
        "description" = "Documentation and knowledge base - Uses 'docs' profile (opens folder, not workspace)"
        "isFolder" = $true
    }
    "azure" = @{
        "file" = "azure-infrastructure.code-workspace"
        "profile" = "code"
        "description" = "Azure infrastructure and DevOps environment - Uses 'code' profile"
    }
    "root" = @{
        "file" = $null
        "profile" = $null
        "description" = "Opens js-codebase root folder with all files visible"
        "isFolder" = $true
    }
}

function Show-WorkspaceMenu {
    Write-Host "`nAvailable Workspaces:" -ForegroundColor Cyan
    Write-Host "======================" -ForegroundColor Cyan
    
    foreach ($key in $workspaces.Keys | Sort-Object) {
        $info = $workspaces[$key]
        Write-Host "$key" -ForegroundColor Yellow -NoNewline
        Write-Host " - $($info.description)" -ForegroundColor White
        if ($info.profile) {
            Write-Host "    Profile: $($info.profile)" -ForegroundColor Gray
        }
    }
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Cyan
    Write-Host "  -WithProfile : Launch with recommended VS Code profile" -ForegroundColor Gray
    Write-Host ""
}

function Start-Workspace {
    param($WorkspaceName)
    
    if (-not $workspaces.ContainsKey($WorkspaceName)) {
        Write-Host "Unknown workspace: $WorkspaceName" -ForegroundColor Red
        Show-WorkspaceMenu
        return
    }
    
    $config = $workspaces[$WorkspaceName]
    
    Write-Host "Launching $WorkspaceName workspace..." -ForegroundColor Green
    Write-Host "Description: $($config.description)" -ForegroundColor Gray
    
    # Handle special cases for folder-only opens
    if ($config.isFolder) {
        if ($WorkspaceName -eq "root") {
            # Open js-codebase root folder
            $targetPath = $baseDir
            Write-Host "Opening js-codebase root folder" -ForegroundColor Cyan
        } elseif ($WorkspaceName -eq "docs") {
            # Open resources folder
            $targetPath = Join-Path $baseDir "resources"
            Write-Host "Opening resources folder (not as workspace)" -ForegroundColor Cyan
        }
        
        if ($WithProfile -and $config.profile) {
            Write-Host "Using VS Code profile: $($config.profile)" -ForegroundColor Cyan
            Start-Process -FilePath "code" -ArgumentList @("--profile", $config.profile, $targetPath)
        } else {
            code $targetPath
        }
        return
    }
    
    # Handle workspace file opens
    $workspaceFile = Join-Path $PSScriptRoot $config.file
    
    # Determine command based on profile usage
    if ($WithProfile -and $config.profile) {
        Write-Host "Using VS Code profile: $($config.profile)" -ForegroundColor Cyan
    }
    
    # Launch VS Code with the specific workspace
    if (Test-Path $workspaceFile) {
        if ($WithProfile -and $config.profile) {
            Start-Process -FilePath "code" -ArgumentList @("--profile", $config.profile, $workspaceFile)
        } else {
            code $workspaceFile
        }
    } else {
        Write-Host "Workspace file not found: $workspaceFile" -ForegroundColor Red
        Write-Host "Creating basic workspace structure..." -ForegroundColor Yellow
        
        if ($WithProfile -and $config.profile) {
            Start-Process -FilePath "code" -ArgumentList @("--profile", $config.profile, $baseDir)
        } else {
            code $baseDir
        }
    }
}

# Main execution
if ($args.Count -eq 0 -and $Workspace -eq "root") {
    Show-WorkspaceMenu
    $choice = Read-Host "Select workspace (or press Enter for root)"
    if ([string]::IsNullOrEmpty($choice)) {
        $choice = "root"
    }
    Start-Workspace $choice
} else {
    Start-Workspace $Workspace
}
