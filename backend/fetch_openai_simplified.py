from playwright.sync_api import sync_playwright

def fetch_article():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,  # Run with UI to see what's happening
            args=['--disable-blink-features=AutomationControlled']
        )
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        )
        
        page = context.new_page()
        
        try:
            print("Loading OpenAI page...")
            # Try with shorter timeout and different wait strategy
            response = page.goto(
                "https://openai.com/index/new-tools-for-building-agents/", 
                timeout=15000,
                wait_until="domcontentloaded"
            )
            
            print(f"Response status: {response.status if response else 'None'}")
            
            # Take a screenshot to see what we got
            page.screenshot(path="openai_page.png")
            print("Screenshot saved as openai_page.png")
            
            # Try to get any text content
            page.wait_for_timeout(3000)  # Wait 3 seconds
            
            # Get all text
            text_content = page.evaluate("""
                () => {
                    // Try multiple selectors
                    const selectors = ['article', 'main', '.content', 'body'];
                    for (const sel of selectors) {
                        const elem = document.querySelector(sel);
                        if (elem && elem.innerText) {
                            return elem.innerText;
                        }
                    }
                    return document.body.innerText;
                }
            """)
            
            if text_content:
                print("\n=== Article Content ===")
                print(text_content[:5000])  # Print first 5000 chars
            else:
                print("No text content found")
                
        except Exception as e:
            print(f"Error: {e}")
            # Try to get page content anyway
            try:
                html = page.content()
                print(f"HTML length: {len(html)} chars")
                print("First 500 chars of HTML:")
                print(html[:500])
            except:
                pass
        finally:
            browser.close()

if __name__ == "__main__":
    fetch_article()
