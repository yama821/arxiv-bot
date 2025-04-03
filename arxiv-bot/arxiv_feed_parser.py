#!/usr/bin/env python3
# written by So Okada so.okada@gmail.com
# a simple parser for arXiv new submission rss feeds
# a part of twXiv
# https://github.com/so-okada/twXiv/

import re
import feedparser
import datetime
from dateutil.parser import parse


class retrieve:
    def __init__(self, cat, aliases):
        url = "http://rss.arxiv.org/rss/" + cat
        resp = feedparser.parse(url)

        titles = []
        primary_subjects = []
        identifiers = []
        authors = []
        abstracts = []
        labels = []
        versions = []
        published_dates = []
        for each in resp.entries:
            titles.append(each["title"])
            subject = each["tags"][0]["term"]
            subject = alias_replace(subject, aliases)
            primary_subjects.append(subject)

            # new submissions, cross-lists, or replacements
            announce_type = each["arxiv_announce_type"]
            if "replace" in announce_type:
                labels.append("Replacement")
            elif "cross" in announce_type:
                labels.append("Cross-list")
            elif subject == cat:
                labels.append("New submission")
            else:
                labels.append("Cross-list")

            oai = each["id"]
            version = re.sub("v", "", re.findall("v[0-9]+", oai)[0])
            # versions
            versions.append(version)
            identifiers.append(re.sub("v[0-9]+", "", re.sub("oai:arXiv.org:", "", oai)))
            authors.append(re.sub("\n[ ]+", ", ", each["author"]))
            abstracts.append(each["summary"])

            dt = datetime.datetime.strptime(each["published"], "%a, %d %b %Y %H:%M:%S %z")
            dt_jst = dt.astimezone(datetime.timezone(datetime.timedelta(hours=9)))
            published_dates.append(dt_jst)

        self.cat = cat
        self.feed = resp
        self.bozo = resp["bozo"]
        self.entries = resp.entries
        self.updated = resp["feed"]["published"]
        self.updated_parsed = datetime.datetime(*resp["feed"]["published_parsed"][:6])
        self.identifiers = identifiers
        self.authors = authors
        self.titles = titles
        self.labels = labels
        self.primary_subjects = primary_subjects
        self.abstracts = abstracts
        self.versions = versions
        self.published_dates = published_dates

        # total number of new submissions/crosslists/replacements
        self.total = len(resp.entries)

        # metadata for new submissions/cross-lists/replacements
        newsubmissions = []
        crosslists = []
        replacements = []
        len_identifiers = len(self.identifiers)
        for each in range(len_identifiers):
            entry = {}
            entry["id"] = self.identifiers[each]
            entry["abs_url"] = "https://arxiv.org/abs/" + entry["id"]
            entry["pdf_url"] = re.sub("abs", "pdf", entry["abs_url"])
            entry["html_url"] = re.sub("abs", "html", entry["abs_url"])
            entry["title"] = self.titles[each]
            entry["authors"] = self.authors[each]
            entry["primary_subject"] = self.primary_subjects[each]
            entry["abstract"] = self.abstracts[each]
            entry["label"] = self.labels[each]
            entry["version"] = self.versions[each]
            entry["published"] = self.published_dates[each]
            # comments and subjects are not in feed 2020-07-12
            entry["comments"] = ""
            entry["subjects"] = ""

            if entry["label"] == "New submission":
                newsubmissions.append(entry)
            elif entry["label"] == "Cross-list":
                crosslists.append(entry)
            else:
                replacements.append(entry)

        self.newsubmissions = newsubmissions
        self.crosslists = crosslists
        self.replacements = replacements

        self.num_newsubmissions = len(newsubmissions)
        self.num_crosslists = len(crosslists)
        self.num_replacements = len(replacements)


def alias_replace(subject, aliases):
    if not aliases:
        return subject
    for i, j in aliases.items():
        if j == subject:
            return i
    return subject

if __name__ == "__main__":
    retriever = retrieve('math.CO', None)
    print(type(retriever.entries[0]))
    for entry in retriever.newsubmissions:
        print(entry["abs_url"])
    
    print(retriever.newsubmissions[0]["published"])
