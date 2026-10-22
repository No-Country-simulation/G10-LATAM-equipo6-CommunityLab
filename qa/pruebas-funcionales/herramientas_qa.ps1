function Set-Estado($id, $estado, $nota) {
  $p = "qa\pruebas-funcionales\estados.csv"
  $rows = @(Import-Csv $p -Delimiter ';' -Encoding UTF8)
  $r = $rows | Where-Object ID -eq $id
  if (-not $r) { "No existe $id"; return }
  $r.Estado = $estado; $r.Nota = $nota
  $rows | Export-Csv $p -Delimiter ';' -NoTypeInformation -Encoding UTF8
  "$id -> $estado"
}
function Set-Hallazgo($id, $detalle, $seg) {
  $p = "qa\pruebas-funcionales\hallazgos.csv"
  $rows = @(Import-Csv $p -Delimiter ';' -Encoding UTF8)
  $r = $rows | Where-Object ID -eq $id
  if (-not $r) { "No existe $id"; return }
  if ($detalle) { $r.Detalle = $detalle }
  if ($seg) { $r.Seguimiento = $seg }
  $rows | Export-Csv $p -Delimiter ';' -NoTypeInformation -Encoding UTF8
  "$id actualizado"
}
function Add-Hallazgo($id, $sev, $caso, $detalle, $seg) {
  $p = "qa\pruebas-funcionales\hallazgos.csv"
  $rows = @(Import-Csv $p -Delimiter ';' -Encoding UTF8)
  if ($rows.ID -contains $id) { "$id ya existe, no se modifica"; return }
  $rows += [pscustomobject]@{ ID = $id; Severidad = $sev; Caso = $caso; Detalle = $detalle; Seguimiento = $seg }
  $rows | Export-Csv $p -Delimiter ';' -NoTypeInformation -Encoding UTF8
  "$id agregado"
}
function Reg-UI($id, $estado, $obs) {
  $d = (Resolve-Path "qa\pruebas-funcionales\evidencias").Path; $f = "$d\$id.txt"
  if (-not (Test-Path $f)) { "$id - Prueba manual en el panel Streamlit (entorno local)" | Out-File $f -Encoding utf8 }
  "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss K')] commit $(git rev-parse --short HEAD) | Resultado: $estado | $obs" | Out-File $f -Append -Encoding utf8
}
