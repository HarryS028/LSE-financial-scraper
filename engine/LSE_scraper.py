from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
import re
import itertools
import sys



# Function that scrapes financial data from a LSE fundamentals web page
def scraper(link):

    driver = webdriver.PhantomJS()
    driver.get(link)
    html = driver.execute_script("return document.body.outerHTML;")
    soup = BeautifulSoup(html, 'html.parser')

    return soup


# Function that converts scraped LSE data in to long and narrow format dataframe, columns: company name, metric, year, value, currency, unit

def processor(text, company_name, metric_list):

    # Get positions of dateyearend
    pattern = r'\d{4}-\d{2}-\d{2}'
    columns = [y.start() for y in re.finditer(pattern, text)]

    dates = []
    for p in columns:
        dates.append(text[p:p+9])

    dates_dict = dict(zip(columns, dates))

    alls = ['Total Revenue', 'Cost of Revenue', 'Gross Profit', 'Operating Expenses', 'Other Operating expenses', 'Operating profit', 'Net interest', 'Other non operating income/expense',
     r'Pre tax profits \(from continued &a; discontinued\)', 'Below line adjustments', 'Depreciation &a; Amortization',
    'Taxes', r'After tax profits \(from continued &a; discontinued\)', r'Net profit \(from continued &a; discontinued\)', 
    'Equity Holders of parent company', 'Continued EPS - Basic', r'Continued &a; Discontinued EPS - Basic', 'Dividend per share', 'Total Assets', 'Non-current assets',
    'Current assets', 'Total liabilities', 'Non-current liabilities', 'Current liabilities', 'Net assets', 'Total Equity', 'Shareholders Funds',
    'PE Ratio', 'PEG', 'Earnings per Share Growth', 'Dividend Cover', 'Revenue Per Share', 'Pre-Tax Profit per Share', 'Operating Margin', 'Return on Capital Employed',
    'Dividend Yield', 'Dividend per Share Growth', r'Net Asset Value per Share \(exc. Intangibles\)', 'Net Gearing']

    ratios = ['PE Ratio', 'PEG', 'Earnings per Share Growth', 'Dividend Cover', 'Revenue Per Share', 'Pre-Tax Profit per Share', 'Operating Margin', 'Return on Capital Employed',
    'Dividend Yield', 'Dividend per Share Growth', r'Net Asset Value per Share \(exc. Intangibles\)', 'Net Gearing']

    balance_sheet = ['Total Assets', 'Non-current assets', 'Current assets', 'Total liabilities', 'Non-current liabilities', 'Current liabilities', 'Net assets', 
    'Total Equity', 'Shareholders Funds']

    income_state = ['Total Revenue', 'Cost of Revenue', 'Gross Profit', 'Operating Expenses', 'Other Operating expenses', 'Operating profit', 'Net interest',
     'Other non operating income/expense', r'Pre tax profits \(from continued &a; discontinued\)', 'Below line adjustments', 'Depreciation &a; Amortization',
    'Taxes', r'After tax profits \(from continued &a; discontinued\)', r'Net profit \(from continued &a; discontinued\)', 
    'Equity Holders of parent company', 'Continued EPS - Basic', r'Continued &a; Discontinued EPS - Basic', 'Dividend per share']

    metrics = []
    if metric_list[0] == "true":
        metrics = metrics + alls
    
    if metric_list[1] == "true":
        metrics = metrics + ratios

    if metric_list[2] == "true":
        metrics = metrics + balance_sheet

    if metric_list[3] == "true":
        metrics = metrics + income_state

    js_extension = '&q;,&q;value&q;:'
    pattern2 = r'-?\d+(?:\.\d+)?'

    # Get currency positions and values, compare with dates dict to get currency by year
    pattern3 = r'currency&q;:{&q;label&q'
    pattern4 = r'[A-Z]{3}'
    currency_pos = [c.start() for c in re.finditer(pattern3, text)]
    currency_values = []
    for c in currency_pos:
        currency_soup = text[c: c + 100]
        currency = re.search(pattern4, currency_soup)
        currency_values.append(currency.group())

    currency_dict = dict(zip(currency_pos, currency_values))

    # Sort keys for loop
    dates_dict_keys = list(reversed(sorted(dates_dict.keys())))

    cur_dat_dict = {}
    for cur in currency_dict:
        for d in dates_dict_keys:
            if d < cur:
                cur_dat_dict[dates_dict[d]] = currency_dict[cur]
                break

    output_list = []
    # For loop over metrics
    for metric in metrics:

        # Get positions of the metric so we can find the year
        metric_positions = [p.start() for p in re.finditer(metric+js_extension+pattern2, text)]

        metric_dates = []
        for item in metric_positions:
            for k in dates_dict_keys:
                if k < item:
                    metric_dates.append(dates_dict[k])
                    break


        # Pull out values
        value_soup = re.findall(metric+js_extension+pattern2, text)
        values = []
        for value in value_soup:
            v = re.search(pattern2, value)
            values.append(v.group())


        metrics_list = [metric for i in range(len(metric_dates))]
        company_list = [company_name for i in range(len(metric_dates))]

        working_output = list(zip(company_list, metrics_list, metric_dates, values))
        working_output = list(set(working_output))
        output_list.append(working_output)
    
    output_list = list(itertools.chain.from_iterable(output_list))

    # Put in to dataframe long narrow format
    df = pd.DataFrame(output_list, columns = ['Company name', 'Metric', 'FYE', 'Value'])
    df['Year'] = df['FYE'].str[0:4]

    # Add currencies to dataframe
    currency_map_dict = {}
    for k in cur_dat_dict:
        key_ = (re.search(r'\d{4}', k)).group()
        value_ = cur_dat_dict[k]
        currency_map_dict[key_] = value_

    currency_df = pd.DataFrame.from_dict(currency_map_dict, orient='Index', columns=['Currency'])

    # Join currency dictionary to df
    df = df.merge(currency_df, how="left", left_on="Year", right_index=True)
 
    # Export to excel
    #df.to_excel(r'test_output.xlsx', encoding='UTF-8')

    return df

inputs = sys.argv[1]
check_status = sys.argv[2]

def main_func(input_file, status):

    status_list = status.split(",")

    # Generate output location output_loc
    slash_pos = input_file.rfind('\\')
    output_loc = input_file[ : slash_pos + 1]

    # Take first sheet of spreadsheet
    xls_file = pd.ExcelFile(input_file)
    df = xls_file.parse('Sheet1')

    # Main process
    df_out = pd.DataFrame(columns=['Company name', 'Metric', 'FYE'])
    for i in range(len(df.iloc[:, 0])):
        company = df.iloc[i, 0]
        url = df.iloc[i, 1]
        text_current = str(scraper(url))
        df_current = processor(text_current, company, status_list)
        df_out = df_out.append(df_current, ignore_index=True)

    df_out.to_excel(output_loc + 'LSE-financials.xlsx', encoding='UTF-8')
    return "Scraping complete"

#print(main_func(r"C:\Users\Harry\Python\test_data.xlsx", "false,true,false,false"))
print(main_func(inputs, check_status))
sys.stdout.flush()