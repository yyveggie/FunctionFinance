import rootutils
rootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
from crewai import Task
from textwrap import dedent
from pydantic import BaseModel, Field
from scheduler.prompt_tips import tip_section, encourage_section
import time

class Output(BaseModel):
    recommendations: list[dict] = Field(description='A list containing three dictionaries, giving the final confidence level and reason for each recommendation.')

class FinancialTasks:
    def global_news_analysis_task(self, agent, company):
        return Task(
            description=dedent(
                f"""\
                    Extracting information from global news that has significant impacts on the financial markets, conducting in-depth analysis of its effects on {company} stock, and predicting its potential impacts on future trends in industries and markets related to {company}. Specifically:

                    1.Overview of News Events
                    2 Event Impact Analysis
                    3 Risk and Opportunity Identification
                    4 Market Trend Prediction
                    5 Investment Strategy Recommendations

                    After completing each round of tasks, you need to combine previous recommendations (including your own other agents), and provide recommendations for the {company} stock after the current task is completed (i.e., buy, hold, or sell), along with the confidence level for each recommendation, such as buy: 60%, hold: 20%, sell: 20%, and provide a brief reason for each confidence level.

                    {tip_section()}, {encourage_section()}
                """
            ),
            expected_output="A brief, focused, and neatly formatted analysis report containing the mentioned key points, and providing recommendations for 'sell', 'buy', and 'hold' along with confidence levels and reasons at the end",
            output_pydantic=Output,
            async_execution=False,
            agent=agent,
            output_file=f"./output/global_news_analysis_{company}_{time.time()}.md",
        )

    def financial_industry_analysis_task(self, agent, company):
        return Task(
            description=dedent(
                f"""\
                    Interpret the user's query or follow the manager's directive to identify the target financial industry. Utilize a set of analytical tools to gather and process financial news, data and reports relevant to the identified industry. Conduct in-depth analysis on the following aspects:
                    1. Industry Overview: 
                    Provide a comprehensive overview of the industry, including its size, key players, products/services, and market segments.

                    2. Industry Trends:
                    Analyze the latest trends shaping the industry, such as technological advancements, regulatory changes, and shifts in consumer behavior.

                    3. Competitive Landscape:
                    Assess the competitive dynamics within the industry, including market share, competitive strategies, and potential disruptors.

                    4. Risk Analysis:
                    Identify and evaluate the significant risks and challenges faced by the industry, such as economic factors, geopolitical tensions, and cybersecurity threats.

                    5. Growth Opportunities:
                    Highlight potential growth opportunities within the industry, such as new markets, product innovations, or strategic partnerships.

                    6. Future Outlook and Recommendations:
                    Based on your analysis, provide a future outlook for the industry and offer actionable recommendations for companies operating within the sector.
                    
                    After completing each round of tasks, you need to combine previous recommendations (including your own previous recommendations and recommendations from other agents), and provide recommendations for the {company} after the current task is completed (i.e., buy, hold, or sell), along with the confidence level for each recommendation, such as buy: 60%, hold: 20%, sell: 20%, and provide a brief reason for each confidence level.
                    
                    {tip_section()}, {encourage_section()}
                """
            ),
            expected_output="Full analysis report in bullet points",
            async_execution=False,
            agent=agent,
            output_file="./output/financial_industry_analysis_report.md",
        )

    def company_stock_news_analysis_task(self, agent, query):
        return Task(
            description=dedent(
                f"""\
                    Fulfill your responsibilities by either incorporating the user's query or following requests from your manager or colleagues. Your responsibilities are as follows:
                    Conduct a comprehensive microeconomic financial analysis for a specific company or stock. The analysis should cover the following key aspects:
                    1. Company Overview:
                    Provide an overview of the company, including its business model, product/service offerings, target markets, and competitive positioning.

                    2. Financial Performance Analysis:
                    Analyze the company's recent financial performance, including revenue, profitability, cash flow, and key financial ratios. Identify trends and drivers behind the performance.

                    3. News and Events Impact:
                    Evaluate the impact of recent news, events, and announcements on the company's stock price and market perception. Consider factors such as product launches, acquisitions, regulatory changes, and industry developments.

                    4. Competitive Landscape:
                    Assess the competitive environment in which the company operates, including key competitors, their strengths and weaknesses, and potential threats or opportunities.

                    5. Risk Analysis:
                    Identify and evaluate the significant risks and challenges faced by the company, such as economic factors, regulatory changes, supply chain disruptions, or cybersecurity threats.

                    6. Future Outlook and Recommendations:
                    Based on your analysis, provide a future outlook for the company and its stock performance. Offer actionable recommendations for investors, such as buy, sell, or hold recommendations, and potential entry/exit points.

                    here is the user query: {query}

                    {tip_section()}, {encourage_section()}
                """
            ),
            expected_output="Full analysis report in bullet points",
            async_execution=False,
            agent=agent,
            output_file="./output/company_stock_news_analysis_report.md",
        )

    def behavioral_financial_analysis_task(self, agent, company):
        return Task(
            description=dedent(
                f"""\
                    Conduct a behavioral finance analysis for {company} stock, incorporating data from user social networks (comments, posts, etc.) related to the {company}. The analysis should cover the following aspects:
                    
                    1. Sentiment Analysis
                    2. Behavioral Biases Identification
                    3. Market Overreaction/Underreaction
                    4. Psychological Factors
                    5. Contrarian Opportunities
                    6. Recommendations
                    
                    After completing each round of tasks, you need to combine previous recommendations (including your own and other agents), and provide recommendations for the {company} stock after the current task is completed (i.e., buy, hold, or sell), along with the confidence level for each recommendation, such as buy: 60%, hold: 20%, sell: 20%, and provide a brief reason for each confidence level.
                    
                    {tip_section()}, {encourage_section()}
                """
            ),
            expected_output="A brief, focused, and neatly formatted analysis report containing the mentioned key points, and providing recommendations for 'sell', 'buy', and 'hold' along with confidence levels and reasons at the end.",
            output_pydantic=Output,
            async_execution=False,
            agent=agent,
            output_file=f"./output/behavioral_financial_analysis_{company}_{time.time()}.md",
        )

    def sentiment_analysis_task(self, agent, company):
        return Task(
            description=dedent(
                f"""\
                    Conduct a comprehensive sentiment analysis on {company} stock. The analysis should cover the following aspects:

                    1. Sentiment Categorization
                    2. Sentiment Trends and Patterns
                    3. Key Opinion Leaders and Influencers
                    4. Market Sentiment Analysis
                    5. Recommendations and Insights

                    After completing each round of tasks, you need to combine previous recommendations (including your own and other agents), and provide recommendations for the {company} stock after the current task is completed (i.e., buy, hold, or sell), along with the confidence level for each recommendation, such as buy: 60%, hold: 20%, sell: 20%, and provide a brief reason for each confidence level.
                    
                    {tip_section()}, {encourage_section()}
                """
            ),
            expected_output="A brief, focused, and neatly formatted analysis report containing the mentioned key points, and providing recommendations for 'sell', 'buy', and 'hold' along with confidence levels and reasons at the end.",
            output_pydantic=Output,
            async_execution=False,
            agent=agent,
            output_file=f"./output/sentiment_analysis_{company}_{time.time()}.md",
        )

    def competitor_analysis_task(self, agent, query):
        return Task(
            description=dedent(
                f"""\
                    Fulfill your responsibilities by either incorporating the user's query or following requests from your manager or colleagues. Your responsibilities are as follows:
                    Based on the user's request, identify specific stocks or companies, then conduct a comprehensive competitor analysis for those entities. The analysis should cover the following key aspects in detail:
                    1. Company Overview:
                    Provide an in-depth overview of the target company's business model, product/service offerings, target markets, and competitive positioning.

                    2. Competitor Identification:
                    Identify the key direct and indirect competitors operating in the same industry or market segment as the target company.

                    3. Competitive Landscape:
                    Analyze the competitive landscape, including market share, pricing strategies, distribution channels, and marketing efforts of the competitors.

                    4. Strengths and Weaknesses Analysis:
                    Conduct a comparative analysis of the strengths and weaknesses of the target company and its competitors. Evaluate factors such as product quality, pricing, customer service, brand reputation, and innovation.

                    5. Growth Strategies:
                    Assess the growth strategies employed by the competitors, such as new product launches, acquisitions, geographic expansion, or partnerships.

                    6. Future Outlook and Recommendations:
                    Based on your analysis, provide a future outlook for the target company's position in the competitive landscape. Offer actionable recommendations for the company to maintain or improve its competitive position.

                    here is the user query: {query}

                    {tip_section()}, {encourage_section()}
                """
            ),
            expected_output="Full analysis report in bullet points",
            async_execution=False,
            agent=agent,
            output_file="./output/competitor_analysis_report.md",
        )

    def valuation_analysis_task(self, agent, query):
        return Task(
            description=dedent(
                f"""\
                    Fulfill your responsibilities by either incorporating the user's query or following requests from your manager or colleagues. Your responsibilities are as follows:
                    
                    Conduct a detailed valuation analysis of the specific stocks or companies mentioned therein.
                    
                    here is the user query: {query}
                    
                    {tip_section()}, {encourage_section()}
                """
            ),
            expected_output=dedent(
                """\
                    A detailed summary report that adeptly utilizes list format to present various viewpoints. It may include prompts or bold font for key sections.
                """
            ),
            async_execution=False,
            agent=agent,
            output_file="./output/valuation_analysis_report.md",
        )

    def risk_factor_analysis_task(self, agent, query):
        return Task(
            description=dedent(
                f"""\
                    Fulfill your responsibilities by either incorporating the user's query or following requests from your manager or colleagues. Your responsibilities are as follows:
                    
                    Combined with the user's query, perform risk factor analysis on the specific stocks or companies mentioned therein.
                    
                    here is the user query: {query}
                    
                    {tip_section()}, {encourage_section()}
                """
            ),
            expected_output=dedent(
                """\
                    A detailed summary report that adeptly utilizes list format to present various viewpoints. It may include prompts or bold font for key sections.
                """
            ),
            async_execution=False,
            agent=agent,
            output_file="./output/risk_factor_analysis_report.md",
        )

    def investment_advice_task(self, agent, query):
        return Task(
            description=dedent(
                f"""\
                    Fulfill your responsibilities by either incorporating the user's query or following requests from your manager or colleagues. Your responsibilities are as follows:
                    
                    Combine the user query and the output report of other tasks to infer investment recommendations in detail and give a detailed investment report.
                    
                    here is the user query: {query}
                    
                    {tip_section()}, {encourage_section()}
                """
            ),
            expected_output=dedent(
                """\
                    A detailed summary report that adeptly utilizes list format to present various viewpoints. It may include prompts or bold font for key sections.
                """
            ),
            async_execution=False,
            agent=agent,
            output_file="./output/investment_advice_report.md",
        )

    def report_coordination_and_writing_task(self, agent, query):
        return Task(
            description=dedent(
                f"""\
                    Fulfill your responsibilities by either incorporating the user's query or following requests from your manager or colleagues. Your responsibilities are as follows:
                    
                    Using the insights provided by other analysts or agents, please craft an expertly styled report that is targeted towards the investor community. Make sure to also include the long-term implications insights that your co-worker has shared.
                    
                    Please ensure that the report is written in a professional tone and style. Write in a format and style worthy to be published in the wall street journal.
                    
                    here is the user query: {query}
                    
                    {tip_section()}, {encourage_section()}
                """
            ),
            expected_output=dedent(
                """\
                    Please ensure that the report is written in a professional tone and style. Write in a format and style worthy to be published in the wall street journal.        
                """
            ),
            agent=agent,
            output_file="./output/financial_analysis_report.md",
        )

    def market_trend_analysis_task(self, agent, query):
        return Task(
            description=dedent(
            f"""\
                Fulfill your responsibilities by either incorporating the user's query or following requests from your manager or colleagues. Your responsibilities are as follows:
                Utilizing the get_market_trend tool, conduct a comprehensive analysis of current trends in various market sectors. The analysis should cover the following key aspects:
                1. Market Overview:
                Provide an overview of the current state of the overall market, including major indices, trading volumes, and market sentiment.

                2. Sector Performance:
                Analyze the performance of different market sectors, such as technology, healthcare, energy, finance, and consumer goods. Identify the top-performing and underperforming sectors.

                3. Trend Identification:
                Identify emerging trends within each sector, such as new technologies, regulatory changes, consumer preferences, or macroeconomic factors driving the trends.

                4. Investment Opportunities:
                Based on the identified trends, highlight potential investment opportunities in specific stocks, sectors, or industries that are well-positioned to benefit from the trends.

                5. Risk Analysis:
                Identify potential risks associated with the current market trends, such as geopolitical tensions, economic uncertainties, or industry-specific challenges.

                6. Investment Strategy Recommendations:
                Provide actionable recommendations for investment strategies, such as sector rotation, portfolio diversification, or specific stock picks, based on the market trend analysis.
                
                here is the user query: {query}
                
                {tip_section()}, {encourage_section()}
            """
            ),
            expected_output="Full analysis report in bullet points",
            agent=agent,
            output_file="./output/market_trend_analysis_report.md",
        )

    def sec_filings_analysis_task(self, agent, query):
        return Task(
            description=dedent(
            f"""\
                Fulfill your responsibilities by either incorporating the user's query or following requests from your manager or colleagues. Your responsibilities are as follows:
                Leverage advanced analytical tools to review and analyze the latest SEC filings of the specified company. The analysis should cover the following key aspects:
                1. Financial Metrics:
                Extract and analyze essential financial metrics from the filings, such as revenue, profitability, cash flows, and key financial ratios. Identify trends and assess the company's financial health.

                2. Risk Factors:
                Identify and evaluate the significant risk factors disclosed in the Risk Factors section of the filings, including operational, financial, legal, and competitive risks.

                3. Management's Discussion and Analysis (MD&A):
                Interpret and summarize the key points from the MD&A section, including management's assessment of the company's performance, strategies, and future outlook.

                4. Competitive Landscape:
                Analyze the competitive landscape and the company's position within its industry, based on the information provided in the filings.

                5. Growth Opportunities:
                Highlight potential growth opportunities for the company, such as new product launches, market expansions, or strategic partnerships, based on the insights from the filings.

                6. Investment Recommendations:
                Provide actionable investment recommendations, such as buy, sell, or hold, based on the comprehensive analysis of the company's SEC filings.
                The analysis should be unbiased, factual, and supported by evidence from the filings. Clearly differentiate between factual statements from the filings and your own interpretations or opinions.
                
                here is the user query: {query}
                
                {tip_section()}, {encourage_section()}
            """
            ),
            expected_output="Full analysis report in bullet points",
            agent=agent,
            output_file="./output/sec_filings_analysis_report.md",
        )

    def earnings_call_analysis_task(self, agent, query):
        return Task(
            description=dedent(
            f"""
                Fulfill your responsibilities by either incorporating the user's query or following requests from your manager or colleagues. Your responsibilities are as follows:
                Process and analyze the latest earnings call transcript of the specified company. The analysis should cover the following key aspects:
                1. Financial Performance:
                Extract and analyze the company's financial performance metrics discussed during the earnings call, such as revenue, earnings, margins, and cash flows. Identify trends and compare against analyst expectations.

                2. Executive Sentiment:
                Assess the overall sentiment and tone of the executives during the call. Identify key positive and negative sentiments expressed regarding the company's performance, strategies, and future outlook.

                3. Strategic Initiatives:
                Highlight any strategic initiatives, product launches, or growth plans mentioned during the call, and analyze their potential impact on the company's future performance.

                4. Competitive Landscape:
                Evaluate the discussion around the competitive landscape, including the company's position relative to its competitors, any competitive threats or opportunities mentioned, and strategies to address them.

                5. Risk Factors:
                Identify any significant risk factors or challenges discussed during the call, such as regulatory changes, supply chain issues, or macroeconomic factors that may impact the company's operations.

                6. Guidance and Outlook:
                Analyze the company's guidance and outlook for future financial performance, including any revisions to previous guidance or long-term targets discussed during the call.
                
                here is the user query: {query}
                
                {tip_section()}, {encourage_section()}
            """
            ),
            expected_output="Full analysis report in bullet points",
            agent=agent,
            output_file="./output/earnings_call_analysis_report.md",
        )

    def financial_statements_task(self, agent, query):
        return Task(
            description=dedent(
            f"""
                Fulfill your responsibilities by either incorporating the user's query or following requests from your manager or colleagues. Your responsibilities are as follows:
                Identify and retrieve the latest Income Statement, Balance Sheet, Cash Flow Statement, Revenue, and Quote Data for the specified company. Conduct a comprehensive analysis of these financial statements and data, covering the following key aspects:
                1. Income Statement Analysis:
                Analyze the company's revenue streams, cost structure, and profitability. Assess the trends in revenue growth, gross margins, operating margins, and net income over recent periods.

                2. Balance Sheet Analysis: 
                Evaluate the company's asset structure, including current and non-current assets, as well as its capital structure, encompassing liabilities and shareholders' equity. Assess the company's financial stability and leverage ratios.

                3. Cash Flow Analysis:
                Analyze the company's cash inflows and outflows from operating, investing, and financing activities. Assess the company's liquidity, cash management practices, and ability to generate positive cash flows.

                4. Revenue Analysis:
                Examine the company's revenue data, including revenue sources, geographic distribution, and revenue growth trends over time.

                5. Quote Data Analysis:
                Analyze the company's stock price data, including historical price movements, trading volume, and any significant events or announcements that may have impacted the stock price.

                6. Financial Ratios and Trends:
                Calculate and interpret key financial ratios, such as liquidity, profitability, leverage, and efficiency ratios. Identify and analyze trends in the company's financial performance, asset structure, and cash flows over recent periods, highlighting any significant changes or potential red flags.
                
                here is the user query: {query}
                
                {tip_section()}, {encourage_section()}
            """
            ),
            expected_output="Full analysis report in bullet points",
            agent=agent,
            output_file="./output/financial_statements_report.md",
        )
    
    def fomc_analysis_task(self, agent, query):
        return Task(
            description=dedent(
            f"""
                Fulfill your responsibilities by either incorporating the user's query or following requests from your manager or colleagues. Your responsibilities are as follows:
                Conduct an in-depth analysis of the latest Federal Open Market Committee (FOMC) statement or meeting minutes. The analysis should cover the following key aspects:
                1. Economic Assessment:
                Analyze the FOMC's assessment of current economic conditions, including factors such as GDP growth, employment, inflation, and overall economic health.

                2. Monetary Policy Stance:
                Evaluate the FOMC's monetary policy stance, including any changes to the federal funds rate, balance sheet operations, or forward guidance on future policy actions.

                3. Rationale and Justification:
                Interpret the rationale and justification provided by the FOMC for their policy decisions, considering factors such as inflation targets, employment objectives, and economic risks.

                4. Dissenting Views:
                Identify and analyze any dissenting views or opposing perspectives expressed by FOMC members, highlighting potential areas of disagreement or concern.

                5. Market Implications:
                Assess the potential implications of the FOMC's decisions and statements on financial markets, including impacts on interest rates, stock markets, and the overall investment landscape.

                6. Future Outlook:
                Provide insights into the FOMC's likely future policy actions based on their stated economic projections, risk assessments, and policy guidance.
            
                here is the user query: {query}
                
                {tip_section()}, {encourage_section()}
            """),
            expected_output="Full analysis report in bullet points",
            agent=agent,
            output_file="./output/fomc_analysis_report.md",
        )
    
    def senior_research_task(self, agent, query):
        return Task(
            description=
            dedent(
            f"""
                Fulfill your responsibilities by either incorporating the user's query or following requests from your manager or colleagues. Your responsibilities are as follows:
                
                please conduct a comprehensive analysis of specific company latest SEC 10-K or 10-Q filing. The analysis should include the following key points:

                Business Overview: Briefly describe company's business model, its products and services, and its target market.

                Risk Factors: Identify and discuss the major risk factors that company has disclosed in its 10-K or 10-Q filing.

                Management's Discussion and Analysis (MD&A): Summarize the key points from the MD&A section, including any significant changes in operations, financial condition, or liquidity.

                Competitive Landscape: Discuss company's competitive position in its industry and how it compares to its major competitors.

                Future Outlook: Based on the information in the 10-K or 10-Q filing and your analysis, provide a brief outlook on company's future performance.

                Please ensure that all information is sourced from company's latest SEC 10-K or 10-Q filing and that the analysis is unbiased and factual.
            
                here is the user query: {query}
                
                {tip_section()}, {encourage_section()}
            """
            ),
            expected_output="Full analysis report in bullet points",
            agent=agent,
        )
    
    def visionary_task(self, agent, query):
        return Task(
            description=dedent(
            f"""
                Fulfill your responsibilities by either incorporating the user's query or following requests from your manager or colleagues. Your responsibilities are as follows:
                
                Using the insights provided by the Senior Research Analyst, think through deeply the future implications of the points that are made. Consider the following questions as you craft your response:

                What are the current limitations or pain points that this technology mentioned in the Senior Research Analyst report could address?

                How might this technology disrupt traditional business models and create new opportunities for innovation?

                What are the potential risks and challenges associated with the adoption of this technology, and how might they be mitigated?

                How could this technology impact consumers, employees, and society as a whole?

                What are the long-term implications of this technology, and how might it shape the future of the industry?

                Provide a detailed analysis of the technology's potential impact, backed by relevant examples, data, and insights. Your response should demonstrate your ability to think strategically, anticipate future trends, and articulate complex ideas in a clear and compelling manner.    

                here is the user query: {query}
                
                {tip_section()}, {encourage_section()}
            """
            ),
            expected_output="Analysis report with deeper insights in implications",
            agent=agent,
        )
        
    def writer_task(self, agent, query):
        return Task(
            description=
            f"""\
                Fulfill your responsibilities by either incorporating the user's query or following requests from your manager or colleagues. Your responsibilities are as follows:
            
                Using the insights provided by the Senior Research Analyst and Visionary,please craft an expertly styled report that is targeted towards the investor community. Make sure to also include the long-term implications insights that your co-worker, Visionary, has shared.  
                
                Please ensure that the report is written in a professional tone and style, and that all information is sourced from company's latest SEC 10-K or 10-Q filing. Write in a format and style worthy to be published in the wall street journal.
            
                here is the user query: {query}
                
                {tip_section()}, {encourage_section()}
            """,
            expected_output="A detailed comprehensive report on specific company that expertly presents the research done by your co-worker, Senior Research Analyst and Visionary",
            agent=agent,
        )
    
    def final_recommendation_task(self, agent, company):
        return Task(
            description=
            f"""\
                Gather and grasp the confidence level changes in recommendations from each agent for each round of tasks for {company} stock. 
                Carefully consider the reasons for their changes, focusing on the confidence levels of the last few 
                recommendations. Delve into the financial and psychological principles behind all the collected data, 
                and provide your recommendations (sell, buy, hold) along with confidence levels and reasons.
            """,
            expected_output=f"A detailed, comprehensive, and neatly formatted stock recommendation report on {company} stock providing the final confidence levels for each recommendation (buy, sell, hold), along with compelling reasons.",
            output_pydantic=Output,
            async_execution=False,
            agent=agent,
            output_file=f"./output/final_recommendation_{company}_{time.time()}.md",
        )

