import json
import os
from shutil import copyfile
from tempfile import TemporaryDirectory
import subprocess

# This script generates cv.tex (from cv-in.tex) and then compiles cv.pdf

# Some of our latex'ing requires us to be in the same directory as the files
os.chdir(os.path.dirname(os.path.realpath(__file__)))

# Globals ----------------------------------------------------------------------
# These file paths are relative to this script's directory
personalDataJson = "personalData.json"
cvTexPlaceholder = "cv-in.tex"
cvTexGenerated = "cv.tex" # The generated result produced by this script
outputDir = ".."


# Helpers ----------------------------------------------------------------------
def pdfLatex(inputTexFile, outputPdfFile):
    with TemporaryDirectory() as tempDir:
        # Run pdf latex, the pdf should be output with the same basename as in input file
        subprocess.run(["pdflatex", "-output-directory", tempDir, inputTexFile])
        pdfResult = os.path.join(tempDir, os.path.splitext(os.path.basename(inputTexFile))[0] + ".pdf")
        copyfile(pdfResult, outputPdfFile)

def makeTexAuthorList(authors):
    authorList = ", ".join(authors)
    return authorList.replace("Kevin Karsch", "{\\bf Kevin Karsch}")


# Main -------------------------------------------------------------------------
# Read / parse inputs
with open(cvTexPlaceholder) as tex:
    texLines = tex.readlines()

with open(personalDataJson, "r") as jsonFile:
    personalData = json.load(jsonFile)

education = personalData["education"]
experience = personalData["experience"]
publications = personalData["papers"]
patents = personalData["patents"]
bookchapters = personalData["bookchapters"]
teaching = personalData["teaching"]
funding = personalData["funding"]
awards = personalData["awards"]
press = personalData["press"]
skills = personalData["skills"]

# Find placeholders and replace them with generated tex, writing the new file as we go
with open(cvTexGenerated, "w") as generatedTex:
    generatedTex.write("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
    generatedTex.write("%%\n")
    generatedTex.write("%% This file was generated by {}\n".format(os.path.basename(__file__)))
    generatedTex.write("%%\n")
    generatedTex.write("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
    generatedTex.write("\n\n")

    for line in texLines:
        if line.strip() == "{{education-placeholder}}":
            for item in education:
                degree = item["degree"]
                where = item["where"]
                years = item["years"]
                bullets = item["bullets"]
                generatedTex.write("\\begin{{cvEvent}}{{{}}}{{{}}}{{{}}}\n".format(degree, where, years))
                for bullet in bullets:
                    generatedTex.write("\\cvEventBullet{{{}}}\n".format(bullet))
                generatedTex.write("\\end{cvEvent}\n\n")
        elif line.strip() == "{{experience-placeholder}}":
            for item in experience:
                role = item["role"]
                where = item["where"]
                years = item["years"]
                bullets = item["bullets"]
                generatedTex.write("\\begin{{cvEvent}}{{{}}}{{{}}}{{{}}}\n".format(role, where, years))
                for bullet in bullets:
                    if isinstance(bullet, list):
                        for subbullet in bullet:
                            generatedTex.write("\\cvEventBulletSub{{{}}}\n".format(subbullet))
                    else:
                        generatedTex.write("\\cvEventBullet{{{}}}\n".format(bullet))
                generatedTex.write("\\end{cvEvent}\n\n")
        elif line.strip() == "{{teaching-placeholder}}":
            for item in teaching:
                role = item["role"]
                where = item["where"]
                years = item["years"]
                bullets = item["bullets"]
                generatedTex.write("\\begin{{cvEvent}}{{{}}}{{{}}}{{{}}}\n".format(role, where, years))
                for bullet in bullets:
                    generatedTex.write("\\cvEventBullet{{{}}}\n".format(bullet))
                generatedTex.write("\\end{cvEvent}\n\n")
        elif line.strip() == "{{publications-placeholder}}":
            for item in publications:
                title = item["title"]
                authors = item["authors"]
                venue = item["venue"]
                publicationString = "{}. {}, {{\it {}}}.".format(makeTexAuthorList(authors), title, venue)
                generatedTex.write("\\cvEventBullet{{{}}}\n".format(publicationString))
        elif line.strip() == "{{patents-placeholder}}":
            for item in patents:
                title = item["title"]
                authors = item["authors"]
                pending = item.get("pending", False)
                if pending:
                    patentNumber = "(pending)"
                else:
                    patentNumber = item["patentNumber"]
                patentString = "{}. {}, {{\it {}}}.".format(makeTexAuthorList(authors), title, patentNumber)
                generatedTex.write("\\cvEventBullet{{{}}}\n".format(patentString))
        elif line.strip() == "{{bookchapters-placeholder}}":
            for item in bookchapters:
                title = item["title"]
                authors = item["authors"]
                book = item["book"]
                pages = item["pages"]
                editors = item["editors"]
                publisher = item["publisher"]
                year = item["year"]
                chapterString = "{}. {}. In {{\it {}}} ({} eds). {}, {}, {}.".format(makeTexAuthorList(authors), title, book, ", ".join(editors), publisher, year, pages)
                generatedTex.write("\\cvEventBullet{{{}}}\n".format(chapterString))
        elif line.strip() == "{{funding-placeholder}}":
            for item in funding:
                name = item["name"]
                award = item["award"]
                years = item["years"]
                fundingString = "{}. {{\it {}}}, {}.".format(award, name, years)
                generatedTex.write("\\cvEventBullet{{{}}}\n".format(fundingString))
        elif line.strip() == "{{awards-placeholder}}":
            for item in awards:
                name = item["name"]
                year = item["year"]
                link = item.get("link", None)
                if link:
                    awardString = "\\href{{{}}}{{{}}}, {}.".format(link, name, year)
                else:
                    awardString = "{}, {}.".format(name, year)
                generatedTex.write("\\cvEventBullet{{{}}}\n".format(awardString))
        elif line.strip() == "{{press-placeholder}}":
            for item in press:
                title = item["title"]
                pubInfo = item.get("pubInfo", None)
                link = item["link"]
                pressString = "\\href{{{}}}{{{}}}".format(link, title)
                if pubInfo:
                    pressString += " {}".format(pubInfo)
                generatedTex.write("\\cvEventBullet{{{}}}\n".format(pressString))
        elif line.strip() == "{{skills-placeholder}}":
            for key, value in skills.items():
                skillType = key.capitalize()
                skillList = ", ".join(value)
                skillString = "{{\\bf {}}}: {}".format(skillType, skillList)
                generatedTex.write("\\cvEventBullet{{{}}}\n".format(skillString))
        else:
            generatedTex.write(line)

# Compile tex files
pdfLatex(cvTexGenerated, os.path.join(outputDir, "cv.pdf"))
