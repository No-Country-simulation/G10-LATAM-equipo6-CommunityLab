$base   = $PSScriptRoot
$ev     = Join-Path $base "evidencias"
$commit = git rev-parse --short HEAD
$fecha  = Get-Date -Format "yyyy-MM-dd HH:mm K"
$mapa = @{ INF="Infraestructura y setup base"; DOC="Contenedores Docker"; DB="PostgreSQL con pgvector"; N8N="Orquestador n8n"; PY="Sistema dual con pipelines Python"; IA="APIs de IA, prompts e imágenes"; LOG="Lógica condicional"; UI="Panel Streamlit"; OBJ="JSON en OCI Object Storage"; E2E="Flujo extremo a extremo" }
$casos = @(Import-Csv (Join-Path $base "estados.csv") -Delimiter ';' -Encoding UTF8)
$hall  = @(Import-Csv (Join-Path $base "hallazgos.csv") -Delimiter ';' -Encoding UTF8)
$todos = @(Get-ChildItem $ev -Recurse -File -ErrorAction SilentlyContinue)

$filas = foreach ($c in $casos) {
  $arch = @($todos | Where-Object { $_.BaseName -like "$($c.ID)*" })
  $ult = "-"; $nom = "-"
  if ($arch.Count) {
    $ult = ($arch | Sort-Object LastWriteTime -Descending | Select-Object -First 1).LastWriteTime.ToString("yyyy-MM-dd HH:mm")
    $nom = ($arch | ForEach-Object { $_.Name }) -join ", "
  }
  [pscustomobject]@{ ID=$c.ID; Backlog=$mapa[($c.ID -split '-')[0]]; Prueba=$c.Prueba; Estado=$c.Estado; Evidencias=$nom; Ultima=$ult; Nota=$c.Nota }
}

$m = New-Object System.Collections.ArrayList
[void]$m.Add("# Matriz de trazabilidad - CommunityLab (pruebas funcionales QA)")
[void]$m.Add("")
[void]$m.Add("- Fecha de generación: $fecha")
[void]$m.Add("- Commit probado: $commit")
[void]$m.Add("- Entorno: local (Windows y Docker Desktop), salvo INF-06 contra el servidor del equipo")
[void]$m.Add("")
[void]$m.Add("## Resumen por estado")
[void]$m.Add("| Estado | Casos |")
[void]$m.Add("|---|---|")
foreach ($g in ($filas | Group-Object Estado | Sort-Object Count -Descending)) { [void]$m.Add("| $($g.Name) | $($g.Count) |") }
[void]$m.Add("")
[void]$m.Add("## Matriz: backlog, caso, evidencia")
[void]$m.Add("| ID | Historia del backlog | Prueba | Estado | Evidencias | Última evidencia | Nota |")
[void]$m.Add("|---|---|---|---|---|---|---|")
foreach ($r in $filas) { [void]$m.Add("| $($r.ID) | $($r.Backlog) | $($r.Prueba) | $($r.Estado) | $($r.Evidencias) | $($r.Ultima) | $($r.Nota) |") }
[void]$m.Add("")
[void]$m.Add("## Hallazgos vinculados a casos")
[void]$m.Add("| ID | Severidad | Caso | Detalle | Seguimiento |")
[void]$m.Add("|---|---|---|---|---|")
foreach ($h in $hall) { [void]$m.Add("| $($h.ID) | $($h.Severidad) | $($h.Caso) | $($h.Detalle) | $($h.Seguimiento) |") }
[void]$m.Add("")
[void]$m.Add("## Integridad de evidencias (SHA-256, primeros 12 caracteres)")
[void]$m.Add("| Archivo | Hash | Fecha | KB |")
[void]$m.Add("|---|---|---|---|")
foreach ($a in $todos) {
  $h12 = (Get-FileHash $a.FullName -Algorithm SHA256).Hash.Substring(0,12)
  $rel = $a.FullName.Substring($ev.Length + 1)
  [void]$m.Add("| $rel | $h12 | $($a.LastWriteTime.ToString('yyyy-MM-dd HH:mm')) | $([math]::Round($a.Length/1KB,1)) |")
}
$sin = @($todos | Where-Object { $n = $_.BaseName; -not ($casos | Where-Object { $n -like "$($_.ID)*" }) })
if ($sin.Count) { [void]$m.Add(""); [void]$m.Add("Archivos de apoyo sin caso propio (entradas, salidas y logs): $($sin.Count)") }

$m | Out-File (Join-Path $base "trazabilidad.md") -Encoding utf8
$filas | Export-Csv (Join-Path $base "trazabilidad.csv") -NoTypeInformation -Encoding UTF8
$filas | Group-Object Estado | Select-Object Name, Count | Format-Table -AutoSize
"Generado: $(Join-Path $base 'trazabilidad.md')"
