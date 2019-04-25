import json

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
        if authorData and "website" in authorData:
            linkedAuthorList.append('<a href="{website}">{name}</a>'.format(website = authorData["website"], name = authorName))
        else:
            linkedAuthorList.append(authorName)
    return linkedAuthorList

def getLeadingWhitespaceCharacters(string):
    return string[:len(string.rstrip())-len(string.strip())]

# main -------------------------------------------------------------------------
publicationJson = "./publications.json"
placeholderWebpage = "./index-in.html"
outputWebpage = "../index.html"

with open(placeholderWebpage) as webpage:
    webpageHtmlLines = webpage.readlines()

with open(publicationJson, "r") as jsonFile:
    publicationData = json.load(jsonFile)

fullAuthorList = publicationData["authors"]
fullPaperList = publicationData["papers"]
fullPatentList = publicationData["patents"]

papersHtmlSnippets = []
for paper in fullPaperList:
    #Get all paper related data (and fail if anything necessary is missing)
    paperTitle = paper["title"]
    paperVenue= paper["venue"]
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
        '    <img class="img-fluid rounded mx-auto d-block" width="300px" src="{rep_image_link}">\n'.format(rep_image_link = repImageLink),
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
    patentLink = patent["link"]
    patentNumber = patent["patentNumber"]

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
        if line.strip() == "{papers_placeholder}":
            leadingWhitespace = getLeadingWhitespaceCharacters(line)
            allHtmlLines = [item for sublist in papersHtmlSnippets for item in sublist]
            for newline in [leadingWhitespace + html for html in allHtmlLines]:
                generatedWebpage.write(newline)
        elif line.strip() == "{patents_placeholder}":
            leadingWhitespace = getLeadingWhitespaceCharacters(line)
            allHtmlLines = [item for sublist in patentsHtmlSnippets for item in sublist]
            for newline in [leadingWhitespace + html for html in allHtmlLines]:
                generatedWebpage.write(newline)
        else:
            generatedWebpage.write(line)
