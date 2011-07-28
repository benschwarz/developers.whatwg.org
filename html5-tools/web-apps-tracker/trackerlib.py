# Make sure we have a module for doing shell scripts and one for simple web forms.
import os
import cgi
import re

# This function can probably be beautified
def parseRawLog(svnLog):
    """Parses a raw svn log.

    Returns a list with entries, each list item containing a dictionary with
    two keys; info (string) and changes (list)
    """
    logList = cgi.escape(svnLog.read()).splitlines()
    entries = []
    current = 0
    separator = "-" * 72
    for i, line in enumerate(logList):
        if line != separator:
            # After the separator comes the log info
            if logList[i - 1] == separator:
                entries.append({"info": line, "changes": []})
            elif line:
                entries[current]["changes"].append(line)

            # If next list item is a separator, there are no more changes
            if logList[i + 1] == separator:
                current += 1
    return entries


def parseLogLine(logInfo):
    mapping = {
        "e": "editorial",
        "a": "authors",
        "c": "conformance-checkers",
        "g": "gecko",
        "i": "internet-explorer",
        "o": "opera",
        "w": "webkit",
        "r": "google-gears",
        "t": "tools",
        "0": "draft-content",
        "1": "stable-draft",
        "2": "implemented",
        "3": "stable"
        }
    changes = []
    classes = []
    bug = None
    for line in logInfo:
        if line.startswith("Fixing http://www.w3.org/Bugs/Public/show_bug.cgi?id="):
            bug = line[53:]
        elif line.startswith("["):
            for c in line:
                if c in mapping:
                    classes.append(mapping[c])
                if c == "]":
                    if (not classes) or (len(classes) == 1 and classes[0] == "editorial"):
                        classes.append("none")
                if c == ")":
                    break
            changes.append(line.split(") ", 1)[-1])
        else:
            changes.append(line)
    return {"changes": changes, "classes": classes, "bug": bug}


def getRevisionData(revision):
    revInfo = revision["info"] # This is the info line for a revision
    revChanges = parseLogLine(revision["changes"]) # Changes for the revision

    iconClasses = ["authors", "conformance-checkers", "gecko", "internet-explorer", "opera", "webkit", "google-gears", "tools"]
    titleClasses = ["editorial", "draft-content", "stable-draft", "implemented", "stable"]

    # Get the revision number
    number = getNumber(revInfo, 1)
    # Get the revision date and chop off the seconds and time zone
    date = re.split(" \(", re.split(" \| ", revInfo)[2])[0][:16]

    # Get stuff from the changes line(s)
    # TODO: fix the classAttr and titleAttr to only return if non-empty
    classAttr = " class=\"%s\"" % " ".join(revChanges["classes"])
    titleAttr = " title=\"%s\"" % ", ".join([title.replace("-", " ").title() for title in revChanges["classes"] if title in titleClasses])
    icons = "".join([("<img src=\"icons/%s\" alt=\"[%s]\"> ") % (class_, class_.replace("-", " ").title()) for class_ in revChanges["classes"] if class_ in iconClasses])
    changes = "<br>".join(revChanges["changes"])

    # TODO: Implement the source stuff to work with links
    link = "?from=%s&amp;to=%s" % (str(toInt(number) - 1), number)

    bug = ""
    if revChanges["bug"]:
        bug = "<a href=\"http://www.w3.org/Bugs/Public/show_bug.cgi?id=" + revChanges["bug"] + "\">" + revChanges["bug"] + "</a>"

    return {
        "number": number,
        "link": link,
        "classAttr": classAttr,
        "titleAttr": titleAttr,
        "icons": icons,
        "changes": changes,
        "date": date,
        "bug" : bug
        }


def formatLog(logList):
    output = ""
    if logList:
        output += "<table id=\"log\">\n   <tr>" \
            "<th>SVN</th>" \
            "<th>Bug</th>" \
            "<th>Comment</th>" \
            "<th>Time (UTC)</th></tr>"
        for revision in logList:
            revData = getRevisionData(revision)
            output += "\n   <tr%(classAttr)s%(titleAttr)s>" \
                "<td>%(number)s</td>" \
                "<td>%(bug)s</td>" \
                "<td><a href=\"%(link)s\">%(icons)s%(changes)s</a></td>" \
                "<td>%(date)s</td></tr>" % revData
        output += "\n  </table>"
    return output


def formatDiff(diff):
    """Takes a svn diff and marks it up with elements for styling purposes

    Returns a formatted diff
    """
    diff = diff.splitlines()
    diffList = []

    def formatLine(line):
        format = "<samp class=\"%s\">%s</samp>"
        formattingTypes = {"+": "addition", "-": "deletion", "@": "line-info"}
        diffType = line[0]
        if diffType in formattingTypes.keys():
            diffList.append(format % (formattingTypes[diffType], line))
        else:
            diffList.append("<samp>%s</samp>" % line)

    for line in diff:
        formatLine(line)

    return "\n".join(diffList)

def getDiffCommand(source, revFrom, revTo):
    command = "svn diff -r %s%s %s"
    if revTo:
        return command % (revFrom, ":%s" % revTo, source)
    else:
        return command % (revFrom, "", source)

def getLogCommand(source, revFrom, revTo):
    revFrom += 1
    return "svn log %s -r %s:%s" % (source, revFrom, revTo)

def getDiff(source, revFrom, revTo, identifier):
    if identifier == "":
        identifier = "html5"
    filename = identifier + "-" + str(revFrom) + "-" + str(revTo)

    # Specialcase revTo 0 so future revFrom=c&revTo=0 still show the latest
    if revTo != 0 and os.path.exists("diffs/" + filename):
        return open("diffs/" + filename, "r").read()
    else:
        diff = cgi.escape(os.popen(getDiffCommand(source, revFrom, revTo)).read())
        if not diff:
            return diff

        # Specialcase revTo 0 so future revFrom=c&revTo=0 still show the
        # latest
        if revTo == 0:
            filename = identifier + "-" + str(revFrom) + "-" + str(getNumber(diff, 2))

            # Return early if we already have this diff stored
            if os.path.exists("diffs/" + filename):
                return diff

        # Store the diff
        if not os.path.isdir("diffs"):
            os.mkdir("diffs")
        file = open("diffs/" + filename, "w")
        file.write(diff)
        file.close()
        return diff

def getNumber(s, n):
    return int(re.split("\D+", s)[n])


def toInt(s):
    return int(float(s))


def startFormatting(title, identifier, url, source):
    document = """Content-Type:text/html;charset=UTF-8

<!doctype html>
<html lang=en>
 <head>
  <title>%s Tracker</title>
  <style>
   html { background:#fff; color:#000; font:1em/1 Arial, sans-serif }
   form { margin:1em 0; font-size:.7em }
   fieldset { margin:0; padding:0; border:0 }
   legend { padding:0; font-weight:bold }
   input[type=number] { width:4.5em }
   table { border-collapse:collapse }
   table td { padding:.1em .5em }
   table td:last-child { white-space:nowrap }
   img { font-size:xx-small }

   .draft-content { background-color:#eee }
   .stable-draft { background-color:#fcc }
   .implemented { background-color:#f99 }
   .stable { background-color:#f66 }
   body .editorial { color:gray }

   :link { background:transparent; color:#00f }
   :visited { background:transparent; color:#066 }
   img { border:0; vertical-align:middle }

   td :link { color:inherit }
   td a { text-decoration:none; display:block }
   td a:hover { text-decoration:underline }

   .editorial tr.editorial { display:none }

   pre { display:table; white-space:normal }
   samp samp { margin:0; display:block; white-space:pre }
   .deletion { background:#fdd; color:#900 }
   .addition { background:#dfd; color:#000 }
   .line-info { background:#eee; color:#000 }
  </style>
  <script>
   function setCookie(name,value) { localStorage["tracker%s-" + name] = value }
   function readCookie(name) { return localStorage["tracker%s-" + name] }
   function setFieldValue(idName, n) { document.getElementById(idName).value = n }
   function getFieldValue(idName) { return document.getElementById(idName).value }
   function setFrom(n) {
     setCookie("from", n)
     setFieldValue("from", n)
     setFieldValue("to", "")
   }

   function showEdits() { return document.getElementById("editorial").checked }
   function updateEditorial() {
     var editorial = showEdits() ? "" : "editorial"
     setCookie("editorial", editorial)
     document.body.className = editorial
   }
  </script>
 </head>
 <body>
  <h1>%s</h1>
  <form>
   <fieldset>
    <legend>Diff</legend>
    <label>From: <input id=from type=number min=1 value="%s" name=from required></label>
    <label>To: <input id=to type=number min=0 value="%s" name=to></label> (omit for latest revision)
    <input type=submit value="Generate diff">
   </fieldset>
  </form>
  <form>
   <fieldset>
    <legend>Filter</legend>
    <label class="editorial">Show editorial changes <input type="checkbox" id="editorial" checked="" onchange="updateEditorial()"></label>
   </fieldset>
  </form>
  <script>
   if(getFieldValue("from") == "" && readCookie("from") != null)
     setFrom(readCookie("from"))
   if(readCookie("editorial") == "editorial") {
     document.getElementById("editorial").checked = false
     updateEditorial()
   }
  </script>
  %s
 </body>
</html>"""
    showDiff = False
    revFrom = 290 # basically ignored, but sometimes a useful fiction for debugging
    revTo = 0
    os.environ["TZ"] = "" # Set time zone to UTC. Kinda hacky, but works :-)
    form = cgi.FieldStorage()

    if "from" in form:
        try:
            revFrom = toInt(form["from"].value)
            showDiff = True
        except:
            pass

    if showDiff and "to" in form:
        try:
            revTo = toInt(form["to"].value)
            if 0 < revTo < revFrom:
                revFrom, revTo = revTo, revFrom
        except:
            pass

    # Put it on the screen
    if not showDiff:
        #
        # HOME
        #
        if "limit" in form and form["limit"].value == "-1":
            limit = ""
        else:
            limit = " --limit 100"
            try:
                limit = " --limit %s" % toInt(form["limit"].value)
            except:
                pass
        svnLog = os.popen("svn log %s%s" % (source, limit))
        parsedLog = parseRawLog(svnLog)
        formattedLog = formatLog(parsedLog)
        print document % (title, identifier, identifier, title + " Tracker", "", "", formattedLog)
    else:
        #
        # DIFF
        #
        diff = formatDiff(getDiff(source, revFrom, revTo, identifier))
        markuptitle = "<a href=" + url + ">" + title + " Tracker" + "</a>"
        try:
            # This fails if there is no diff -- hack
            revTo = getNumber(diff, 2)
            svnLog = os.popen(getLogCommand(source, revFrom, revTo))
            parsedLog = parseRawLog(svnLog)
            formattedLog = formatLog(parsedLog)
            result = """%s
  <pre id="diff"><samp>%s</samp></pre>
  <p><a href="?from=%s&amp;to=%s" rel=prev>Previous</a> | <a href="?from=%s&amp;to=%s" rel=next>Next</a>
  <p><input type="button" value="Prefill From field for next time!" onclick="setFrom(%s)">""" % (formattedLog, diff, revFrom-1, revFrom, revTo, revTo+1, revTo)

            # Short URL
            shorturlmarkup = ""
            if title == "HTML5":
                shorturl = "http://html5.org/r/"
                if revTo - revFrom == 1:
                    shorturl += str(revTo)
                else:
                    shorturl += str(revFrom) + "-" + str(revTo)
                shorturlmarkup = """<p>Short URL: <code><a href="%s">%s</a></code>\n  """ % (shorturl, shorturl)
            shorturlmarkup += result
            print document % (title, identifier, identifier, markuptitle, revFrom, revTo, shorturlmarkup)
        except:
            print document % (title, identifier, identifier, markuptitle, revFrom, "", "No result.")
