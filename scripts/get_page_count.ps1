$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open('E:\NEXCIV\NexCiv_Major_Project_Report.docx')
$pages = $doc.ComputeStatistics(2)
$words = $doc.ComputeStatistics(0)
$doc.Close([ref]0)
$word.Quit()
Write-Output "PAGE_COUNT: $pages"
Write-Output "WORD_COUNT: $words"
