import json
import os

# This script generates the homepage from index-in.html

# Globals ----------------------------------------------------------------------
thisDir = os.path.dirname(os.path.realpath(__file__))
personalDataJson = os.path.join(thisDir, "personalData.json")
placeholderWebpage = os.path.join(thisDir, "index-in.html")
outputWebpage = os.path.join(thisDir, "..", "index.html")


# Helpers ----------------------------------------------------------------------
def findAuthor(authorName, fullAuthorList):
    for authorData in fullAuthorList:
        if "name" in authorData:
            if authorName == authorData["name"]:
                return authorData
    return None #Author not found

def generateLinkedAuthorList(paperAuthorList, fullAuthorList):
    linkedAuthorList = []
    for authorName in paperAuthorList:
        authorData = findAuthor(authorName, fullAuthorList)
        if authorName.lower() == "kevin karsch": # Case insensitive just in case
            linkedAuthorList.append('<b>Kevin Karsch</b>') # No need to link to the website we're already on
        elif authorData and "website" in authorData:
            linkedAuthorList.append('<a href="{website}">{name}</a>'.format(website = authorData["website"], name = authorName))
        else:
            linkedAuthorList.append(authorName)
    return linkedAuthorList

def getLeadingWhitespaceCharacters(string):
    return string[:len(string.rstrip())-len(string.strip())]


# Main -------------------------------------------------------------------------
# Read / parse inputs
with open(placeholderWebpage) as webpage:
    webpageHtmlLines = webpage.readlines()

with open(personalDataJson, "r") as jsonFile:
    personalData = json.load(jsonFile)

linksList = personalData["links"]
fullAuthorList = personalData["authors"]
fullPaperList = personalData["papers"]
fullPatentList = personalData["patents"]

linksHtmlSnippets = []
for linkObject in linksList:
    name = linkObject["name"]
    link = linkObject["link"]
    linksHtmlSnippets.append('<a href="{link}">{name}</a>'.format(link = link, name = name))


papersHtmlSnippets = []
for paper in fullPaperList:
    #Get all paper related data (and fail if anything necessary is missing)
    paperTitle = paper["title"]
    paperVenue = paper["venue"]
    paperAuthors = paper["authors"]
    paperAllLinks = paper["links"]
    paperLink = paperAllLinks["arxiv"] if ("arxiv" in paperAllLinks) else paperAllLinks["paper"]
    repImageLink = paperAllLinks["repImage"]
    extraLinks = paperAllLinks.get("extras")
    paperNotes = paper.get("notes")

    # Create linked author list
    authorList = generateLinkedAuthorList(paperAuthors, fullAuthorList)

    # Create extra links
    extrasList = []
    if isinstance(extraLinks, dict):
        for name, link in extraLinks.items():
            extrasList.append('<a href="{link}">{name}</a>'.format(link = link, name = name))

    # Format notes (if any)
    notesHtml = '      <p class="small">{}</p>\n'.format(paperNotes) if paperNotes else ""

    # Store html
    papersHtmlSnippets.append([
        '<div class="row mt-4 align-items-center">\n', #add top pad, align column content vertical center
        '  <div class="col-4 d-none d-md-block">\n', #hide if less than md
        '    <img class="img-fluid rounded mx-auto d-block" width="200px" src="{rep_image_link}">\n'.format(rep_image_link = repImageLink),
        '  </div>\n',
        '  <div class="col-xs-12 col-md-8">\n', #8 if md, 12 if less
        '      <p class="lead"><a href="{paper_link}">{paper_title}</a></p>\n'.format(paper_link = paperLink, paper_title = paperTitle),
        '      <p>{author_list}</p>\n'.format(author_list = ", ".join(authorList)),
        '      <p><i>{venue}</i></p>\n'.format(venue = paperVenue),
        '      <p>{extras}</p>\n'.format(extras = (" | ").join(extrasList)),
        notesHtml,
        '    </ul>\n',
        '  </div>\n',
        '</div>\n\n',
    ]);


patentsHtmlSnippets = []
for patent in fullPatentList:
    #Get all paper related data (and fail if anything necessary is missing)
    patentTitle = patent["title"]
    patentAuthors = patent["authors"]
    patentLink = patent.get("link")
    patentNumber = patent.get("patentNumber")
    pending = patent.get("pending", False)

    if pending: #don't show pending patents
        continue

    # Create linked author list
    authorList = generateLinkedAuthorList(patentAuthors, fullAuthorList)

    # Store html
    patentsHtmlSnippets.append([
        '<div class="row mt-4">\n',
        '  <div class="col-12">\n',
        '    <p class="lead"><a href="{patent_link}">{patent_title}</a></p>\n'.format(patent_link = patentLink, patent_title = patentTitle),
        '    <p>{author_list}</p>\n'.format(author_list = ", ".join(authorList)),
        '    <p>Patent No. {patent_no}</p>\n'.format(patent_no = patentNumber),
        '  </div>\n',
        '</div>\n\n',
    ]);

# Find placeholders and replace them with generated html, writing the new webpage as we go
with open(outputWebpage, "w") as generatedWebpage:
    for line in webpageHtmlLines:
        if line.strip() == "{{links-placeholder}}":
            leadingWhitespace = getLeadingWhitespaceCharacters(line)
            generatedWebpage.write(leadingWhitespace + ' | '.join(linksHtmlSnippets))

        elif line.strip() == "{{papers-placeholder}}":
            leadingWhitespace = getLeadingWhitespaceCharacters(line)
            allHtmlLines = [item for sublist in papersHtmlSnippets for item in sublist]
            for newline in [leadingWhitespace + html for html in allHtmlLines]:
                generatedWebpage.write(newline)

        elif line.strip() == "{{patents-placeholder}}":
            leadingWhitespace = getLeadingWhitespaceCharacters(line)
            allHtmlLines = [item for sublist in patentsHtmlSnippets for item in sublist]
            for newline in [leadingWhitespace + html for html in allHtmlLines]:
                generatedWebpage.write(newline)

        else:
            generatedWebpage.write(line)
