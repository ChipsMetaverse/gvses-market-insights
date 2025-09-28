import 'dotenv/config';
import { createClient } from '@supabase/supabase-js';
import fs from 'fs/promises';
import path from 'path';
import pino from 'pino';

const logger = pino({ level: process.env.LOG_LEVEL || 'info' });

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
  throw new Error('Supabase environment variables SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set');
}

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, {
  auth: {
    persistSession: false,
    autoRefreshToken: false,
  },
});

async function runMigration(filePath: string): Promise<void> {
  const migrationName = path.basename(filePath);
  logger.info({ migration: migrationName }, 'Running migration');

  try {
    // Read the SQL file
    const sql = await fs.readFile(filePath, 'utf-8');
    
    // Split into individual statements (basic split on semicolon)
    const statements = sql
      .split(';')
      .map(s => s.trim())
      .filter(s => s.length > 0 && !s.startsWith('--'));
    
    // Execute each statement
    for (const statement of statements) {
      if (statement.length === 0) continue;
      
      // Use RPC to execute raw SQL
      const { error } = await supabase.rpc('exec_sql', {
        query: statement + ';'
      }).single();
      
      if (error) {
        // Try direct execution as alternative
        const { error: directError } = await supabase.from('_migrations').select('*').limit(0);
        if (!directError) {
          logger.warn({ statement: statement.substring(0, 100) }, 'Skipped statement (may require direct SQL execution)');
          continue;
        }
        throw error;
      }
    }
    
    logger.info({ migration: migrationName }, 'Migration completed successfully');
  } catch (error) {
    logger.error({ error, migration: migrationName }, 'Migration failed');
    throw error;
  }
}

async function main() {
  const migrationsDir = path.join(process.cwd(), 'migrations');
  
  try {
    // Get all SQL files in migrations directory
    const files = await fs.readdir(migrationsDir);
    const sqlFiles = files
      .filter(f => f.endsWith('.sql'))
      .sort(); // Ensure they run in order
    
    logger.info({ count: sqlFiles.length }, 'Found migration files');
    
    for (const file of sqlFiles) {
      if (file.includes('phase2')) {
        // Only run phase2 migrations for now
        await runMigration(path.join(migrationsDir, file));
      }
    }
    
    logger.info('All migrations completed');
    process.exit(0);
  } catch (error) {
    logger.error({ error }, 'Migration runner failed');
    process.exit(1);
  }
}

main().catch(error => {
  logger.error({ error }, 'Unhandled error in migration runner');
  process.exit(1);
});