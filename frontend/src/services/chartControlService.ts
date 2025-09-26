/**
 * Chart Control Service
 * Processes agent commands to control TradingView Lightweight Charts
 */

import { marketDataService, SymbolSearchResult } from './marketDataService';

export interface ChartCommand {
  type: 'symbol' | 'timeframe' | 'indicator' | 'zoom' | 'scroll' | 'style' | 'reset' | 'crosshair' | 'drawing';
  value: any;
  metadata?: {
    assetType?: 'stock' | 'crypto';
    [key: string]: any;
  };
  timestamp?: number;
}

export interface ChartControlCallbacks {
  onSymbolChange?: (symbol: string, metadata?: { assetType?: 'stock' | 'crypto' }) => void;
  onTimeframeChange?: (timeframe: string) => void;
  onIndicatorToggle?: (indicator: string, enabled: boolean) => void;
  onZoomChange?: (level: number) => void;
  onScrollToTime?: (time: number) => void;
  onStyleChange?: (style: 'candles' | 'line' | 'area') => void;
  onPatternHighlight?: (pattern: string, info?: { description?: string; indicator?: string }) => void;
  onCommandExecuted?: (command: ChartCommand, success: boolean, message: string) => void;
  onCommandError?: (error: string) => void;
}

class ChartControlService {
  private callbacks: ChartControlCallbacks = {};
  private currentSymbol: string = 'TSLA';
  private chartRef: any = null;
  
  // Company name to ticker mapping (200+ companies)
  private companyToTicker: { [key: string]: string } = {
    // Tech Giants
    'NVIDIA': 'NVDA',
    'APPLE': 'AAPL',
    'MICROSOFT': 'MSFT',
    'GOOGLE': 'GOOGL',
    'ALPHABET': 'GOOGL',
    'AMAZON': 'AMZN',
    'META': 'META',
    'FACEBOOK': 'META',
    'NETFLIX': 'NFLX',
    'TESLA': 'TSLA',
    'INTEL': 'INTC',
    'AMD': 'AMD',
    'ORACLE': 'ORCL',
    'SALESFORCE': 'CRM',
    'ADOBE': 'ADBE',
    'CISCO': 'CSCO',
    'IBM': 'IBM',
    'BROADCOM': 'AVGO',
    'QUALCOMM': 'QCOM',
    'TEXAS INSTRUMENTS': 'TXN',
    'PAYPAL': 'PYPL',
    'SPOTIFY': 'SPOT',
    'SQUARE': 'SQ',
    'BLOCK': 'SQ',
    'SHOPIFY': 'SHOP',
    'UBER': 'UBER',
    'LYFT': 'LYFT',
    'AIRBNB': 'ABNB',
    'ZOOM': 'ZM',
    'DOCUSIGN': 'DOCU',
    'PALANTIR': 'PLTR',
    'SNOWFLAKE': 'SNOW',
    'DATABRICKS': 'DBX',
    'CLOUDFLARE': 'NET',
    'CROWDSTRIKE': 'CRWD',
    'OKTA': 'OKTA',
    'TWILIO': 'TWLO',
    'SLACK': 'WORK',
    'ATLASSIAN': 'TEAM',
    'ASANA': 'ASAN',
    'MONDAY': 'MNDY',
    'UNITY': 'U',
    'ROBLOX': 'RBLX',
    'COINBASE': 'COIN',
    'ROBINHOOD': 'HOOD',
    'DRAFTKINGS': 'DKNG',
    'PINTEREST': 'PINS',
    'SNAP': 'SNAP',
    'SNAPCHAT': 'SNAP',
    'TWITTER': 'TWTR',
    'X': 'TWTR',
    
    // Financial
    'JPMORGAN': 'JPM',
    'JP MORGAN': 'JPM',
    'CHASE': 'JPM',
    'BANK OF AMERICA': 'BAC',
    'WELLS FARGO': 'WFC',
    'GOLDMAN': 'GS',
    'GOLDMAN SACHS': 'GS',
    'MORGAN STANLEY': 'MS',
    'CITIGROUP': 'C',
    'CITI': 'C',
    'AMERICAN EXPRESS': 'AXP',
    'AMEX': 'AXP',
    'BERKSHIRE': 'BRK.B',
    'BERKSHIRE HATHAWAY': 'BRK.B',
    'BLACKROCK': 'BLK',
    'CHARLES SCHWAB': 'SCHW',
    'SCHWAB': 'SCHW',
    'VISA': 'V',
    'MASTERCARD': 'MA',
    'FIDELITY': 'FNF',
    
    // Retail & Consumer
    'WALMART': 'WMT',
    'TARGET': 'TGT',
    'COSTCO': 'COST',
    'HOME DEPOT': 'HD',
    'LOWES': 'LOW',
    'NIKE': 'NKE',
    'ADIDAS': 'ADDYY',
    'STARBUCKS': 'SBUX',
    'MCDONALDS': 'MCD',
    'COCA COLA': 'KO',
    'COKE': 'KO',
    'PEPSI': 'PEP',
    'PEPSICO': 'PEP',
    'DISNEY': 'DIS',
    'WARNER': 'WBD',
    'PARAMOUNT': 'PARA',
    'COMCAST': 'CMCSA',
    'VERIZON': 'VZ',
    'AT&T': 'T',
    'ATT': 'T',
    'T-MOBILE': 'TMUS',
    'TMOBILE': 'TMUS',
    
    // Healthcare & Pharma
    'JOHNSON & JOHNSON': 'JNJ',
    'JNJ': 'JNJ',
    'PFIZER': 'PFE',
    'MODERNA': 'MRNA',
    'ABBVIE': 'ABBV',
    'MERCK': 'MRK',
    'LILLY': 'LLY',
    'ELI LILLY': 'LLY',
    'BRISTOL': 'BMY',
    'BRISTOL MYERS': 'BMY',
    'ASTRAZENECA': 'AZN',
    'NOVARTIS': 'NVS',
    'ROCHE': 'RHHBY',
    'ABBOTT': 'ABT',
    'MEDTRONIC': 'MDT',
    'CVS': 'CVS',
    'WALGREENS': 'WBA',
    'UNITEDHEALTH': 'UNH',
    'ANTHEM': 'ANTM',
    'CIGNA': 'CI',
    'HUMANA': 'HUM',
    
    // Automotive
    'FORD': 'F',
    'GENERAL MOTORS': 'GM',
    'GM': 'GM',
    'TOYOTA': 'TM',
    'HONDA': 'HMC',
    'VOLKSWAGEN': 'VWAGY',
    'VW': 'VWAGY',
    'BMW': 'BMWYY',
    'MERCEDES': 'DMLRY',
    'FERRARI': 'RACE',
    'RIVIAN': 'RIVN',
    'LUCID': 'LCID',
    'NIO': 'NIO',
    'XPENG': 'XPEV',
    'LI AUTO': 'LI',
    
    // Airlines & Travel
    'BOEING': 'BA',
    'AIRBUS': 'EADSY',
    'DELTA': 'DAL',
    'UNITED': 'UAL',
    'AMERICAN AIRLINES': 'AAL',
    'SOUTHWEST': 'LUV',
    'JETBLUE': 'JBLU',
    'SPIRIT': 'SAVE',
    'ALASKA': 'ALK',
    'BOOKING': 'BKNG',
    'EXPEDIA': 'EXPE',
    'MARRIOTT': 'MAR',
    'HILTON': 'HLT',
    'HYATT': 'H',
    'CARNIVAL': 'CCL',
    'ROYAL CARIBBEAN': 'RCL',
    'NORWEGIAN': 'NCLH',
    
    // Energy & Commodities
    'EXXON': 'XOM',
    'EXXONMOBIL': 'XOM',
    'CHEVRON': 'CVX',
    'SHELL': 'SHEL',
    'BP': 'BP',
    'CONOCOPHILLIPS': 'COP',
    'MARATHON': 'MRO',
    'OCCIDENTAL': 'OXY',
    'SCHLUMBERGER': 'SLB',
    'HALLIBURTON': 'HAL',
    
    // International
    'ALIBABA': 'BABA',
    'TENCENT': 'TCEHY',
    'BAIDU': 'BIDU',
    'JD': 'JD',
    'PINDUODUO': 'PDD',
    'MEITUAN': 'MPNGY',
    'BYTEDANCE': 'BDNCE',
    'XIAOMI': 'XIACF',
    'BYD': 'BYDDY',
    'SAMSUNG': 'SSNLF',
    'SONY': 'SONY',
    'NINTENDO': 'NTDOY',
    'SOFTBANK': 'SFTBY',
    'RAKUTEN': 'RKUNY',
    'NESTLE': 'NSRGY',
    'UNILEVER': 'UL',
    'LVMH': 'LVMUY',
    'ASML': 'ASML',
    'TSMC': 'TSM',
    'TAIWAN SEMICONDUCTOR': 'TSM',
    'INFOSYS': 'INFY',
    'WIPRO': 'WIT',
    'TATA': 'TTM',
    'RELIANCE': 'RELI',
    'ARAMCO': 'ARMCO',
    'PETROBRAS': 'PBR',
    'VALE': 'VALE',
    'MERCADOLIBRE': 'MELI',
    'NUBANK': 'NU',
    'STONE': 'STNE',
    'PAGSEGURO': 'PAGS',
    
    // ETFs & Indices
    'SPY': 'SPY',
    'S&P': 'SPY',
    'S&P 500': 'SPY',
    'QQQ': 'QQQ',
    'NASDAQ': 'QQQ',
    'DIA': 'DIA',
    'DOW': 'DIA',
    'DOW JONES': 'DIA',
    'IWM': 'IWM',
    'RUSSELL': 'IWM',
    'VTI': 'VTI',
    'VOO': 'VOO',
    'VANGUARD': 'VTI',
    'ARK': 'ARKK',
    'ARKK': 'ARKK',
    'ARKG': 'ARKG',
    'ARKQ': 'ARKQ',
    'ARKW': 'ARKW',
    'GLD': 'GLD',
    'GOLD': 'GLD',
    'SLV': 'SLV',
    'SILVER': 'SLV',
    'USO': 'USO',
    'OIL': 'USO'
  };
  
  // Cryptocurrency to ticker mapping (supports CoinGecko, Yahoo, and CoinMarketCap)
  private cryptoToTicker: { [key: string]: { gecko: string; yahoo: string; cmc?: string } } = {
    // Major cryptocurrencies
    'BITCOIN': { gecko: 'bitcoin', yahoo: 'BTC-USD', cmc: 'BTC' },
    'BTC': { gecko: 'bitcoin', yahoo: 'BTC-USD', cmc: 'BTC' },
    'ETHEREUM': { gecko: 'ethereum', yahoo: 'ETH-USD', cmc: 'ETH' },
    'ETH': { gecko: 'ethereum', yahoo: 'ETH-USD', cmc: 'ETH' },
    'BINANCE': { gecko: 'binancecoin', yahoo: 'BNB-USD', cmc: 'BNB' },
    'BNB': { gecko: 'binancecoin', yahoo: 'BNB-USD', cmc: 'BNB' },
    'CARDANO': { gecko: 'cardano', yahoo: 'ADA-USD', cmc: 'ADA' },
    'ADA': { gecko: 'cardano', yahoo: 'ADA-USD', cmc: 'ADA' },
    'SOLANA': { gecko: 'solana', yahoo: 'SOL-USD', cmc: 'SOL' },
    'SOL': { gecko: 'solana', yahoo: 'SOL-USD', cmc: 'SOL' },
    'XRP': { gecko: 'ripple', yahoo: 'XRP-USD', cmc: 'XRP' },
    'RIPPLE': { gecko: 'ripple', yahoo: 'XRP-USD', cmc: 'XRP' },
    'DOGECOIN': { gecko: 'dogecoin', yahoo: 'DOGE-USD', cmc: 'DOGE' },
    'DOGE': { gecko: 'dogecoin', yahoo: 'DOGE-USD', cmc: 'DOGE' },
    'POLYGON': { gecko: 'matic-network', yahoo: 'MATIC-USD', cmc: 'MATIC' },
    'MATIC': { gecko: 'matic-network', yahoo: 'MATIC-USD', cmc: 'MATIC' },
    'POLKADOT': { gecko: 'polkadot', yahoo: 'DOT-USD', cmc: 'DOT' },
    'DOT': { gecko: 'polkadot', yahoo: 'DOT-USD', cmc: 'DOT' },
    'CHAINLINK': { gecko: 'chainlink', yahoo: 'LINK-USD', cmc: 'LINK' },
    'LINK': { gecko: 'chainlink', yahoo: 'LINK-USD', cmc: 'LINK' },
    'AVALANCHE': { gecko: 'avalanche-2', yahoo: 'AVAX-USD', cmc: 'AVAX' },
    'AVAX': { gecko: 'avalanche-2', yahoo: 'AVAX-USD', cmc: 'AVAX' },
    'UNISWAP': { gecko: 'uniswap', yahoo: 'UNI-USD', cmc: 'UNI' },
    'UNI': { gecko: 'uniswap', yahoo: 'UNI-USD', cmc: 'UNI' },
    'LITECOIN': { gecko: 'litecoin', yahoo: 'LTC-USD', cmc: 'LTC' },
    'LTC': { gecko: 'litecoin', yahoo: 'LTC-USD', cmc: 'LTC' },
    'COSMOS': { gecko: 'cosmos', yahoo: 'ATOM-USD', cmc: 'ATOM' },
    'ATOM': { gecko: 'cosmos', yahoo: 'ATOM-USD', cmc: 'ATOM' },
    'STELLAR': { gecko: 'stellar', yahoo: 'XLM-USD', cmc: 'XLM' },
    'XLM': { gecko: 'stellar', yahoo: 'XLM-USD', cmc: 'XLM' },
    'MONERO': { gecko: 'monero', yahoo: 'XMR-USD', cmc: 'XMR' },
    'XMR': { gecko: 'monero', yahoo: 'XMR-USD', cmc: 'XMR' },
    'TRON': { gecko: 'tron', yahoo: 'TRX-USD', cmc: 'TRX' },
    'TRX': { gecko: 'tron', yahoo: 'TRX-USD', cmc: 'TRX' },
    'ETHEREUM CLASSIC': { gecko: 'ethereum-classic', yahoo: 'ETC-USD', cmc: 'ETC' },
    'ETC': { gecko: 'ethereum-classic', yahoo: 'ETC-USD', cmc: 'ETC' },
    'FILECOIN': { gecko: 'filecoin', yahoo: 'FIL-USD', cmc: 'FIL' },
    'FIL': { gecko: 'filecoin', yahoo: 'FIL-USD', cmc: 'FIL' },
    'AAVE': { gecko: 'aave', yahoo: 'AAVE-USD', cmc: 'AAVE' },
    'COMPOUND': { gecko: 'compound-governance-token', yahoo: 'COMP-USD', cmc: 'COMP' },
    'COMP': { gecko: 'compound-governance-token', yahoo: 'COMP-USD', cmc: 'COMP' },
    'MAKER': { gecko: 'maker', yahoo: 'MKR-USD', cmc: 'MKR' },
    'MKR': { gecko: 'maker', yahoo: 'MKR-USD', cmc: 'MKR' },
    'SUSHI': { gecko: 'sushi', yahoo: 'SUSHI-USD', cmc: 'SUSHI' },
    'SUSHISWAP': { gecko: 'sushi', yahoo: 'SUSHI-USD', cmc: 'SUSHI' },
    'CURVE': { gecko: 'curve-dao-token', yahoo: 'CRV-USD', cmc: 'CRV' },
    'CRV': { gecko: 'curve-dao-token', yahoo: 'CRV-USD', cmc: 'CRV' },
    'FANTOM': { gecko: 'fantom', yahoo: 'FTM-USD', cmc: 'FTM' },
    'FTM': { gecko: 'fantom', yahoo: 'FTM-USD', cmc: 'FTM' },
    'ALGORAND': { gecko: 'algorand', yahoo: 'ALGO-USD', cmc: 'ALGO' },
    'ALGO': { gecko: 'algorand', yahoo: 'ALGO-USD', cmc: 'ALGO' },
    'NEAR': { gecko: 'near', yahoo: 'NEAR-USD', cmc: 'NEAR' },
    'NEAR PROTOCOL': { gecko: 'near', yahoo: 'NEAR-USD', cmc: 'NEAR' },
    'FLOW': { gecko: 'flow', yahoo: 'FLOW-USD', cmc: 'FLOW' },
    'HEDERA': { gecko: 'hedera-hashgraph', yahoo: 'HBAR-USD', cmc: 'HBAR' },
    'HBAR': { gecko: 'hedera-hashgraph', yahoo: 'HBAR-USD', cmc: 'HBAR' },
    'INTERNET COMPUTER': { gecko: 'internet-computer', yahoo: 'ICP-USD', cmc: 'ICP' },
    'ICP': { gecko: 'internet-computer', yahoo: 'ICP-USD', cmc: 'ICP' },
    'THE SANDBOX': { gecko: 'the-sandbox', yahoo: 'SAND-USD', cmc: 'SAND' },
    'SAND': { gecko: 'the-sandbox', yahoo: 'SAND-USD', cmc: 'SAND' },
    'DECENTRALAND': { gecko: 'decentraland', yahoo: 'MANA-USD', cmc: 'MANA' },
    'MANA': { gecko: 'decentraland', yahoo: 'MANA-USD', cmc: 'MANA' },
    'AXIE': { gecko: 'axie-infinity', yahoo: 'AXS-USD', cmc: 'AXS' },
    'AXS': { gecko: 'axie-infinity', yahoo: 'AXS-USD', cmc: 'AXS' },
    'ENJIN': { gecko: 'enjincoin', yahoo: 'ENJ-USD', cmc: 'ENJ' },
    'ENJ': { gecko: 'enjincoin', yahoo: 'ENJ-USD', cmc: 'ENJ' },
    'GALA': { gecko: 'gala', yahoo: 'GALA-USD', cmc: 'GALA' },
    'THETA': { gecko: 'theta-token', yahoo: 'THETA-USD', cmc: 'THETA' },
    'VECHAIN': { gecko: 'vechain', yahoo: 'VET-USD', cmc: 'VET' },
    'VET': { gecko: 'vechain', yahoo: 'VET-USD', cmc: 'VET' },
    'ZILLIQA': { gecko: 'zilliqa', yahoo: 'ZIL-USD', cmc: 'ZIL' },
    'ZIL': { gecko: 'zilliqa', yahoo: 'ZIL-USD', cmc: 'ZIL' },
    'SHIBA': { gecko: 'shiba-inu', yahoo: 'SHIB-USD', cmc: 'SHIB' },
    'SHIB': { gecko: 'shiba-inu', yahoo: 'SHIB-USD', cmc: 'SHIB' },
    'SHIBA INU': { gecko: 'shiba-inu', yahoo: 'SHIB-USD', cmc: 'SHIB' },
    
    // Stablecoins
    'TETHER': { gecko: 'tether', yahoo: 'USDT-USD', cmc: 'USDT' },
    'USDT': { gecko: 'tether', yahoo: 'USDT-USD', cmc: 'USDT' },
    'USDC': { gecko: 'usd-coin', yahoo: 'USDC-USD', cmc: 'USDC' },
    'USD COIN': { gecko: 'usd-coin', yahoo: 'USDC-USD', cmc: 'USDC' },
    'BUSD': { gecko: 'binance-usd', yahoo: 'BUSD-USD', cmc: 'BUSD' },
    'DAI': { gecko: 'dai', yahoo: 'DAI-USD', cmc: 'DAI' },
    'FRAX': { gecko: 'frax', yahoo: 'FRAX-USD', cmc: 'FRAX' },
    'TUSD': { gecko: 'true-usd', yahoo: 'TUSD-USD', cmc: 'TUSD' },
    'PAX': { gecko: 'paxos-standard', yahoo: 'PAX-USD', cmc: 'PAX' },
    'PAXOS': { gecko: 'paxos-standard', yahoo: 'PAX-USD', cmc: 'PAX' }
  };
  
  // Symbol conflicts (symbols that exist as both stock and crypto)
  private symbolConflicts: { [key: string]: { stock: string; crypto: { gecko: string; yahoo: string; cmc?: string } } } = {
    'AMP': { stock: 'AMP', crypto: { gecko: 'amp-token', yahoo: 'AMP-USD', cmc: 'AMP' }},
    'ADA': { stock: 'ADA', crypto: { gecko: 'cardano', yahoo: 'ADA-USD', cmc: 'ADA' }},
    'LINK': { stock: 'LINK', crypto: { gecko: 'chainlink', yahoo: 'LINK-USD', cmc: 'LINK' }},
    'UNI': { stock: 'UNI', crypto: { gecko: 'uniswap', yahoo: 'UNI-USD', cmc: 'UNI' }},
    'DOT': { stock: 'DOT', crypto: { gecko: 'polkadot', yahoo: 'DOT-USD', cmc: 'DOT' }},
    'COMP': { stock: 'COMP', crypto: { gecko: 'compound-governance-token', yahoo: 'COMP-USD', cmc: 'COMP' }},
    'CRV': { stock: 'CRV', crypto: { gecko: 'curve-dao-token', yahoo: 'CRV-USD', cmc: 'CRV' }},
    'FLOW': { stock: 'FLOW', crypto: { gecko: 'flow', yahoo: 'FLOW-USD', cmc: 'FLOW' }},
    'SAND': { stock: 'SAND', crypto: { gecko: 'the-sandbox', yahoo: 'SAND-USD', cmc: 'SAND' }}
  };

  // Enhanced command patterns for parsing agent responses
  private commandPatterns = {
    // Symbol patterns - prioritize company names over generic matches
    symbol: /(?:CHART|SHOW|DISPLAY|SWITCH TO|CHANGE TO|LOAD|VIEW|PULL UP)[:\s]+([A-Z]{1,5}(?:-USD)?)|(?:show(?:ing)? (?:me |you )?|display(?:ing)?|load(?:ing)?|switch(?:ing)? to|change to|here(?:'s| is))?\s*(?:the )?(NVIDIA|APPLE|TESLA|MICROSOFT|AMAZON|GOOGLE|META|FACEBOOK|NETFLIX|[A-Z]{1,5})(?:'s)?\s*(?:chart|stock|ticker|price|data)?/i,
    
    // Timeframe patterns - support more variations
    timeframe: /(?:TIMEFRAME|TIME|PERIOD|RANGE|VIEW)[:\s]+(1D|5D|1W|2W|1M|3M|6M|1Y|2Y|5Y|YTD|ALL|MAX)|(?:show |display |set )?(one|1) ?(day|week|month|year)|(?:show |display |set )?(five|5) ?(days?|weeks?|months?|years?)|(?:year to date|ytd|all time|maximum)/i,
    
    // Indicator patterns - expanded list
    indicator: /(?:ADD|SHOW|HIDE|REMOVE|TOGGLE|DISPLAY)[:\s]+(MA|EMA|SMA|RSI|MACD|VOLUME|VOL|BOLLINGER|BB|VWAP|STOCHASTIC|ATR)|(?:add |show |display |toggle )?(moving average|exponential moving|rsi|macd|volume|bollinger bands?|vwap)/i,
    
    // Zoom patterns - more natural language
    zoom: /(?:ZOOM)[:\s]+(IN|OUT|\d+%?)|zoom ?(in|out)(?: ?(\d+))?%?|(?:closer|further|magnify|shrink)/i,
    
    // Scroll patterns - date navigation
    scroll: /(?:SCROLL|GO TO|NAVIGATE TO|JUMP TO)[:\s]+(\d{4}-\d{2}-\d{2}|\w+)|(?:go to |scroll to |jump to |show )?(yesterday|today|last week|last month|beginning|end)/i,
    
    // Style patterns - chart types
    style: /(?:STYLE|VIEW|TYPE|CHART TYPE)[:\s]+(CANDLES?|LINE|AREA|BARS?|HEIKIN|HOLLOW)|(?:switch to |change to |use )?(candlestick|candle|line|area|bar|heikin ashi|hollow candle)s?(?: chart)?/i,
    
    // Reset view pattern
    reset: /(?:RESET|FIT|AUTO)[:\s]*(VIEW|SCALE|ZOOM)?|reset (?:the )?(?:chart|view|zoom)|fit (?:to )?(?:screen|content)|auto ?scale/i,
    
    // Crosshair pattern
    crosshair: /(?:CROSSHAIR|CURSOR)[:\s]+(ON|OFF|TOGGLE)|(?:show|hide|toggle)(?: the)? crosshair/i
  };

  /**
   * Register callbacks for chart control events
   */
  registerCallbacks(callbacks: ChartControlCallbacks) {
    this.callbacks = { ...this.callbacks, ...callbacks };
  }

  /**
   * Set the chart reference for direct control
   */
  setChartRef(chart: any) {
    this.chartRef = chart;
  }

  /**
   * Detect asset type from context
   */
  private detectAssetType(response: string): 'stock' | 'crypto' | 'auto' {
    const cryptoKeywords = /crypto|coin|token|bitcoin|ethereum|blockchain|defi|web3|nft|mining|wallet|satoshi/i;
    const stockKeywords = /stock|share|equity|company|corporation|nasdaq|nyse|s&p|dow|earnings|dividend|ipo/i;
    
    if (cryptoKeywords.test(response)) return 'crypto';
    if (stockKeywords.test(response)) return 'stock';
    return 'auto';
  }
  
  /**
   * Validate if a string is likely a stock symbol
   */
  private isValidSymbol(symbol: string): boolean {
    if (!symbol || symbol.length < 1) return false;
    
    const upperSymbol = symbol.toUpperCase();
    
    // Valid patterns:
    // Stock: 1-5 uppercase letters
    // Crypto: XXX-USD, XXX-USDT, XXX-USDC, XXX-BTC, XXX-ETH
    // Special: BRK.A, BRK.B (Berkshire Hathaway)
    const validPatterns = [
      /^[A-Z]{1,5}$/,                                    // Stock symbols
      /^[A-Z]{2,5}-USD$/,                                // Crypto USD pairs
      /^[A-Z]{2,5}-(USDT|USDC|EUR|BTC|ETH)$/,          // Other crypto pairs
      /^BRK\.[AB]$/                                      // Berkshire special case
    ];
    
    return validPatterns.some(pattern => pattern.test(upperSymbol));
  }
  
  /**
   * Resolve symbol using Alpaca search API (semantic approach)
   */
  private async resolveSymbolWithSearch(query: string): Promise<{ symbol: string; type: 'stock' | 'crypto'; name?: string } | null> {
    try {
      console.log(`Searching for symbol with query: "${query}"`);
      
      // Use Alpaca search to find matching symbols
      const searchResponse = await marketDataService.searchSymbols(query, 5);
      
      if (searchResponse.results.length > 0) {
        // Get the best match (first result is most relevant due to backend sorting)
        const bestMatch = searchResponse.results[0];
        
        console.log(`Found symbol: ${bestMatch.symbol} (${bestMatch.name}) via Alpaca search`);
        
        return {
          symbol: bestMatch.symbol,
          type: 'stock', // Alpaca primarily deals with US equities
          name: bestMatch.name
        };
      }
      
      console.log(`No symbols found for query: "${query}"`);
      return null;
    } catch (error) {
      console.error(`Error searching for symbol "${query}":`, error);
      return null;
    }
  }

  /**
   * Resolve symbol based on context and mappings (legacy fallback)
   */
  private resolveSymbol(symbol: string, context: 'stock' | 'crypto' | 'auto', tradingPair?: string): { symbol: string; type: 'stock' | 'crypto'; tradingPair?: string } | null {
    const upperSymbol = symbol.toUpperCase();
    
    // First validate the symbol
    if (!this.isValidSymbol(upperSymbol)) {
      console.warn(`Invalid symbol rejected: ${upperSymbol}`);
      return null;
    }
    
    // Check if it's a conflicting symbol
    if (this.symbolConflicts[upperSymbol]) {
      if (context === 'crypto') {
        const cryptoConfig = this.symbolConflicts[upperSymbol].crypto;
        const pair = this.selectTradingPair(cryptoConfig, tradingPair);
        return { symbol: pair.symbol, type: 'crypto', tradingPair: pair.pair };
      } else if (context === 'stock') {
        return { symbol: this.symbolConflicts[upperSymbol].stock, type: 'stock' };
      } else {
        // Default to stock for conflicting symbols in auto mode
        console.log(`Symbol ${upperSymbol} exists as both stock and crypto, defaulting to stock`);
        return { symbol: this.symbolConflicts[upperSymbol].stock, type: 'stock' };
      }
    }
    
    // Check company names
    if (this.companyToTicker[upperSymbol]) {
      return { symbol: this.companyToTicker[upperSymbol], type: 'stock' };
    }
    
    // Check crypto names
    if (this.cryptoToTicker[upperSymbol]) {
      const pair = this.selectTradingPair(this.cryptoToTicker[upperSymbol], tradingPair);
      return { symbol: pair.symbol, type: 'crypto', tradingPair: pair.pair };
    }
    
    // Check if it's a direct crypto symbol with trading pair suffix
    if (upperSymbol.match(/-USD$|-USDT$|-USDC$|-EUR$|-BTC$|-ETH$/)) {
      const pairMatch = upperSymbol.match(/(USD|USDT|USDC|EUR|BTC|ETH)$/);
      return { symbol: upperSymbol, type: 'crypto', tradingPair: pairMatch?.[1] };
    }
    
    // If context suggests crypto, try adding trading pair suffix
    if (context === 'crypto' && upperSymbol.length <= 5 && !upperSymbol.includes('-')) {
      const defaultPair = tradingPair || 'USD';
      return { symbol: `${upperSymbol}-${defaultPair}`, type: 'crypto', tradingPair: defaultPair };
    }
    
    // Validate as potential stock symbol
    if (this.isValidSymbol(upperSymbol) && context !== 'crypto') {
      return { symbol: upperSymbol, type: 'stock' };
    }
    
    return null;
  }
  
  private selectTradingPair(
    cryptoConfig: { gecko: string; yahoo: string; cmc?: string },
    requestedPair?: string
  ): { symbol: string; pair: string } {
    // If specific pair requested, try to use it
    if (requestedPair) {
      const upperPair = requestedPair.toUpperCase();
      if (upperPair === 'USDT' || upperPair === 'USDC' || upperPair === 'EUR' || upperPair === 'BTC' || upperPair === 'ETH') {
        // Replace USD with requested pair
        const baseSymbol = cryptoConfig.yahoo.replace(/-USD$/, '');
        return { symbol: `${baseSymbol}-${upperPair}`, pair: upperPair };
      }
    }
    
    // Default to USD pair (most widely available on Yahoo Finance)
    return { symbol: cryptoConfig.yahoo, pair: 'USD' };
  }

  /**
   * Parse drawing command from API format
   */
  private parseDrawingCommand(cmd: string): ChartCommand | null {
    const parts = cmd.split(':');
    const type = parts[0];
    
    switch(type) {
      case 'SUPPORT':
        return {
          type: 'drawing',
          value: {
            action: 'support',
            price: parseFloat(parts[1])
          },
          timestamp: Date.now()
        };
        
      case 'RESISTANCE':
        return {
          type: 'drawing',
          value: {
            action: 'resistance',
            price: parseFloat(parts[1])
          },
          timestamp: Date.now()
        };
        
      case 'ENTRY':
        return {
          type: 'drawing',
          value: {
            action: 'entry',
            price: parseFloat(parts[1])
          },
          timestamp: Date.now()
        };
        
      case 'TARGET':
        return {
          type: 'drawing',
          value: {
            action: 'target',
            price: parseFloat(parts[1])
          },
          timestamp: Date.now()
        };
        
      case 'STOPLOSS':
        return {
          type: 'drawing',
          value: {
            action: 'stoploss',
            price: parseFloat(parts[1])
          },
          timestamp: Date.now()
        };
        
      case 'TRENDLINE':
        return {
          type: 'drawing',
          value: {
            action: 'trendline',
            startPrice: parseFloat(parts[1]),
            startTime: parseInt(parts[2]),
            endPrice: parseFloat(parts[3]),
            endTime: parseInt(parts[4])
          },
          timestamp: Date.now()
        };
        
      case 'FIBONACCI':
        return {
          type: 'drawing',
          value: {
            action: 'fibonacci',
            high: parseFloat(parts[1]),
            low: parseFloat(parts[2])
          },
          timestamp: Date.now()
        };
        
      case 'PATTERN':
        return {
          type: 'drawing',
          value: {
            action: 'pattern',
            patternType: parts[1],
            startCandle: parseInt(parts[2]),
            endCandle: parseInt(parts[3])
          },
          timestamp: Date.now()
        };
        
      default:
        return null;
    }
  }

  /**
   * Parse agent response for chart commands (async for symbol search)
   */
  async parseAgentResponse(response: string, chartCommandsFromApi?: string[]): Promise<ChartCommand[]> {
    const commands: ChartCommand[] = [];
    
    // Process explicit chart commands from API first
    if (chartCommandsFromApi && chartCommandsFromApi.length > 0) {
      for (const cmd of chartCommandsFromApi) {
        // Check if it's a drawing command
        const drawingCommand = this.parseDrawingCommand(cmd);
        if (drawingCommand) {
          commands.push(drawingCommand);
        } else {
          // Handle other command types
          if (cmd.startsWith('CHART:')) {
            const symbol = cmd.substring(6);
            commands.push({
              type: 'symbol',
              value: symbol,
              timestamp: Date.now()
            });
          } else if (cmd.startsWith('TIMEFRAME:')) {
            const timeframe = cmd.substring(10);
            commands.push({
              type: 'timeframe', 
              value: timeframe,
              timestamp: Date.now()
            });
          }
        }
      }
    }
    
    // Detect context from the response
    const assetContext = this.detectAssetType(response);
    
    // Detect trading pair mentions
    const tradingPairMatch = response.match(/\b(USDT|USDC|EUR|BTC|ETH)\s*(pair|trading|market)?\b/i);
    const requestedPair = tradingPairMatch ? tradingPairMatch[1] : undefined;
    
    // Check for symbol changes (handle multiple capture groups)
    const symbolMatch = response.match(this.commandPatterns.symbol);
    if (symbolMatch) {
      // Find the first non-undefined capture group
      const rawSymbol = symbolMatch[1] || symbolMatch[2];
      
      if (rawSymbol) {
        // Try semantic search first (best for company names like "Microsoft")
        let resolved = await this.resolveSymbolWithSearch(rawSymbol);
        
        if (!resolved) {
          // Fallback to legacy static mapping if search fails
          const legacyResolved = this.resolveSymbol(rawSymbol, assetContext, requestedPair);
          if (legacyResolved) {
            resolved = {
              symbol: legacyResolved.symbol,
              type: legacyResolved.type,
              name: rawSymbol
            };
          }
        }
        
        if (resolved) {
          console.log(`Resolved "${rawSymbol}" to ${resolved.type} symbol: ${resolved.symbol}${resolved.name ? ` (${resolved.name})` : ''}`);
          commands.push({
            type: 'symbol',
            value: resolved.symbol,
            metadata: { 
              assetType: resolved.type,
              companyName: resolved.name
            },
            timestamp: Date.now()
          });
        } else {
          console.log(`Could not resolve symbol: "${rawSymbol}"`);
        }
      }
    }

    // Check for timeframe changes
    const timeframeMatch = response.match(this.commandPatterns.timeframe);
    if (timeframeMatch) {
      commands.push({
        type: 'timeframe',
        value: timeframeMatch[1],
        timestamp: Date.now()
      });
    }

    // Check for indicator toggles
    const indicatorMatch = response.match(this.commandPatterns.indicator);
    if (indicatorMatch) {
      const action = indicatorMatch[0].split(/[:\s]+/)[0].toUpperCase();
      const enabled = action === 'ADD' || action === 'SHOW';
      commands.push({
        type: 'indicator',
        value: { name: indicatorMatch[1], enabled },
        timestamp: Date.now()
      });
    }

    // Check for zoom commands
    const zoomMatch = response.match(this.commandPatterns.zoom);
    if (zoomMatch) {
      let zoomValue = 0;
      if (zoomMatch[1] === 'IN') zoomValue = 1.2;
      else if (zoomMatch[1] === 'OUT') zoomValue = 0.8;
      else zoomValue = parseFloat(zoomMatch[1]) / 100;
      
      commands.push({
        type: 'zoom',
        value: zoomValue,
        timestamp: Date.now()
      });
    }

    // Check for scroll commands
    const scrollMatch = response.match(this.commandPatterns.scroll);
    if (scrollMatch) {
      commands.push({
        type: 'scroll',
        value: scrollMatch[1],
        timestamp: Date.now()
      });
    }

    // Check for style changes
    const styleMatch = response.match(this.commandPatterns.style);
    if (styleMatch) {
      const styleValue = styleMatch[1] || styleMatch[2];
      const styleMap: { [key: string]: 'candles' | 'line' | 'area' } = {
        'CANDLE': 'candles',
        'CANDLES': 'candles',
        'CANDLESTICK': 'candles',
        'LINE': 'line',
        'AREA': 'area',
        'BAR': 'candles',
        'BARS': 'candles',
        'HEIKIN': 'candles',
        'HOLLOW': 'candles'
      };
      
      commands.push({
        type: 'style',
        value: styleMap[styleValue?.toUpperCase()] || 'candles',
        timestamp: Date.now()
      });
    }

    // Check for reset command
    const resetMatch = response.match(this.commandPatterns.reset);
    if (resetMatch) {
      commands.push({
        type: 'reset',
        value: 'view',
        timestamp: Date.now()
      });
    }

    // Check for crosshair command
    const crosshairMatch = response.match(this.commandPatterns.crosshair);
    if (crosshairMatch) {
      const action = crosshairMatch[1]?.toUpperCase() || 'TOGGLE';
      commands.push({
        type: 'crosshair',
        value: action === 'ON' || (action === 'TOGGLE' && !this.chartRef?.options()?.crosshair?.mode),
        timestamp: Date.now()
      });
    }

    return commands;
  }

  /**
   * Execute drawing command
   */
  private executeDrawingCommand(drawing: any): boolean {
    // Base chartControlService doesn't handle drawings directly
    // Drawing commands should be handled by enhancedChartControl
    // Return false to indicate the command wasn't handled here
    console.log('Drawing command received by base service:', drawing.action);
    return false;
  }

  /**
   * Execute a chart command
   */
  executeCommand(command: ChartCommand): boolean {
    let message = '';
    let success = false;
    
    try {
      switch (command.type) {
        case 'drawing':
          success = this.executeDrawingCommand(command.value);
          if (success) {
            const action = command.value.action;
            message = `Drew ${action} ${command.value.price ? `at $${command.value.price}` : ''}`;
          } else {
            message = 'Failed to execute drawing';
          }
          break;
          
        case 'symbol':
          if (this.callbacks.onSymbolChange) {
            this.currentSymbol = command.value;
            this.callbacks.onSymbolChange(command.value, command.metadata);
            const assetType = command.metadata?.assetType;
            const icon = assetType === 'crypto' ? '₿' : '📈';
            message = `${icon} Switched to ${command.value}`;
            success = true;
          } else {
            message = 'Symbol change not available';
          }
          break;
          
        case 'timeframe':
          if (this.callbacks.onTimeframeChange) {
            this.callbacks.onTimeframeChange(command.value);
            message = `Timeframe: ${command.value}`;
            success = true;
          } else {
            message = 'Timeframe change not available';
          }
          break;
          
        case 'indicator':
          if (this.callbacks.onIndicatorToggle) {
            this.callbacks.onIndicatorToggle(
              command.value.name,
              command.value.enabled
            );
            message = `${command.value.enabled ? 'Added' : 'Removed'} ${command.value.name}`;
            success = true;
          } else {
            message = 'Indicator toggle not available';
          }
          break;
          
        case 'zoom':
          if (this.callbacks.onZoomChange && this.chartRef) {
            try {
              const timeScale = this.chartRef.timeScale();
              if (command.value > 1) {
                timeScale.zoomIn();
                message = 'Zoomed in';
              } else {
                timeScale.zoomOut();
                message = 'Zoomed out';
              }
              success = true;
            } catch (error) {
              console.error('Zoom error:', error);
              message = 'Zoom function not available';
            }
          } else {
            message = 'Zoom control not available';
          }
          break;
          
        case 'scroll':
          if (this.callbacks.onScrollToTime && this.chartRef) {
            // Parse date or relative time
            let targetTime: number;
            const scrollValue = command.value || '';
            if (scrollValue && scrollValue.match && scrollValue.match(/\d{4}-\d{2}-\d{2}/)) {
              targetTime = new Date(scrollValue).getTime() / 1000;
              message = `Scrolled to ${scrollValue}`;
            } else if (scrollValue) {
              // Handle relative times like "yesterday", "last week"
              const now = new Date();
              switch (scrollValue.toLowerCase()) {
                case 'yesterday':
                  targetTime = (now.getTime() - 86400000) / 1000;
                  message = 'Scrolled to yesterday';
                  break;
                case 'last week':
                  targetTime = (now.getTime() - 604800000) / 1000;
                  message = 'Scrolled to last week';
                  break;
                case 'last month':
                  targetTime = (now.getTime() - 2592000000) / 1000;
                  message = 'Scrolled to last month';
                  break;
                default:
                  targetTime = now.getTime() / 1000;
                  message = 'Scrolled to current time';
              }
            }
            
            this.chartRef.timeScale().scrollToPosition(targetTime, false);
            success = true;
          } else {
            message = 'Scroll control not available';
          }
          break;
          
        case 'style':
          if (this.callbacks.onStyleChange) {
            this.callbacks.onStyleChange(command.value);
            const styleNames = {
              'candles': 'Candlestick',
              'line': 'Line',
              'area': 'Area'
            };
            message = `Style: ${styleNames[command.value] || command.value}`;
            success = true;
          } else {
            message = 'Style change not available';
          }
          break;
          
        case 'reset':
          if (this.chartRef) {
            try {
              this.chartRef.timeScale().fitContent();
              message = 'Chart view reset';
              success = true;
            } catch (e) {
              message = 'Failed to reset view';
            }
          } else {
            message = 'Chart not available';
          }
          break;
          
        case 'crosshair':
          if (this.chartRef) {
            try {
              const mode = command.value ? 1 : 0;
              this.chartRef.applyOptions({
                crosshair: {
                  mode: mode
                }
              });
              message = `Crosshair ${command.value ? 'enabled' : 'disabled'}`;
              success = true;
            } catch (e) {
              message = 'Failed to toggle crosshair';
            }
          } else {
            message = 'Chart not available';
          }
          break;
          
        default:
          message = `Unknown command: ${command.type}`;
      }
      
      // Trigger callback with result
      if (this.callbacks.onCommandExecuted) {
        this.callbacks.onCommandExecuted(command, success, message);
      }
      
      console.log(`Chart Command: ${message} (${success ? 'Success' : 'Failed'})`);
      
    } catch (error: any) {
      const errorMsg = `Error: ${error.message || 'Command failed'}`;
      console.error('Error executing chart command:', error);
      
      if (this.callbacks.onCommandError) {
        this.callbacks.onCommandError(errorMsg);
      }
      
      if (this.callbacks.onCommandExecuted) {
        this.callbacks.onCommandExecuted(command, false, errorMsg);
      }
      
      return false;
    }
    
    return success;
  }

  /**
   * Process agent response and execute any chart commands (async)
   */
  async processAgentResponse(response: string, chartCommandsFromApi?: string[]): Promise<ChartCommand[]> {
    const commands = await this.parseAgentResponse(response, chartCommandsFromApi);
    const executedCommands: ChartCommand[] = [];
    
    for (const command of commands) {
      if (this.executeCommand(command)) {
        executedCommands.push(command);
      }
    }
    
    return executedCommands;
  }

  /**
   * Get current chart state
   */
  getChartState() {
    return {
      symbol: this.currentSymbol,
      hasChart: !!this.chartRef
    };
  }

  /**
   * Helper to format command for agent prompt
   */
  static formatCommandExample(type: string, value: string): string {
    switch (type) {
      case 'symbol':
        return `CHART:${value}`;
      case 'timeframe':
        return `TIMEFRAME:${value}`;
      case 'indicator':
        return `ADD:${value}`;
      case 'zoom':
        return `ZOOM:${value}`;
      case 'scroll':
        return `SCROLL:${value}`;
      case 'style':
        return `STYLE:${value}`;
      default:
        return '';
    }
  }
}

// Export singleton instance
export const chartControlService = new ChartControlService();

// Export types and class for testing
export { ChartControlService };
