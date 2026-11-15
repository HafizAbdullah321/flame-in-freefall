$pptxPath = (Resolve-Path "Flame in Freefall - NASA Space Apps.pptx").Path
$pdfPath = (Join-Path (Get-Location) "Flame in Freefall - NASA Space Apps.pdf")

Write-Host "Opening PowerPoint to convert $pptxPath to $pdfPath..."
$pptApp = New-Object -ComObject PowerPoint.Application

try {
    $presentation = $pptApp.Presentations.Open($pptxPath, [Microsoft.Office.Core.MsoTriState]::msoTrue, [Microsoft.Office.Core.MsoTriState]::msoFalse, [Microsoft.Office.Core.MsoTriState]::msoFalse)
    # ppSaveAsPDF = 32
    $presentation.SaveAs($pdfPath, 32)
    $presentation.Close()
    Write-Host "Successfully saved $pdfPath"
} finally {
    $pptApp.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($pptApp) | Out-Null
}

