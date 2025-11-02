"""
Market Data Population Script for Supabase
Fetches historical data from Alpaca and stores in Supabase
Implements rate limiting, batching, and error handling
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import sys

from supabase import create_client, Client
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('market_data_population.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class PopulationConfig:
    """Configuration for data population"""
    years_back: int = 20
    batch_size: int = 50
    rate_limit_delay: float = 0.5  # seconds between API calls
    max_retries: int = 3
    retry_delay: float = 5.0
    priority_symbols: List[str] = None
    
    def __post_init__(self):
        if self.priority_symbols is None:
            self.priority_symbols = [
                'SPY', 'QQQ', 'IWM', 'DIA',  # Major ETFs
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA',  # Mega caps
                'JPM', 'BAC', 'WFC', 'GS', 'MS',  # Financials
                'XOM', 'CVX',  # Energy
                'JNJ', 'UNH', 'PFE',  # Healthcare
                'COST', 'WMT', 'HD',  # Retail
            ]


class MarketDataPopulator:
    """Handles population of historical market data into Supabase"""
    
    def __init__(self, config: PopulationConfig = None):
        """Initialize the populator"""
        self.config = config or PopulationConfig()
        
        # Initialize Supabase client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)
        logger.info("✅ Supabase client initialized")
        
        # Initialize Alpaca client
        alpaca_api_key = os.getenv("ALPACA_API_KEY")
        alpaca_secret_key = os.getenv("ALPACA_SECRET_KEY")
        
        if not alpaca_api_key or not alpaca_secret_key:
            raise ValueError("ALPACA_API_KEY and ALPACA_SECRET_KEY must be set")
        
        self.alpaca_client = StockHistoricalDataClient(alpaca_api_key, alpaca_secret_key)
        logger.info("✅ Alpaca client initialized")
        
        # Statistics
        self.stats = {
            'total_symbols': 0,
            'successful': 0,
            'failed': 0,
            'total_records': 0,
            'start_time': datetime.now()
        }
    
    async def get_all_tradable_symbols(self) -> List[str]:
        """Get list of all tradable symbols"""
        try:
            # For now, return a curated list
            # In production, fetch from Alpaca's assets API
            symbols = self.config.priority_symbols.copy()
            
            # Add more symbols from common indices
            sp500_sample = [
                'AMD', 'INTC', 'CSCO', 'ORCL', 'ADBE', 'CRM', 'NFLX',
                'DIS', 'BA', 'CAT', 'MMM', 'GE', 'F', 'GM',
                'PEP', 'KO', 'MCD', 'SBUX', 'NKE',
                'V', 'MA', 'PYPL', 'SQ',
                'UBER', 'LYFT', 'ABNB',
                'ZM', 'SNOW', 'PLTR', 'COIN', 'RBLX'
            ]
            symbols.extend(sp500_sample)
            
            # Remove duplicates
            symbols = list(set(symbols))
            
            self.stats['total_symbols'] = len(symbols)
            logger.info(f"📊 Found {len(symbols)} symbols to process")
            
            return symbols
            
        except Exception as e:
            logger.error(f"❌ Error fetching symbols: {e}")
            return []
    
    async def fetch_historical_data(
        self, 
        symbol: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> Optional[pd.DataFrame]:
        """Fetch historical data for a symbol from Alpaca"""
        try:
            request_params = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Day,
                start=start_date,
                end=end_date
            )
            
            bars = self.alpaca_client.get_stock_bars(request_params)
            
            if not bars or symbol not in bars:
                logger.warning(f"⚠️ No data returned for {symbol}")
                return None
            
            # Convert to DataFrame
            df = bars[symbol].df
            
            if df.empty:
                logger.warning(f"⚠️ Empty data for {symbol}")
                return None
            
            logger.info(f"✅ Fetched {len(df)} records for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error fetching data for {symbol}: {e}")
            return None
    
    def transform_dataframe_to_records(
        self, 
        df: pd.DataFrame, 
        symbol: str
    ) -> List[Dict[str, Any]]:
        """Transform DataFrame to Supabase-compatible records"""
        records = []
        
        for index, row in df.iterrows():
            record = {
                'symbol': symbol,
                'date': index.date().isoformat(),
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': int(row['volume']),
                'adjusted_close': float(row['close']),  # Alpaca doesn't provide adj_close
                'data_source': 'alpaca'
            }
            records.append(record)
        
        return records
    
    async def upsert_records(
        self, 
        records: List[Dict[str, Any]], 
        symbol: str
    ) -> bool:
        """Upsert records into Supabase"""
        if not records:
            return False
        
        try:
            # Batch insert with upsert (on conflict update)
            result = self.supabase.table('market_data_daily').upsert(
                records,
                on_conflict='symbol,date'
            ).execute()
            
            self.stats['total_records'] += len(records)
            logger.info(f"💾 Inserted {len(records)} records for {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error inserting records for {symbol}: {e}")
            return False
    
    async def populate_symbol(
        self, 
        symbol: str, 
        retry_count: int = 0
    ) -> bool:
        """Populate historical data for a single symbol"""
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=self.config.years_back * 365)
            
            logger.info(f"🔄 Processing {symbol} ({start_date.date()} to {end_date.date()})")
            
            # Fetch data
            df = await self.fetch_historical_data(symbol, start_date, end_date)
            
            if df is None or df.empty:
                logger.warning(f"⚠️ Skipping {symbol} - no data available")
                self.stats['failed'] += 1
                return False
            
            # Transform to records
            records = self.transform_dataframe_to_records(df, symbol)
            
            # Upsert to database
            success = await self.upsert_records(records, symbol)
            
            if success:
                # Update symbol metadata
                await self.update_symbol_metadata(symbol, df)
                self.stats['successful'] += 1
                return True
            else:
                self.stats['failed'] += 1
                return False
            
        except Exception as e:
            logger.error(f"❌ Error populating {symbol}: {e}")
            
            # Retry logic
            if retry_count < self.config.max_retries:
                logger.info(f"🔁 Retrying {symbol} (attempt {retry_count + 1}/{self.config.max_retries})")
                await asyncio.sleep(self.config.retry_delay)
                return await self.populate_symbol(symbol, retry_count + 1)
            
            self.stats['failed'] += 1
            return False
    
    async def update_symbol_metadata(self, symbol: str, df: pd.DataFrame):
        """Update or insert symbol metadata"""
        try:
            first_date = df.index[0].date()
            last_date = df.index[-1].date()
            
            metadata = {
                'symbol': symbol,
                'is_active': True,
                'is_tradable': True,
                'first_trade_date': first_date.isoformat(),
                'last_update': last_date.isoformat(),
                'asset_type': 'stock',
                'exchange': 'unknown',  # Would need to fetch from Alpaca assets API
                'metadata': {
                    'record_count': len(df),
                    'last_sync': datetime.now().isoformat()
                }
            }
            
            self.supabase.table('symbols').upsert(
                metadata,
                on_conflict='symbol'
            ).execute()
            
        except Exception as e:
            logger.error(f"❌ Error updating metadata for {symbol}: {e}")
    
    async def log_sync_operation(
        self, 
        sync_type: str,
        symbols_updated: int,
        records_inserted: int,
        errors: int,
        duration: int,
        status: str
    ):
        """Log sync operation to database"""
        try:
            log_entry = {
                'sync_type': sync_type,
                'sync_date': datetime.now().date().isoformat(),
                'symbols_updated': symbols_updated,
                'records_inserted': records_inserted,
                'errors': errors,
                'duration_seconds': duration,
                'status': status
            }
            
            self.supabase.table('data_sync_log').insert(log_entry).execute()
            
        except Exception as e:
            logger.error(f"❌ Error logging sync operation: {e}")
    
    async def populate_all_symbols(self):
        """Populate data for all symbols with rate limiting"""
        logger.info("🚀 Starting market data population")
        
        # Get all symbols
        symbols = await self.get_all_tradable_symbols()
        
        if not symbols:
            logger.error("❌ No symbols to process")
            return
        
        # Process priority symbols first
        priority_set = set(self.config.priority_symbols)
        priority_symbols = [s for s in symbols if s in priority_set]
        other_symbols = [s for s in symbols if s not in priority_set]
        
        all_symbols = priority_symbols + other_symbols
        
        logger.info(f"📊 Processing {len(priority_symbols)} priority symbols first")
        logger.info(f"📊 Then processing {len(other_symbols)} additional symbols")
        
        # Process in batches
        for i in range(0, len(all_symbols), self.config.batch_size):
            batch = all_symbols[i:i + self.config.batch_size]
            batch_num = i // self.config.batch_size + 1
            total_batches = (len(all_symbols) + self.config.batch_size - 1) // self.config.batch_size
            
            logger.info(f"\n{'='*60}")
            logger.info(f"📦 Processing batch {batch_num}/{total_batches}: {len(batch)} symbols")
            logger.info(f"{'='*60}\n")
            
            for symbol in batch:
                await self.populate_symbol(symbol)
                await asyncio.sleep(self.config.rate_limit_delay)
            
            # Log progress
            self.print_progress()
        
        # Final summary
        self.print_final_summary()
    
    def print_progress(self):
        """Print current progress"""
        elapsed = (datetime.now() - self.stats['start_time']).total_seconds()
        success_rate = (self.stats['successful'] / max(self.stats['successful'] + self.stats['failed'], 1)) * 100
        
        logger.info(f"\n{'─'*60}")
        logger.info(f"📊 Progress Report")
        logger.info(f"{'─'*60}")
        logger.info(f"✅ Successful: {self.stats['successful']}/{self.stats['total_symbols']}")
        logger.info(f"❌ Failed: {self.stats['failed']}/{self.stats['total_symbols']}")
        logger.info(f"📈 Success Rate: {success_rate:.1f}%")
        logger.info(f"💾 Total Records: {self.stats['total_records']:,}")
        logger.info(f"⏱️  Elapsed Time: {int(elapsed)} seconds")
        logger.info(f"{'─'*60}\n")
    
    def print_final_summary(self):
        """Print final summary"""
        end_time = datetime.now()
        duration = (end_time - self.stats['start_time']).total_seconds()
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🎉 Market Data Population Complete!")
        logger.info(f"{'='*60}")
        logger.info(f"✅ Successful Symbols: {self.stats['successful']}")
        logger.info(f"❌ Failed Symbols: {self.stats['failed']}")
        logger.info(f"📊 Total Symbols: {self.stats['total_symbols']}")
        logger.info(f"💾 Total Records Inserted: {self.stats['total_records']:,}")
        logger.info(f"⏱️  Total Duration: {int(duration)} seconds ({duration/60:.1f} minutes)")
        logger.info(f"🚀 Average: {duration/max(self.stats['successful'], 1):.1f} seconds per symbol")
        logger.info(f"{'='*60}\n")
        
        # Log to database
        asyncio.create_task(self.log_sync_operation(
            sync_type='backfill',
            symbols_updated=self.stats['successful'],
            records_inserted=self.stats['total_records'],
            errors=self.stats['failed'],
            duration=int(duration),
            status='success' if self.stats['failed'] == 0 else 'partial'
        ))


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Populate market data into Supabase')
    parser.add_argument('--years', type=int, default=20, help='Years of historical data to fetch')
    parser.add_argument('--batch-size', type=int, default=50, help='Batch size for processing')
    parser.add_argument('--rate-limit', type=float, default=0.5, help='Delay between API calls (seconds)')
    parser.add_argument('--symbols', nargs='+', help='Specific symbols to populate (optional)')
    
    args = parser.parse_args()
    
    config = PopulationConfig(
        years_back=args.years,
        batch_size=args.batch_size,
        rate_limit_delay=args.rate_limit
    )
    
    if args.symbols:
        config.priority_symbols = args.symbols
    
    populator = MarketDataPopulator(config)
    
    try:
        await populator.populate_all_symbols()
    except KeyboardInterrupt:
        logger.info("\n⚠️ Population interrupted by user")
        populator.print_final_summary()
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())

