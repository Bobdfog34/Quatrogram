$venv = 'C:\Users\alex_\AppData\Local\Temp\opencode\qgbot-venv'
$bot  = 'C:\Users\alex_\AppData\Local\Temp\opencode\quatrogram\bot\bot.py'

$env:BOT_TOKEN        = [Environment]::GetEnvironmentVariable('BOT_TOKEN','User')
$env:DATABASE_URL     = [Environment]::GetEnvironmentVariable('DATABASE_URL','User')
$env:ADMIN_IDS        = [Environment]::GetEnvironmentVariable('ADMIN_IDS','User')
$env:ADMIN_USERNAMES  = [Environment]::GetEnvironmentVariable('ADMIN_USERNAMES','User')
$env:ADMIN_CHAT_IDS   = [Environment]::GetEnvironmentVariable('ADMIN_CHAT_IDS','User')
$env:NUMBER_PREFIX    = '+7000'

Write-Host 'Quatrogram bot started.'
& "$venv\Scripts\python.exe" $bot
