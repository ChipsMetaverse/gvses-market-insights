#!/usr/bin/env python3
"""Test authentication with fresh browser context"""

from playwright.sync_api import sync_playwright
import time

def main():
    with sync_playwright() as p:
        # Launch with fresh context
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            ignore_https_errors=True
        )

        # Clear storage
        context.clear_cookies()

        page = context.new_page()

        # Enable console logging
        page.on('console', lambda msg: print(f'Console [{msg.type}]: {msg.text}'))

        print('🌐 Navigating to signin page (fresh context)...')
        page.goto('http://localhost:5174/signin', wait_until='networkidle')
        time.sleep(2)

        print('📝 Filling in credentials...')
        email_input = page.locator('input[type="email"]')
        email_input.click()
        email_input.fill('kennyfwk@gmail.com')

        password_input = page.locator('input[type="password"]')
        password_input.click()
        password_input.fill('Stitched1!')

        time.sleep(1)

        print('🔐 Clicking sign-in button...')

        # Listen for network responses
        def handle_response(response):
            if 'auth/v1/token' in response.url:
                print(f'Auth request: {response.status} - {response.url}')
                if response.status != 200:
                    try:
                        print(f'Response body: {response.text()[:200]}')
                    except:
                        pass

        page.on('response', handle_response)

        # Click sign in
        signin_button = page.locator('button:has-text("Sign In")')
        signin_button.click()

        # Wait for either dashboard or error
        try:
            print('⏳ Waiting for response...')
            time.sleep(5)

            current_url = page.url
            print(f'Current URL: {current_url}')

            if '/dashboard' in current_url:
                print('✅ Successfully logged in!')
                page.screenshot(path='.playwright-mcp/dashboard-authenticated-fresh.png')
                print('📸 Screenshot: dashboard-authenticated-fresh.png')
            else:
                print('❌ Still on signin page')

                # Check for error message
                error_elements = page.locator('text=/invalid|error|failed/i')
                if error_elements.count() > 0:
                    print(f'Error message found: {error_elements.first.text_content()}')

                page.screenshot(path='.playwright-mcp/signin-fresh-context.png')
                print('📸 Screenshot: signin-fresh-context.png')

        except Exception as e:
            print(f'Error: {e}')

        finally:
            time.sleep(2)
            browser.close()

if __name__ == '__main__':
    main()
