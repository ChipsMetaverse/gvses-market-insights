#!/usr/bin/env node

import 'dotenv/config';
import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
  console.error('❌ Missing Supabase credentials');
  process.exit(1);
}

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, {
  auth: {
    persistSession: false,
    autoRefreshToken: false,
  },
  db: {
    schema: 'public'
  }
});

async function checkTables() {
  console.log('=================================================');
  console.log('Phase 2 Database Table Check');
  console.log('=================================================\n');
  
  const tables = [
    'headless_jobs',
    'headless_workers', 
    'headless_job_leases',
    'headless_webhook_events'
  ];
  
  let allTablesExist = true;
  
  for (const table of tables) {
    process.stdout.write(`📋 Checking ${table}... `);
    
    try {
      const { data, error } = await supabase
        .from(table)
        .select('id')
        .limit(1);
        
      if (error && error.code === '42P01') {
        console.log('❌ Table does not exist');
        allTablesExist = false;
      } else if (error) {
        console.log(`⚠️  Error: ${error.message}`);
        allTablesExist = false;
      } else {
        console.log('✅ Table exists');
      }
    } catch (err) {
      console.log(`❌ Error: ${err.message}`);
      allTablesExist = false;
    }
  }
  
  console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  
  if (!allTablesExist) {
    console.log('❌ Some tables are missing\n');
    console.log('📝 Manual Action Required:\n');
    console.log('1. Go to: https://supabase.com/dashboard/project/cwnzgvrylvxfhwhsqelc/sql/new');
    console.log('2. Copy the SQL from: migrations/phase2_public_schema.sql');
    console.log('3. Paste and run it in the SQL Editor');
    console.log('4. Once complete, run this script again to verify');
  } else {
    console.log('✅ All Phase 2 tables exist!\n');
    console.log('You can now run: npm start');
  }
  
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
}

checkTables().catch(console.error);