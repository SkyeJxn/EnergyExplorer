# EnergyExplorer

## Problemstellung

Es fehlen öffentliche Werkzeuge, die interaktiv und intuitiv verdeutlichen, wie erneuerbare Energien die Stromproduktion beeinflussen. Dieses Projekt soll eine Plattform bereitstellen, die es Nutzer:innen ermöglicht, diese Zusammenhänge selbstständig zu erkunden und zu verstehen.

## Ziele

Ziel des Projekts ist es, die Daten der Energy-Charts API abzurufen, aufzubereiten und anschaulich zu visualisieren. Dabei sollen Nutzer:innen flexibel den Zeitraum und die dargestellten Datenpunkte auswählen können. Besonderer Fokus liegt darauf, die Daten so aufzubereiten, dass sie es den Nutzer:innen leicht machen, Zusammenhänge zu entdecken und zu verstehen.

## Vorgehensweise

Nachdem die Daten von der API abgerufen sind, werden die Daten zusammengefasst und vereinheitlicht in einer Datenbank gespeichert. Das Visualisierungs-Tool greift auf diese Datenbank zu, speichert sich den aktuellen Stand ab und bereitet die Daten grafisch auf. Die Nutzer:in kann auswählen, welche Daten als Ausgangspunkte visualisiert werden.

## Erwartete Ergebnisse

Das Projekt liefert eine aufbereitete und konsistente Datenbasis aus der Energy-Charts API, die Informationen über Stromproduktion, Anteil erneuerbarer Energien und Strompreise umfasst. Die Daten werden so zusammengeführt, dass unterschiedliche Zeiträume und Datenpunkte vergleichbar sind. Sie werden in interaktiven Diagrammen (Einzellinie, Mehrlinien, Balkendiagramme) dargestellt, die es den Nutzer:innen ermöglichen, Zusammenhänge schnell zu erkennen.

## Funktionsdiagramm

![Workflow](Workflow.png)