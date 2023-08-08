from datetime import datetime
import requests
from bs4 import BeautifulSoup
import urllib.parse
import concurrent.futures
import pandas as pd
import os


MONTHLY_SPEND_URL = (
    "https://www.gov.scot/collections/government-spend-over-gbp500-monthly-reports/"
)


def extract_report(tag_href, tag_text, monthly_spend_url):
    report_url = tag_href

    split_tag_text = tag_text.split()
    report_year_month_array = split_tag_text[-2:]
    report_title = " ".join(report_year_month_array)

    report_month_name = report_year_month_array[0]
    report_month_number = datetime.strptime(report_month_name, "%B").strftime("%m")
    report_year_number = report_year_month_array[1]
    report_year_month = f"{report_year_number}-{report_month_number}"

    print(f"Accessing spend for {report_title} at {report_url}...")

    report_url = urllib.parse.urljoin(monthly_spend_url, report_url)
    report_html = requests.get(report_url)

    report_soup = BeautifulSoup(report_html.content, "html.parser")

    report_table = report_soup.find("table")

    report_dataframe = pd.read_html(str(report_table), header=0, encoding="utf8")[0]

    report_dataframe.to_json(
        f"data/{report_year_month}.json",
        orient="records",
        date_format="iso",
        indent=4,
        force_ascii=False,
    )

    return f"Completed {report_title} at {report_url}"


def main():

    # Pre-check if the data folder exists and if not, create it
    if not os.path.exists('data'):
        os.makedirs('data')

    index_page_html = requests.get(MONTHLY_SPEND_URL)

    index_soup = BeautifulSoup(index_page_html.content, "html.parser")

    report_url_tags = index_soup.find_all(
        lambda tag: tag.name == "a"
        and tag.text != "Spend over £500: archive (pre - May 2016)"
        and tag.text.startswith("Spend over £500")
    )

    print(f"Got {len(report_url_tags)} tags\n")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(extract_report, tag["href"], tag.text, MONTHLY_SPEND_URL)
            for tag in report_url_tags
        ]

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            print(result)


if __name__ == "__main__":
    main()
