from datetime import datetime

def now():
    # 返回当前的日期和时间
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def today():
    # 返回当前的日期
    return datetime.now().date().strftime("%Y-%m-%d")

def year():
    # 返回当前的年份
    return str(datetime.now().year)

def second():
    # 返回当前的时间，精确到秒
    return datetime.now().strftime("%H:%M:%S")

def yyyymmdd():
    # 返回当前的日期，格式为YYYYMMDD
    return datetime.now().strftime("%Y%m%d")

def yyyymm():
    # 返回当前的日期，格式为YYYYMM
    return datetime.now().strftime("%Y%m")

def yyyyq():
    now = datetime.now()
    year = now.year
    month = now.month
    quarter = (month - 1) // 3 + 1
    return f"{year}Q{quarter}"
