"""Script to scrape payment card spend data over £500 from gov.scot"""

import argparse
import concurrent.futures
import os
import urllib.parse
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup

MONTHLY_SPEND_URL = (
    "https://www.gov.scot/collections/government-spend-over-gbp500-monthly-reports/"
)

TIMEOUT = 30

SAVE_PATH = "_data/spendsOver500"

COLUMN_HEADERS_ALIASES = {
    "Merchant Category Description": "Merchant Category Name",
    "Merchant Category  Description": "Merchant Category Name",
    "Mercant Category Name": "Merchant Category Name",
    "Merchant Code Description": "Merchant Category Name",
    "Category Code Description": "Merchant Category Name",
    "Merchant Description": "Merchant Category Name",
    "Financial Transaction Date": "Transaction Date",
    "Transaction Amount (£)": "Transaction Amount",
    "Financial Transaction Amount (£)": "Transaction Amount",
    "Description": "Expense Description",
    "Description To Be Published": "Expense Description",
    "Final Description": "Expense Description",
    "Final Expense Description": "Expense Description",
}

def clean_currency(currency_value, temp):
    """Takes currency strings and turns them into floats with 2 decimal places"""

    if not isinstance(currency_value, str):
        return round(currency_value, 2)
    
    currency_value = currency_value.replace(",","")
    currency_value = currency_value.replace("£","")

    try:
        currency_value = round(float(currency_value), 2)
    except:
        print(temp)
        print(currency_value)

    return currency_value

def clean_report(report_dataframe, temp):
    """Cleans up any inconsistencies in the table"""

    # Title case all column names for consistency
    report_dataframe.columns = map(str.title, report_dataframe.columns)

    # Director General only appears in May 2016 so we may as well remove it
    if "Director General" in report_dataframe.columns:
        report_dataframe = report_dataframe.drop(["Director General"], axis=1)

    # Fix column aliases
    report_dataframe = report_dataframe.rename(columns=COLUMN_HEADERS_ALIASES)

    # Remove duplicate header rows
    report_dataframe = report_dataframe[report_dataframe.iloc[:, 0] != report_dataframe.columns[0]]

    # Remove £ and comma from transaction amounts
    report_dataframe["Transaction Amount"] = report_dataframe[
        "Transaction Amount"
    ].apply(lambda x: clean_currency(x, temp))
    
    # Drop blank unnamed columns
    report_dataframe = report_dataframe.loc[
        :, ~report_dataframe.columns.str.contains("^Unnamed")
    ]

    # Finally, check for missing columns and if so, add them
    # January 2020 doesn't have Merchant Category Name
    if "Merchant Category Name" not in report_dataframe.columns:
        report_dataframe.insert(
            loc=2, column="Merchant Category Name", value="Not specified in data source"
        )

    # December 2019 doesn't have Expense Description
    if "Expense Description" not in report_dataframe.columns:
        report_dataframe.insert(
            loc=5, column="Expense Description", value="Not specified in data source"
        )

    return report_dataframe


def extract_report(tag_href, tag_text, skip_existing=False):
    """Extracts the month's spending report from the given href URL and saves it to a JSON file"""

    report_url = tag_href

    split_tag_text = tag_text.split()
    report_year_month_array = split_tag_text[-2:]
    report_title = " ".join(report_year_month_array)

    report_month_name = report_year_month_array[0]
    report_month_number = datetime.strptime(report_month_name, "%B").strftime("%m")
    report_year_number = report_year_month_array[1]
    report_year_month = f"{report_year_number}-{report_month_number}"

    save_file = f"{SAVE_PATH}/{report_year_month}.json"

    if skip_existing and os.path.exists(save_file):
        print(f"Skipping {report_title} - data file already exists")
        return f"Skipped {report_title}"

    print(f"Accessing spend for {report_title} at {report_url}...")

    report_url = urllib.parse.urljoin(MONTHLY_SPEND_URL, report_url)
    report_html = requests.get(report_url, timeout=TIMEOUT)

    report_soup = BeautifulSoup(report_html.content, "html.parser")

    report_table = report_soup.find("table")

    report_dataframe = pd.read_html(str(report_table), header=0, encoding="utf8")[0]

    report_dataframe = clean_report(report_dataframe, report_title)

    report_dataframe.to_json(
        f"{SAVE_PATH}/{report_year_month}.json",
        orient="records",
        date_format="iso",
        indent=4,
        force_ascii=False,
    )

    return f"Completed {report_title} at {report_url}"


def main():
    """Main method"""

    parser = argparse.ArgumentParser(
        description="Scrape government spend data over £500 from gov.scot"
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip months that already have data files (useful for incremental updates)",
    )
    args = parser.parse_args()

    # Pre-check if the data folder exists and if not, create it
    if not os.path.exists(SAVE_PATH):
        os.makedirs(SAVE_PATH)

    index_page_html = requests.get(MONTHLY_SPEND_URL, timeout=TIMEOUT)

    index_soup = BeautifulSoup(index_page_html.content, "html.parser")

    report_url_tags = index_soup.find_all(
        lambda tag: tag.name == "a"
        and tag.text != "Spend over £500: archive (pre - May 2016)"
        and tag.text.startswith("Spend over £500")
    )

    print(f"Got {len(report_url_tags)} tags\n")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(extract_report, tag["href"], tag.text, args.skip_existing)
            for tag in report_url_tags
        ]

        results = []
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            print(result)

    # Regenerate headers.csv only when new files were downloaded
    new_downloads = [r for r in results if r.startswith("Completed")]
    if new_downloads:
        all_headers = []
        for json_file in sorted(os.listdir(SAVE_PATH)):
            if json_file.endswith(".json"):
                year_month = json_file.replace(".json", "")
                df = pd.read_json(f"{SAVE_PATH}/{json_file}")
                all_headers.append([year_month] + df.columns.tolist())

        if all_headers:
            headers_df = pd.DataFrame(all_headers)
            headers_df.to_csv("headers.csv", index=False)


if __name__ == "__main__":
    main()
