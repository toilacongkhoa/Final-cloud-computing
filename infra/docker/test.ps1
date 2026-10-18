# Build and check both releases. Run from any directory using PowerShell.
$ErrorActionPreference = 'Stop'

function Invoke-Docker {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$DockerArgs)
    $output = & docker @DockerArgs
    if ($LASTEXITCODE -ne 0) { throw "Docker failed: $($DockerArgs -join ' ')" }
    return $output
}

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Push-Location $repoRoot
try {
    Invoke-Docker version --format '{{.Server.Version}}' | Out-Host
    foreach ($release in @('blue', 'green')) {
        $version = if ($release -eq 'blue') { '1.0.0' } else { '2.0.0' }
        $tag = if ($release -eq 'blue') { 'v1' } else { 'v2' }
        $image = "ecs-bluegreen-demo:$tag"
        Invoke-Docker build --platform linux/amd64 -f infra/docker/Dockerfile --build-arg "APP_RELEASE=$release" -t $image . | Out-Host

        $containerId = $null
        try {
            # Random localhost port avoids interfering with the Node.js preview.
            $containerId = Invoke-Docker run --detach --name "bg-test-$release-$PID" --health-interval=1s --publish '127.0.0.1::8080' $image
            $healthy = $false
            for ($attempt = 0; $attempt -lt 30; $attempt++) {
                $info = @(Invoke-Docker inspect $containerId | ConvertFrom-Json)[0]
                if ($info.State.Health.Status -eq 'healthy') { $healthy = $true; break }
                if (-not $info.State.Running) { throw "$release container stopped unexpectedly" }
                Start-Sleep -Seconds 1
            }
            if (-not $healthy) { throw "$release container did not become healthy" }

            $port = $info.NetworkSettings.Ports.'8080/tcp'[0].HostPort
            $baseUrl = "http://127.0.0.1:$port"
            $health = Invoke-RestMethod "$baseUrl/health" -TimeoutSec 5
            $metadata = Invoke-RestMethod "$baseUrl/version" -TimeoutSec 5
            $page = Invoke-WebRequest $baseUrl -UseBasicParsing -TimeoutSec 5
            if ($health.status -ne 'ok') { throw "$release health endpoint failed" }
            if ($metadata.color -ne $release -or $metadata.version -ne $version) { throw "$release metadata mismatch" }
            if ($page.StatusCode -ne 200 -or -not $page.Content.Contains("v$version")) { throw "$release HTML mismatch" }
            if ($page.Headers['Cache-Control'] -notcontains 'no-store') { throw "$release cache header missing" }
            if ((Invoke-Docker exec $containerId id -u) -eq '0') { throw "$release runs as root" }

            $imageInfo = @(Invoke-Docker image inspect $image | ConvertFrom-Json)[0]
            if ($imageInfo.Os -ne 'linux' -or $imageInfo.Architecture -ne 'amd64') { throw "$release platform mismatch" }
            $files = Invoke-Docker exec $containerId ls -a /app
            if ($files -contains '.git' -or $files -contains 'reports' -or $files -contains 'evidence') {
                throw "$release image contains unrelated repository files"
            }
            Invoke-Docker stop --time 10 $containerId | Out-Null
            $stopped = @(Invoke-Docker inspect $containerId | ConvertFrom-Json)[0]
            if ($stopped.State.ExitCode -ne 0) { throw "$release did not shut down cleanly" }
            Write-Output "PASS $release v$version - image, healthcheck, HTTP, non-root user, clean shutdown"
        } finally {
            # Remove only the test container created by this invocation.
            if ($containerId) { Invoke-Docker rm --force $containerId | Out-Null }
        }
    }
} finally {
    Pop-Location
}
