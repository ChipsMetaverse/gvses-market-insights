#!/usr/bin/env node

import 'dotenv/config';
import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
  console.error('❌ Missing Supabase credentials');
  process.exit(1);
}

// Create client without schema restriction
const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, {
  auth: {
    persistSession: false,
    autoRefreshToken: false,
  },
});

async function executeMigration() {
  console.log('🚀 Attempting to create headless schema...');
  
  // Try creating schema using a simple query
  const { data, error } = await supabase.rpc('query', {
    query_text: 'CREATE SCHEMA IF NOT EXISTS headless'
  });
  
  if (error) {
    console.log('First attempt failed, trying alternative approach...');
    
    // Try using direct SQL via the SQL endpoint
    const response = await fetch(`${SUPABASE_URL}/rest/v1/`, {
      method: 'POST', 
      headers: {
        'apikey': SUPABASE_SERVICE_ROLE_KEY,
        'Authorization': `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
      },
      body: JSON.stringify({
        query: 'CREATE SCHEMA IF NOT EXISTS headless'
      })
    });
    
    if (!response.ok) {
      console.error('❌ Failed to create schema:', await response.text());
      console.log('\n📋 Manual action required:');
      console.log('1. Go to: https://supabase.com/dashboard/project/cwnzgvrylvxfhwhsqelc');
      console.log('2. Navigate to SQL Editor');
      console.log('3. Run: CREATE SCHEMA IF NOT EXISTS headless;');
      return;
    }
  }
  
  console.log('✅ Schema creation attempted');
  
  // Test if we can access the schema now
  const testQuery = await supabase.from('headless.headless_workers').select('*').limit(1);
  
  if (testQuery.error && testQuery.error.code === 'PGRST106') {
    console.log('❌ Schema still not accessible via PostgREST');
    console.log('   The schema may need to be exposed in Supabase settings');
  } else {
    console.log('✅ Schema is accessible!');
  }
}

executeMigration().catch(console.error);