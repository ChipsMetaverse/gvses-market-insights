#!/usr/bin/env node

import 'dotenv/config';
import { createClient } from '@supabase/supabase-js';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
  console.error('❌ Supabase environment variables must be set');
  process.exit(1);
}

// Use public schema to create the headless schema
const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, {
  db: {
    schema: 'public',
  },
  auth: {
    persistSession: false,
    autoRefreshToken: false,
  },
});

async function applyMigration() {
  try {
    console.log('📋 Reading Phase 2 migration file...');
    const migrationPath = path.join(__dirname, 'migrations', 'phase2_supabase.sql');
    const migrationSQL = await fs.readFile(migrationPath, 'utf-8');

    console.log('🚀 Applying Phase 2 migration to Supabase...');
    console.log('   URL:', SUPABASE_URL);
    
    // Split the SQL into individual statements and execute them
    // Remove comments and split by semicolons
    const statements = migrationSQL
      .split('\n')
      .filter(line => !line.trim().startsWith('--'))
      .join('\n')
      .split(/;\s*$/m)
      .filter(stmt => stmt.trim().length > 0)
      .map(stmt => stmt.trim() + ';');

    let successCount = 0;
    let errorCount = 0;

    for (const statement of statements) {
      if (statement.trim().length === 0) continue;
      
      // Skip comments
      if (statement.trim().startsWith('--')) continue;

      // For debugging, show first 60 chars of each statement
      const preview = statement.substring(0, 60).replace(/\n/g, ' ');
      process.stdout.write(`   Executing: ${preview}...`);

      const { error } = await supabase.rpc('exec_sql', { 
        sql: statement 
      }).single();

      if (error) {
        // Try direct SQL execution via the SQL endpoint
        const response = await fetch(`${SUPABASE_URL}/rest/v1/rpc/exec_sql`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'apikey': SUPABASE_SERVICE_ROLE_KEY,
            'Authorization': `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
          },
          body: JSON.stringify({ sql: statement })
        });

        if (!response.ok) {
          console.log(' ❌');
          console.error(`   Error: ${error?.message || 'Failed to execute'}`);
          errorCount++;
        } else {
          console.log(' ✅');
          successCount++;
        }
      } else {
        console.log(' ✅');
        successCount++;
      }
    }

    console.log(`\n📊 Migration Results:`);
    console.log(`   ✅ Successful statements: ${successCount}`);
    console.log(`   ❌ Failed statements: ${errorCount}`);

    if (errorCount > 0) {
      console.log('\n⚠️  Some statements failed. The migration may need to be applied manually.');
      console.log('   Please use the Supabase Dashboard SQL Editor to apply the migration.');
    } else {
      console.log('\n✅ Phase 2 migration applied successfully!');
    }

  } catch (error) {
    console.error('❌ Failed to apply migration:', error.message);
    console.log('\n📋 Manual Migration Instructions:');
    console.log('1. Go to: https://cwnzgvrylvxfhwhsqelc.supabase.co');
    console.log('2. Navigate to SQL Editor');
    console.log('3. Copy contents of: migrations/phase2_supabase.sql');
    console.log('4. Paste and execute in SQL Editor');
    process.exit(1);
  }
}

console.log('=================================================');
console.log('Phase 2 Database Migration Tool');
console.log('=================================================\n');

applyMigration();