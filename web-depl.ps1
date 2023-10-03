Publish-AzWebApp -ResourceGroupName deploy-first-rg  -Name python-automation -ArchivePath C:\Users\SV528SM\Downloads\
$app = Get-AzWebApp -ResourceGroupName deploy-first-rg -Name python-automation
Publish-AzWebApp -WebApp $app -ArchivePath C:\Users\SV528SM\Downloads\deployment.zip -AsJob


$resourceGroupName='deploy-first-rg'
$appServiceName='python-automation'

az webapp deploy --name $appServiceName --resource-group $resourceGroupName --src-path C:\Users\SV528SM\Downloads\deployment.zip