#!/usr/bin/env python3
"""
Fix all hardcoded localhost:8000 references to use dynamic getApiUrl()
"""

import os
import re

# Files to update
files_to_update = [
    '/Volumes/WD My Passport 264F Media/claude-voice-mcp/frontend/src/services/agentOrchestratorService.ts',
    '/Volumes/WD My Passport 264F Media/claude-voice-mcp/frontend/src/hooks/useElevenLabsConversation.ts',
    '/Volumes/WD My Passport 264F Media/claude-voice-mcp/frontend/src/providers/ProviderConfig.ts',
    '/Volumes/WD My Passport 264F Media/claude-voice-mcp/frontend/src/components/VoiceAssistantElevenlabs.tsx',
    '/Volumes/WD My Passport 264F Media/claude-voice-mcp/frontend/src/components/VoiceAssistantFixed.tsx',
    '/Volumes/WD My Passport 264F Media/claude-voice-mcp/frontend/src/hooks/useOpenAIRealtimeConversation.ts',
    '/Volumes/WD My Passport 264F Media/claude-voice-mcp/frontend/src/hooks/useIndicatorState.ts',
    '/Volumes/WD My Passport 264F Media/claude-voice-mcp/frontend/src/components/voice/VoiceAssistantElevenlabs.tsx',
    '/Volumes/WD My Passport 264F Media/claude-voice-mcp/frontend/src/components/voice/VoiceAssistantFixed.tsx',
    '/Volumes/WD My Passport 264F Media/claude-voice-mcp/frontend/src/hooks/useAgentConversation.ts',
    '/Volumes/WD My Passport 264F Media/claude-voice-mcp/frontend/src/components/voice/VoiceAssistantElevenLabsFixed.tsx',
]

def update_file(filepath):
    """Update a single file to use getApiUrl()"""
    
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return False
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Check if already has getApiUrl import
    has_import = "import { getApiUrl }" in content or "from '../utils/apiConfig'" in content
    
    # Add import if needed
    if not has_import:
        # Find the last import statement
        import_pattern = r'^import .*?;$'
        imports = re.findall(import_pattern, content, re.MULTILINE)
        if imports:
            last_import = imports[-1]
            # Add getApiUrl import after the last import
            content = content.replace(
                last_import, 
                last_import + "\nimport { getApiUrl } from '../utils/apiConfig';"
            )
    
    # Replace hardcoded URLs with getApiUrl()
    patterns_to_replace = [
        (r"const apiUrl = import\.meta\.env\.VITE_API_URL \|\| 'http://localhost:8000';?", 
         "const apiUrl = getApiUrl();"),
        (r"const API_URL = import\.meta\.env\.VITE_API_URL \|\| 'http://localhost:8000';?", 
         "const API_URL = getApiUrl();"),
        (r"this\.baseUrl = import\.meta\.env\.VITE_API_URL \|\| 'http://localhost:8000';?", 
         "this.baseUrl = getApiUrl();"),
        (r"apiUrl = 'http://localhost:8000'", 
         "apiUrl = getApiUrl()"),
        (r"apiUrl: import\.meta\.env\.VITE_API_URL \|\| 'http://localhost:8000'", 
         "apiUrl: getApiUrl()"),
    ]
    
    for pattern, replacement in patterns_to_replace:
        content = re.sub(pattern, replacement, content)
    
    # Special case for useAgentConversation.ts with type cast
    if 'useAgentConversation.ts' in filepath:
        content = content.replace(
            "const apiUrl = (import.meta as any).env.VITE_API_URL || 'http://localhost:8000';",
            "const apiUrl = getApiUrl();"
        )
    
    # Write back if changed
    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"✅ Updated: {os.path.basename(filepath)}")
        return True
    else:
        print(f"⏭️  No changes needed: {os.path.basename(filepath)}")
        return False

def main():
    print("Fixing all hardcoded API URLs to use dynamic getApiUrl()...")
    print("=" * 60)
    
    updated_count = 0
    for filepath in files_to_update:
        if update_file(filepath):
            updated_count += 1
    
    print("=" * 60)
    print(f"Complete! Updated {updated_count} files.")
    
    if updated_count > 0:
        print("\n⚠️  Frontend needs to rebuild with these changes.")
        print("Vite should auto-reload with HMR.")

if __name__ == "__main__":
    main()