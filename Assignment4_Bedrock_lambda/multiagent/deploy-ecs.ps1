param(
    [Parameter(Mandatory=$true)]
    [string]$AccountId,
    [Parameter(Mandatory=$true)]
    [string]$Region,
    [string]$RepoName = "multiagent-agentcore",
    [string]$ClusterName = "default",
    [string]$ServiceName = "multiagent-service"
)

$ErrorActionPreference = "Stop"
$ImageUri = "$AccountId.dkr.ecr.$Region.amazonaws.com/$RepoName:latest"

Write-Host "Building image..."
docker build -t "$RepoName" .

Write-Host "Creating ECR repository if needed..."
aws ecr describe-repositories --repository-names $RepoName --region $Region 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    aws ecr create-repository --repository-name $RepoName --region $Region | Out-Null
}

Write-Host "Logging into ECR..."
aws ecr get-login-password --region $Region | docker login --username AWS --password-stdin "$AccountId.dkr.ecr.$Region.amazonaws.com"

docker tag "$RepoName:latest" $ImageUri
docker push $ImageUri

Write-Host "Registering ECS task definition..."
(Get-Content ./ecs-task-definition.json -Raw) `
    -replace "<ACCOUNT_ID>", $AccountId `
    -replace "<REGION>", $Region | Out-File ./ecs-task-definition.rendered.json -Encoding utf8

aws ecs register-task-definition --cli-input-json file://$PWD/ecs-task-definition.rendered.json --region $Region | Out-Null

Write-Host "Creating ECS service..."
(Get-Content ./ecs-service.json -Raw) `
    -replace "<CLUSTER_NAME>", $ClusterName `
    -replace "<SERVICE_NAME>", $ServiceName | Out-File ./ecs-service.rendered.json -Encoding utf8

aws ecs create-service --cluster $ClusterName --service-name $ServiceName --cli-input-json file://$PWD/ecs-service.rendered.json --region $Region | Out-Null

Write-Host "Deployment command finished."
Write-Host "Use: aws ecs describe-services --cluster $ClusterName --services $ServiceName --region $Region"
