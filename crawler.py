import ConfigParser
import pdb
import requests
from bs4 import BeautifulSoup


class IssueScraper:
    headers = ['Articles & Tutorials', 'Sponsored', 'Jobs', 'Libraries & Code', 'News', 'Tools']

    def __init__(self, preferred_topics, issue_number):
        self.preferred_topics = preferred_topics
        self._get_issue(issue_number)

    def _get_issue(self, issue_number):
        issue = requests.get('http://androidweekly.net/issues/issue-{issue_number}'.format(issue_number=issue_number))
        self.bs = BeautifulSoup(issue.text)
        self._update_sections()

    def _update_sections(self):
        self.sections = []
        self.preferred_sections = []
        for header in self.headers:
            section = self.bs.find('h2', text=header)
            self.sections.append(section)
            if header in self.preferred_topics:
               self.preferred_sections.append(section)

    def _get_titles_from_section(self, section):
        next_index = self.sections.index(section) + 1
        next_section_a = None
        if next_index < len(self.sections):
            next_section_a = self.sections[next_index].find_next('a')
        else:
            next_section_a = self.bs.find('footer').find_next('a')
        # recursively collect titles
        def rec_a(titles, current_a, next_section_a):
            if not current_a or current_a == next_section_a:
                return titles
            else:
                current_title = current_a.get_text().strip()
                if current_title:
                    titles.append(current_title)
            return rec_a(titles, current_a.find_next('a'), next_section_a)
        return rec_a([], section.find_next('a'), next_section_a)

    def get_titles(self):
        return reduce(lambda titles1, titles2: titles1 + titles2, [self._get_titles_from_section(section) for section in self.preferred_sections])


def get_last_issue():
    config = ConfigParser.ConfigParser()
    config.readfp(open('config'))
    return config.get('androidweekly.net', 'latest-issue')

def update_last_issue(issue_number):
    config.set('androidweekly.net', 'latest-issue', issue_number)

def get_current_issue():
    from bs4 import BeautifulSoup
    homepage = requests.get('http://androidweekly.net/')
    bs_homepage = BeautifulSoup(homepage.text)
    header = bs_homepage.find('div', {'class': 'issue-header'})
    return header.find('span').get_text().strip().split('#')[1]


if __name__ == '__main__':
    topics = ['Articles & Tutorials', 'Sponsored', 'Libraries & Code', 'Tools']
    current_issue = get_current_issue()
    if current_issue != get_last_issue():
        issue_scraper = IssueScraper(topics, current_issue)
        titles = issue_scraper.get_titles()
        pdb.set_trace()
