from playwright.sync_api import sync_playwright
import time

def fetch_article():
    with sync_playwright() as p:
        # Launch browser in headless mode
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Set a user agent to avoid bot detection
        page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        
        try:
            # Navigate to the page
            print("Navigating to OpenAI article...")
            page.goto("https://openai.com/index/new-tools-for-building-agents/", wait_until="networkidle")
            
            # Wait for content to load
            page.wait_for_selector("article", timeout=10000)
            time.sleep(2)  # Extra wait for dynamic content
            
            # Extract the article content
            article_content = page.evaluate("""
                () => {
                    const article = document.querySelector('article') || document.querySelector('main') || document.body;
                    const title = document.querySelector('h1')?.innerText || '';
                    const content = article?.innerText || '';
                    return {
                        title: title,
                        content: content
                    };
                }
            """)
            
            print(f"\n=== {article_content['title']} ===\n")
            print(article_content['content'])
            
        except Exception as e:
            print(f"Error fetching article: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    fetch_article()
