# Comparative Process Mining
## Wichtiges:
* Bitte darauf achten, dass die Pakete, die benutzt werden, in die `dependencies.txt` überführt werden, ansonsten funktioniert der Docker-Container nicht einwandfrei.
* Die `.gitignore` kann nach eigenem Belieben erweitert werden.
---
## Docker
Damit ihr bei euch auch die App innerhalb des Docker-Containers testen könnt, hier eine kurze Anleitung:

**Benötigt**:
* [docker-desktop](https://www.docker.com/products/docker-desktop) installieren, ebenso verfügbar durch `choco install docker-desktop`
* Terminal oder ein CLI-integriertes IDE (meine Empfehlung ist VSCode).

**Vorgehen**:
* Zu allererst müsst ihr das Image builden. Dafür in den Ordner mit der `Dockerfile` navigieren und folgenden Terminalbefehl eingeben:
    > `docker build . -t <name>`

* Nachdem das Image jetzt gebuildet ist, dürftet ihr mittels `docker images` den oben eingegebenen Namen sehen. Sollte das nicht der Fall sein, ist was schiefgelaufen.

* Nun können wir den Container starten. Den Hauptteil der Konfiguration habe ich bereits in die `Dockerfile` gepackt, also bleibt nur noch:
    > `docker run -d -p 8000:8000 <name>`

* Dieser Befehl sollte nach kurzer Zeit eine lange Zeichenkette ausspucken. Dies ist die ID des Containers (ihr könnt alle laufenden Container auch durch `docker ps` anzeigen lassen, dort steht ebenfalls die ID).

* Mittels `docker exec -it <ID> /bin/bash` (*Notiz*:  Ihr müsst nicht die vollständige ID abtippen, die ersten paar Zeichen genügen, andernfalls meckert Docker) könnt ihr innerhalb des Containers Befehle ausführen. Dies ist aktuell noch möglich, da ich den Container z.Zt. im Idlemodus für die Einrichtung stehen habe (später wird das zwar immernoch gehen, da wir dann allerdings mit dem auf Docker laufenden Webserver interagieren ist das eher unwichtig).

* Nachtrag: Zum Coden empfehle ich innerhalb des Dockercontainers zu arbeiten. Der Server aktualisiert bei jeder Speicherung und kann somit in (fast) realtime geändert werden. Um einen Volumeshare zu erstellen, einfach beim `docker run ...` ein `-v {hier der absolute Pfad zum Projekt}/:/home/app/webapp` ergänzen. So könnt ihr dann mit `docker exec ...` oder in der Docker CLI selbst den Server starten und dann sofort Änderungen sehen.

### **Integration in die Codeumgebung**
Da das viele und wiederholte Ausführen des Commands auf Dauer nervig wird, kann man sich in VSCode Tasks definieren (falls das noch nicht bekannt sein sollte).

**Anleitung**:
1. Ordner innerhalb von VSCode öffnen (über Terminal sehr komfortabel mit `code .`)
2. `Strg` + `Shift` + `P`
3. `Tasks: Run Task` auswählen
4. `Configure a Task` auswählen, dann bei der Templateabfrage `Other` wählen
5. Tada, ihr könnt nun eure Tasks definieren 


Tasks für Build und Run sehen bspw. so aus:

```
{
    // See https://go.microsoft.com/fwlink/?LinkId=733558
    // for the documentation about the tasks.json format
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Docker Build",
            "type": "shell",
            "command": "docker build . -t cpm",
            "problemMatcher": []
        },
        {
            "label": "Docker Run",
            "type": "shell",
            "command": "docker run -d -p 8000:8000 cpm",
            "problemMatcher": []
        }
    ]
}
```
Mit Volumeshare sähe die Task dann so aus:
```
{
    // See https://go.microsoft.com/fwlink/?LinkId=733558
    // for the documentation about the tasks.json format
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Docker Run",
            "type": "shell",
            "command": "docker run -v C:/Users/geiss/Desktop/WS21-22/SPP/process-discovery/:/home/app/webapp -p 8000:8000 -d cpm ",
            "problemMatcher": []
        }
    ]
}
```


## Projektstruktur
```
+---bootstrapdjango     (Settings für django)
+---home                (Home-Page)
+---manage_logs         (Seite für Verwaltung der Logs)
+---media
|  +---event_logs       (Hier werden die Logs gespeichert)
+---static              
|  +---css              (Bootstrap)
|  +---img              (Für statische Bilder)
|  +---js               (Bootstrap)
+---templates           (html-templates)
```
