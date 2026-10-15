# Read-only process and port sweep for the streaks fidelity gate (task 28). Prints, writes nothing.
# Covers name, age (creation time), command line and listening ports, shells included.
$names = '^(python|pythonw|node|playwright|chrome|chromium|headless_shell|bash|sh|cmd|timeout|powershell|pwsh|conhost)\.exe$|^(WebKit|Playwright|pw_run|MiniBrowser)'
$cmdPattern = 'streaks|http\.server|pytest|playwright|scratchpad|fidelity|harness|examples.split|ms-playwright'
$now = Get-Date
Write-Output ("sweep at " + $now.ToString('yyyy-MM-dd HH:mm:ss'))
$procs = Get-CimInstance Win32_Process | Where-Object {
  ($_.Name -match $names) -or ($_.CommandLine -and $_.CommandLine -match $cmdPattern)
} | Where-Object { $_.Name -ne 'msedgewebview2.exe' }
foreach ($p in ($procs | Sort-Object CreationDate)) {
  $cl = if ($p.CommandLine) { $p.CommandLine } else { '' }
  if ($cl.Length -gt 220) { $cl = $cl.Substring(0, 220) + '...' }
  $created = if ($p.CreationDate) { $p.CreationDate.ToString('HH:mm:ss') } else { '?' }
  Write-Output ("PID {0} PPID {1} {2} created {3} | {4}" -f $p.ProcessId, $p.ParentProcessId, $p.Name, $created, $cl)
}
Write-Output "listening on 127.0.0.1 or 0.0.0.0:"
Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.LocalAddress -in @('127.0.0.1', '0.0.0.0', '::', '::1') } | Sort-Object LocalPort | ForEach-Object {
  $owner = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
  Write-Output ("  {0}:{1} pid {2} {3}" -f $_.LocalAddress, $_.LocalPort, $_.OwningProcess, $(if ($owner) { $owner.ProcessName } else { '?' }))
}
