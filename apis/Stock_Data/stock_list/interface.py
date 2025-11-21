import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
import pandas as pd
import akshare as ak
from actionweaver import action
from data_connection.data_handler import handle_large_data
from crawler.sectorsorindustry.stockanalysisSpecificSectorsOrIndustry import StockAnalysis_Specific_Sector, StockAnalysis_Specific_Industry


@action(name="RetrieveAShareStockList")
@handle_large_data()
def stock_info_a_code_name() -> pd.DataFrame:
    """
    Get the list of A-share stock ticker symbol and their corresponding company names from the Shanghai, Shenzhen, and Beijing stock exchanges.
    
    Return:
        ['code','name']
    """
    df = ak.stock_info_a_code_name()
    
    return df


@action(name="RetrieveShanghaiStockList")
@handle_large_data()
def stock_info_sh_name_code(symbol="主板A股",
                            ) -> pd.DataFrame:
    """
    Get the list of stocks from the Shanghai Stock Exchange.

    Parameters:
    - symbol (str): Type of stocks to retrieve. Default is "主板A股". Choose from {"主板A股", "主板B股", "科创板"}.
    
    Return:
        ['证券代码', '证券简称', '公司全称', '上市日期']
    """
    df = ak.stock_info_sh_name_code(symbol=symbol)
    
    return df


@action(name="RetrieveShenzhenStockList")
@handle_large_data()
def stock_info_sz_name_code(symbol="A股列表",
                            ) -> pd.DataFrame:
    """
    Get the list of stocks from the Shenzhen Stock Exchange.

    Parameters:
    - symbol (str): Type of stocks to retrieve. Default is "A股列表". Choose from {"A股列表", "B股列表", "CDR列表", "AB股列表"}.
    
    Return:
        ['板块', 'A股代码', 'A股简称', 'A股上市日期', 'A股总股本', 'A股流通股本', '所属行业']
    """
    df = ak.stock_info_sz_name_code(symbol=symbol)
    
    return df


@action(name="RetrieveBeijingStockList")
@handle_large_data()
def stock_info_bj_name_code() -> pd.DataFrame:
    """
    Get the list of stocks from the Beijing Stock Exchange.
    
    Return:
        ['证券代码', '证券简称', '总股本', '流通股本', '上市日期', '所属行业', '地区', '报告日期']
    """
    df = ak.stock_info_bj_name_code()
    
    return df

@action('Get_the_stock_list_for_specified_industry')
@handle_large_data(boundary=20)
def get_industry_list(industry):
    '''
    Get the complete list of stocks for a specified industry in the U.S. stock market.
    
    Parameters type 1:
    The input for this tool is a specific industry from the list below,
    you can easily infer the meaning of an industry from its name:

    ['Biotechnology', 'Asset Management', 'Banks - Regional', 'Shell Companies', 'Software - Application', 
    'Medical Devices', 'Software - Infrastructure', 'Drug Manufacturers - Specialty & Generic', 
    'Oil & Gas E&P', 'Capital Markets', 'Aerospace & Defense', 'Information Technology Services', 
    'Specialty Industrial Machinery', 'Internet Content & Information', 'Packaged Foods', 'Semiconductors', 
    'Diagnostics & Research', 'Communication Equipment', 'Health Information Services', 'Credit Services', 
    'Medical Instruments & Supplies', 'Telecom Services', 'Specialty Chemicals', 'Oil & Gas Equipment & Services', 
    'Medical Care Facilities', 'Restaurants', 'Auto Parts', 'Specialty Retail', 'Oil & Gas Midstream', 
    'Electrical Equipment & Parts', 'Entertainment', 'Internet Retail', 'Gold', 'Electronic Components', 
    'Education & Training Services', 'Real Estate Services', 'Other Industrial Metals & Mining', 
    'Advertising Agencies', 'Insurance - Property & Casualty', 'REIT - Mortgage', 'Engineering & Construction', 
    'Utilities - Regulated Electric', 'Computer Hardware', 'Marine Shipping', 'Specialty Business Services', 
    'Building Products & Equipment', 'Apparel Retail', 'Auto Manufacturers', 'Furnishings, Fixtures & Appliances', 
    'Scientific & Technical Instruments', 'Semiconductor Equipment & Materials', 'Auto & Truck Dealerships', 
    'Household & Personal Products', 'Leisure', 'REIT - Retail', 'Staffing & Employment Services', 
    'Farm & Heavy Construction Machinery', 'REIT - Office', 'Packaging & Containers', 'Solar', 
    'Rental & Leasing Services', 'Security & Protection Services', 'Steel', 'Utilities - Renewable', 
    'Electronic Gaming & Multimedia', 'REIT - Diversified', 'Apparel Manufacturing', 'Farm Products', 
    'Insurance - Life', 'Integrated Freight & Logistics', 'Banks - Diversified', 'Conglomerates', 
    'Residential Construction', 'Airlines', 'Insurance - Specialty', 'Oil & Gas Refining & Marketing', 
    'REIT - Residential', 'Waste Management', 'Resorts & Casinos', 'Metal Fabrication', 'Gambling', 
    'REIT - Specialty', 'Trucking', 'Agricultural Inputs', 'Recreational Vehicles', 'REIT - Industrial', 
    'Consumer Electronics', 'Drug Manufacturers - General', 'Consulting Services', 'Insurance Brokers', 
    'Beverages - Non-Alcoholic', 'Personal Services', 'Oil & Gas Integrated', 'Travel Services', 
    'REIT - Hotel & Motel', 'Industrial Distribution', 'Other Precious Metals & Mining', 'Building Materials', 
    'REIT - Healthcare Facilities', 'Insurance - Diversified', 'Broadcasting', 'Mortgage Finance', 
    'Pollution & Treatment Controls', 'Utilities - Diversified', 'Utilities - Regulated Water', 'Chemicals', 
    'Utilities - Regulated Gas', 'Real Estate - Development', 'Footwear & Accessories', 'Lodging', 
    'Luxury Goods', 'Tools & Accessories', 'Grocery Stores', 'Electronics & Computer Distribution', 
    'Healthcare Plans', 'Food Distribution', 'Railroads', 'Pharmaceutical Retailers', 'Tobacco', 
    'Financial Data & Stock Exchanges', 'Beverages - Wineries & Distilleries', 'Oil & Gas Drilling', 
    'Home Improvement Retail', 'Discount Stores', 'Insurance - Reinsurance', 'Medical Distribution', 
    'Uranium', 'Publishing', 'Airports & Air Services', 'Beverages - Brewers', 'Thermal Coal', 
    'Paper & Paper Products', 'Business Equipment & Supplies', 'Coking Coal', 'Department Stores', 
    'Real Estate - Diversified', 'Silver', 'Copper', 'Lumber & Wood Production', 'Aluminum', 
    'Textile Manufacturing', 'Confectioners', 'Utilities - Independent Power Producers', 
    'Infrastructure Operations', 'Financial Conglomerates']

        For example, `Consulting Services`.
    '''
    stockanalysis = StockAnalysis_Specific_Industry(industry)
    return stockanalysis.download_industry()


@action('Get_sector_stock_list')
@handle_large_data(boundary=20)
def get_sector_list(sector):
    '''
    Useful to scrape the stock list for the specified sector.
    
    Parameters:
    
    The input for this tool is a specific sector element from the list below:
    ["Financials", "Healthcare", "Technology", "Industrials", "Consumer Discretionary", "Real Estate",
        "Materials", "Communication Services", "Energy", "Consumer Staples", "Utilities"]
        
        For example, `Energy`.
    '''
    stockanalysis = StockAnalysis_Specific_Sector(sector)
    return stockanalysis.download_sector()