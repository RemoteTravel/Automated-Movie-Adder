import argparse
import gspread
import creds
import requests
from datetime import datetime, date, timedelta

curYear = 2024
monthDict = {
    "Jan": "January",
    "Feb": "February",
    "Mar": "March",
    "Apr": "April",
    "May": "May",
    "Jun": "June",
    "Jul": "July",
    "Aug": "August",
    "Sep": "September",
    "Oct": "October",
    "Nov": "November",
    "Dec": "December",
}


def main():
    s = requests.Session()
    title = input("Enter title: ")
    movieOrSeries = input("Enter movie or series: ")
    score = input("Enter your score: ")
    startDate = input("Enter start date: ")
    endDate = input("Enter end date: ")
    comments = input("Enter comments: ")
    jsonData = getData(s, title, movieOrSeries)
    sa = gspread.service_account()
    sh = sa.open(f"Media Sheet {curYear}")
    if movieOrSeries.startswith("s") or movieOrSeries.startswith("S"):
        addToShowSheet(jsonData, sh, score, startDate, endDate, comments)
    else:
        addToMovieSheet(jsonData, sh, score, startDate, endDate, comments)
        # changes


def getData(session, title, movieOrSeries):  # returns array of data
    url = f"http://www.omdbapi.com/?apikey={creds.apiKey}&"
    newURL = url + f"t={title}&"
    inputType = ""
    if movieOrSeries.startswith("m") or movieOrSeries.startswith("M"):
        newURL = newURL + "type=movie&"
    elif movieOrSeries.startswith("s") or movieOrSeries.startswith("S"):
        newURL = newURL + "type=series&"
    r = session.get(newURL)
    # print(r.json())
    return r.json()


def nextBlankRow(worksheet):
    str_list = list(filter(None, worksheet.col_values(1)))
    return str(len(str_list) + 1)


def addToMovieSheet(json, sh, score, startDate, endDate, comments):
    wks = sh.worksheet("Movies")
    newScore = score
    if not score.isdigit() or int(score) < 0 or int(score) > 10:
        newScore = ""
    newStart = ""
    if startDate.startswith("t") or startDate.startswith("T"):
        newStart = datetime.now().strftime("%B %#d %Y")
    newEnd = ""
    if endDate.startswith("t") or endDate.startswith("T"):
        newEnd = datetime.now().strftime("%B %#d %Y")
    if startDate.startswith("y") or startDate.startswith("Y"):
        yesterday = date.today() - timedelta(days=1)
        newStart = yesterday.strftime("%B %#d %Y")
    if endDate.startswith("y") or endDate.startswith("Y"):
        yesterday = date.today() - timedelta(days=1)
        newEnd = yesterday.strftime("%B %#d %Y")
    nextRow = nextBlankRow(wks)
    title = json["Title"]
    genre = json["Genre"]
    rated = json["Rated"]
    imdbVotesNoComma = json["imdbVotes"].replace(",", "")
    votesRoundThou = str(int(imdbVotesNoComma) // 1000)
    releasedSplit = json["Released"].split(" ")
    day = releasedSplit[0]
    if releasedSplit[0].startswith("0"):
        day = releasedSplit[0].replace("0", "")
    newReleased = monthDict[releasedSplit[1]] + f" {day} " + f"{releasedSplit[2]}"
    runtime = json["Runtime"].split(" ")[0]
    boxOffice = json["BoxOffice"]
    newBoxOffice = str((int(boxOffice.replace("$", "").replace(",", ""))) // 100 % 1000)

    valueArr = [
        title,
        newScore,
        newStart,
        newEnd,
        genre,
        rated,
        votesRoundThou,
        newReleased,
        runtime,
        "",
        newBoxOffice,
        comments,
    ]
    wks.append_row(valueArr, table_range=f"A{nextRow}:L{nextRow}")


def addToShowSheet(json, sh, score, startDate, endDate, comments):
    wks = sh.worksheet("Shows")
    # print("json", json)
    newScore = score
    if not score.isdigit() or int(score) < 0 or int(score) > 10:
        newScore = ""
    newStart = ""
    if startDate.startswith("t") or startDate.startswith("T"):
        newStart = datetime.now().strftime("%B %#d %Y")
    newEnd = ""
    if endDate.startswith("t") or endDate.startswith("T"):
        newEnd = datetime.now().strftime("%B %#d %Y")
    if startDate.startswith("y") or startDate.startswith("Y"):
        yesterday = date.today() - timedelta(days=1)
        newStart = yesterday.strftime("%B %#d %Y")
    if endDate.startswith("y") or endDate.startswith("Y"):
        yesterday = date.today() - timedelta(days=1)
        newEnd = yesterday.strftime("%B %#d %Y")
    nextRow = nextBlankRow(wks)
    title = json["Title"]
    genre = json["Genre"]
    rated = json["Rated"]
    imdbVotesNoComma = json["imdbVotes"].replace(",", "")
    votesRoundThou = str(int(imdbVotesNoComma) // 1000)
    releasedSplit = json["Released"].split(" ")
    day = releasedSplit[0]
    if releasedSplit[0].startswith("0"):
        day = releasedSplit[0].replace("0", "")
    newReleased = monthDict[releasedSplit[1]] + f" {day} " + f"{releasedSplit[2]}"

    valueArr = [
        title,
        newScore,
        "",
        newStart,
        newEnd,
        genre,
        rated,
        votesRoundThou,
        newReleased,
        comments,
    ]
    wks.append_row(valueArr, table_range=f"A{nextRow}:J{nextRow}")


main()
