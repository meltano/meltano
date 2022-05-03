#############################################################################
#
#   This script complete the same steps as make build in linux
#
#############################################################################
$MELTANO_WEBAPP = "src/webapp"
$MELTANO_API = "src/meltano/api"

$TO_CLEAN =  "./build", "./dist", "./${MELTANO_API}/static/js", "./${MELTANO_API}/static/css", "./${MELTANO_WEBAPP}/dist"
$API_TEMPLATES = "./src/meltano/api/templates "
foreach ($item in $TO_CLEAN) {

    if (Test-Path $item)
    {
        Remove-Item -Path $item -Recurse -Force
    }

}

$StartingDirectory = Get-Location

Set-Location src/webapp
yarn
yarn build

Set-Location $StartingDirectory
If (Test-Path $API_TEMPLATES)
{
    Write-Output " The Folder ./src/meltano/api/templates already exists"
}
else
{
    mkdir -p ./src/meltano/api/templates
}
Copy-Item -Force ./src/webapp/dist/index.html ./src/meltano/api/templates/webapp.html
Copy-Item -Force ./src/webapp/dist/index-embed.html ./src/meltano/api/templates/embed.html
Copy-Item -Force -Recurse ./src/webapp/dist/static ./src/meltano/api/
