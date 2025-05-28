import time
import csv
import json
import os
import random
import sys
import re
from tqdm import tqdm
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from app.core.config import DATA_DIR


class GoogleMapsMaxReviewScraper:
    def __init__(self, headless=True, chrome_binary_path=None):
        """Initialize the scraper with aggressive settings for max review collection"""
        def create_options(version):
            """Helper function to create fresh ChromeOptions"""
            options = uc.ChromeOptions()
            
            # Set a realistic user agent
            user_agent = f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36'
            options.add_argument(f'--user-agent={user_agent}')
            
            # Add arguments to improve performance and avoid detection
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-infobars')
            options.add_argument('--disable-notifications')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-popup-blocking')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--lang=id')
            options.add_argument('--lang=ID')
            options.add_argument('--accept-lang=id-ID,id')
            
            # Configure chrome binary if provided
            if chrome_binary_path:
                if os.path.exists(chrome_binary_path):
                    print(f"Using Chrome binary at: {chrome_binary_path}")
                    options.binary_location = chrome_binary_path
                else:
                    print(f"Warning: Chrome binary not found at {chrome_binary_path}")
                    # Try to find Chrome in common locations
                    common_locations = [
                        '/usr/bin/google-chrome',
                        '/usr/bin/google-chrome-stable',
                        '/mnt/c/Program Files/Google/Chrome/Application/chrome.exe',
                        '/mnt/c/Program Files (x86)/Google/Chrome/Application/chrome.exe'
                    ]
                    for location in common_locations:
                        if os.path.exists(location):
                            print(f"Found Chrome at: {location}")
                            options.binary_location = location
                            break
            
            return options
        
        try:
            # First attempt with Chrome 136
            print("Attempting to start Chrome with version 136...")
            options = create_options(136)
            self.driver = uc.Chrome(
                options=options,
                headless=headless,
                use_subprocess=True,
                version_main=136
            )
            print("Successfully started Chrome with version 136")
        except Exception as e:
            print(f"Error starting Chrome 136: {str(e)}")
            print("\nTrying with Chrome 135...")
            try:
                # Second attempt with Chrome 135
                options = create_options(135)  # Create fresh options for version 135
                options.add_argument('--no-first-run')
                options.add_argument('--no-service-autorun')
                options.add_argument('--password-store=basic')
                self.driver = uc.Chrome(
                    options=options,
                    headless=headless,
                    use_subprocess=True,
                    version_main=135
                )
                print("Successfully started Chrome with version 135")
            except Exception as e2:
                print(f"Error starting Chrome 135: {str(e2)}")
                print("\nTrying one last time with default version...")
                try:
                    # Final attempt with default version
                    options = create_options(135)  # Create fresh options again
                    self.driver = uc.Chrome(
                        options=options,
                        headless=headless,
                        use_subprocess=True
                    )
                    print("Successfully started Chrome with default version")
                except Exception as e3:
                    print("All Chrome initialization attempts failed.")
                    print(f"Final error: {str(e3)}")
                    raise
        
        # Set up wait and maximize window
        self.wait = WebDriverWait(self.driver, 30)
        self.driver.maximize_window()
        print("Browser setup completed successfully")

    def scrape_reviews(self, place_url, target_reviews=50, max_wait_time=5, max_scroll_attempts=30):
        """
        Main method to scrape reviews using a simplified approach
        
        Args:
            place_url: URL of the Google Maps place
            target_reviews: Desired number of reviews to collect
            max_wait_time: Maximum seconds to wait between scrolls
            max_scroll_attempts: Maximum scroll attempts before giving up
        
        Returns:
            List of review dictionaries
        """
        print(f"Starting review collection for: {place_url}")
        
        # Navigate to the place
        print("Navigating to URL...")
        self.driver.get(place_url)
        print("URL loaded, waiting for page to initialize...")
        time.sleep(5)
        
        # Simple cookie acceptance
        try:
            accept_buttons = self.driver.find_elements(By.XPATH, 
                "//button[contains(., 'Accept') or contains(., 'Agree') or contains(., 'I agree') or contains(., 'Accept all') or contains(., 'OK')]")
            for button in accept_buttons:
                if button.is_displayed():
                    button.click()
                    print("Accepted cookies")
                    time.sleep(2)
                    break
        except:
            print("No cookie dialog found or already accepted")
        
        # Find and click the Reviews tab (simplest approach)
        print("Looking for Reviews tab...")
        review_tab_found = False
        
        # Print all available tabs for debugging
        all_tabs = self.driver.find_elements(By.XPATH, "//button[@role='tab']")
        print(f"Found {len(all_tabs)} tabs total")
        for idx, tab in enumerate(all_tabs):
            try:
                aria_label = tab.get_attribute('aria-label') or ""
                tab_text = tab.text or ""
                print(f"Tab {idx+1}: aria-label='{aria_label}', text='{tab_text}'")
            except:
                print(f"Tab {idx+1}: [Error getting attributes]")
        
        # Try to find the "Reviews" tab by text content, including "Reviews for..."
        # First attempt with specific structure from screenshot
        review_tabs = self.driver.find_elements(By.XPATH, "//button[@role='tab' and contains(@aria-label, 'Ulasan') or contains(@aria-label, 'Reviews')]")
        if not review_tabs:
            # Look for tabs with 'Review' but NOT 'Overview'/'Ringkasan'
            review_tabs = self.driver.find_elements(By.XPATH, "//button[@role='tab' and (contains(., 'Reviews') or contains(., 'Ulasan')) and not(contains(., 'Overview') or contains(., 'Ringkasan'))]")
        if not review_tabs:
            review_tabs = self.driver.find_elements(By.XPATH, "//button[@role='tab' and @aria-label[contains(., 'Reviews for') or contains(., 'Ulasan untuk')]]")
        if not review_tabs:
            review_tabs = self.driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'Reviews for') or contains(@aria-label, 'Ulasan untuk')]")
        if not review_tabs:
            # Look for tabs with text exactly matching "Reviews"
            review_tabs = self.driver.find_elements(By.XPATH, "//button[text()='Reviews' or text()='Ulasan']")
        if not review_tabs:
            # Search all tabs for those that might be review tabs
            for tab in all_tabs:
                try:
                    aria_label = tab.get_attribute('aria-label') or ""
                    tab_text = tab.text or ""
                    # Only consider tabs that have "review" but not "overview"
                    if (("review" in aria_label.lower() or "ulasan" in aria_label.lower()) and 
                        not ("overview" in aria_label.lower() or "ringkasan" in aria_label.lower())):
                        review_tabs = [tab]
                        print(f"Found potential review tab: {aria_label}")
                        break
                    # Check tab text too
                    if (("review" in tab_text.lower() or "ulasan" in tab_text.lower()) and
                        not ("overview" in tab_text.lower() or "ringkasan" in tab_text.lower())):
                        review_tabs = [tab]
                        print(f"Found potential review tab from text: {tab_text}")
                        break
                except:
                    continue
        
        # Sometimes the third tab is the Reviews tab
        if not review_tabs and len(all_tabs) >= 3:
            print("Trying third tab which is often the Reviews tab")
            review_tabs = [all_tabs[2]]
        
        # Try to click the reviews tab
        for tab in review_tabs:
            if tab.is_displayed():
                try:
                    aria_label = tab.get_attribute('aria-label') or ""
                    tab_text = tab.text or ""
                    print(f"Attempting to click tab with aria-label='{aria_label}', text='{tab_text}'")
                    
                    # Force tab into view and try both JS and normal click
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", tab)
                    time.sleep(1)
                    
                    # Try JavaScript click first
                    self.driver.execute_script("arguments[0].click();", tab)
                    print("Used JavaScript click on tab")
                    time.sleep(3)
                    
                    # If JS click might not have worked, try normal click
                    try:
                        tab.click()
                        print("Also used normal click on tab")
                    except:
                        pass
                        
                    review_tab_found = True
                    time.sleep(5)  # Wait for reviews to load
                    break
                except Exception as e:
                    print(f"Failed to click tab: {str(e)}, trying next one")
        
        # If we couldn't find the tab, try directly adding "/reviews" to the URL
        if not review_tab_found:
            print("Could not find Reviews tab, trying direct URL navigation...")
            try:
                # Directly try adding /reviews to the current URL
                current_url = self.driver.current_url
                if '/place/' in current_url and '/reviews' not in current_url:
                    reviews_url = current_url.split('?')[0]
                    if not reviews_url.endswith('/'):
                        reviews_url += '/'
                    reviews_url += 'reviews'
                    print(f"Attempting to navigate directly to: {reviews_url}")
                    self.driver.get(reviews_url)
                    time.sleep(5)
                    review_tab_found = True
                elif 'maps.app.goo.gl' in place_url:
                    # Try getting the shortened URL and modifying it
                    print("Trying to resolve shortened URL...")
                    
                    # Extract the URL components and construct a reviews URL
                    matches = re.search(r"maps/place/([^/]+)/([^/]+)", current_url)
                    if matches:
                        place_name = matches.group(1)
                        place_id = matches.group(2)
                        reviews_url = f"https://www.google.com/maps/place/{place_name}/{place_id}/reviews"
                        print(f"Constructed reviews URL: {reviews_url}")
                        self.driver.get(reviews_url)
                        time.sleep(5)
                        review_tab_found = True
                
                # One more attempt - try to use the UI to find reviews
                if not review_tab_found:
                    # Look for any rating element which might be clickable
                    rating_elements = self.driver.find_elements(By.XPATH, 
                        "//span[contains(@aria-label, 'star') or contains(@aria-label, 'bintang')]")
                    
                    for rating in rating_elements:
                        try:
                            print("Trying to click on rating element")
                            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", rating)
                            self.driver.execute_script("arguments[0].click();", rating)
                            time.sleep(5)
                            # Check if this got us to reviews
                            if self.driver.find_elements(By.XPATH, "//div[contains(@data-review-id, '')]"):
                                print("Successfully navigated to reviews by clicking rating")
                                review_tab_found = True
                                break
                        except:
                            continue
            except Exception as e:
                print(f"Direct URL navigation failed: {str(e)}")
        
        # Simplified check for reviews
        reviews_found = False
        print("Checking for reviews...")
        
        # Try multiple ways to find reviews
        try:
            # First check if we're in a reviews section by looking for common review indicators
            review_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-review-id]')
            if review_elements:
                reviews_found = True
                print(f"Found {len(review_elements)} reviews with data-review-id")
            
            # If not found, try other methods
            if not reviews_found:
                # Look for elements with star ratings that might be reviews
                star_elements = self.driver.find_elements(By.XPATH, '//span[contains(@aria-label, "stars")]')
                if star_elements:
                    print(f"Found {len(star_elements)} elements with star ratings")
                    # Check if any of these are part of reviews
                    for i in range(min(5, len(star_elements))):
                        star = star_elements[i]
                        try:
                            # Go up a few levels to find potential review container
                            parent = star
                            for _ in range(4):
                                parent = parent.find_element(By.XPATH, '..')
                                # Check if this element contains review-like content
                                review_indicators = [
                                    './/div[contains(@class, "fontBodyMedium")]',  # Common text class
                                    './/div[contains(@class, "MyEned")]',  # Date indicator
                                ]
                                for indicator in review_indicators:
                                    if parent.find_elements(By.XPATH, indicator):
                                        print("Found review-like structure")
                                        reviews_found = True
                                        break
                                if reviews_found:
                                    break
                        except:
                            continue
                        
            # One more attempt - look for common review structures
            if not reviews_found:
                review_candidates = self.driver.find_elements(By.XPATH, 
                    '//div[.//span[contains(@aria-label, "stars")] and (.//div[contains(@class, "fontBodyMedium")])]')
                if review_candidates:
                    reviews_found = True
                    print(f"Found {len(review_candidates)} likely review elements")
                
        except Exception as e:
            print(f"Error checking for reviews: {str(e)}")
        
        if not reviews_found:
            print("No reviews found after navigation attempts")
            return []
        
        print("Starting to collect reviews...")
        
        all_reviews = []
        seen_review_texts = set()
        
        # Start scrolling to load reviews
        try:
            with tqdm(total=target_reviews, desc="Loading reviews") as pbar:
                scroll_attempts = 0
                last_reviews_count = 0
                consecutive_no_new_reviews = 0
                last_scroll_height = 0
                
                # Find the scrollable container
                print("Looking for the scrollable reviews container...")
                scroller = None
                
                try:
                    # First, try to find the most reliable scrollable container - the reviews feed
                    review_containers = [
                        # Common feed container
                        (By.CSS_SELECTOR, 'div[role="feed"]'),
                        # Parent of review elements
                        (By.XPATH, '//div[.//div[@data-review-id]]'),
                        # Common Google Maps review containers
                        (By.CSS_SELECTOR, 'div.m6QErb.DxyBCb.kA9KIf.dS8AEf'),
                        (By.CSS_SELECTOR, 'div.m6QErb'),
                        (By.CSS_SELECTOR, 'div.DxyBCb'),
                        (By.CSS_SELECTOR, 'div[jsaction*="scroll"]'),
                        # Search for containers with multiple reviews
                        (By.XPATH, '//div[count(.//div[contains(@class, "fontBodyMedium")]) > 3]'),
                        # Last resort - main content area
                        (By.CSS_SELECTOR, 'div[role="main"]')
                    ]
                    
                    for locator_type, locator in review_containers:
                        try:
                            elements = self.driver.find_elements(locator_type, locator)
                            for element in elements:
                                if element.is_displayed():
                                    # Check if this container has reviews or rating stars
                                    try:
                                        has_reviews = len(element.find_elements(By.XPATH, './/div[@data-review-id]')) > 0
                                        has_stars = len(element.find_elements(By.XPATH, './/span[contains(@aria-label, "star")]')) > 0
                                        
                                        if has_reviews or has_stars:
                                            # Get dimensions to ensure it's a sizeable container
                                            size = element.size
                                            if size['height'] > 100:  # Only consider if it has reasonable height
                                                scroller = element
                                                print(f"Found scrollable container with {locator_type}:{locator}")
                                                break
                                    except:
                                        continue
                            if scroller:
                                break
                        except:
                            continue
                                        
                    # If still not found, use body as fallback
                    if not scroller:
                        scroller = self.driver.find_element(By.TAG_NAME, 'body')
                        print("Using body as scroll container")
                        
                except Exception as e:
                    print(f"Error finding scroll container: {str(e)}, using body")
                    scroller = self.driver.find_element(By.TAG_NAME, 'body')
                
                # Store all review data to avoid duplicates 
                seen_review_ids = set()
                seen_review_texts = set()
                
                # Main scrolling loop
                while len(all_reviews) < target_reviews and scroll_attempts < max_scroll_attempts:
                    scroll_attempts += 1
                    
                    # Before scrolling, get current scroll position
                    try:
                        current_scroll_position = self.driver.execute_script("return arguments[0].scrollTop;", scroller)
                        current_scroll_height = self.driver.execute_script("return arguments[0].scrollHeight;", scroller)
                        print(f"Scroll attempt {scroll_attempts}: position {current_scroll_position}/{current_scroll_height}")
                    except:
                        print(f"Scroll attempt {scroll_attempts}")
                    
                    # Try multiple scroll methods to ensure it works
                    scroll_worked = False
                    
                    # Method 1: JavaScript scroll by a large amount (better for continuous scrolling)
                    try:
                        scroll_distance = 1000 + (scroll_attempts * 200)  # Increase scroll distance each time
                        self.driver.execute_script(
                            "arguments[0].scrollBy({top: arguments[1], behavior: 'smooth'});", 
                            scroller, scroll_distance
                        )
                        scroll_worked = True
                        print(f"Scrolled down by {scroll_distance}px")
                    except Exception as e:
                        print(f"Method 1 scroll failed: {str(e)}")
                    
                    # Method 2: If method 1 didn't work, try scrolling to a specific position
                    if not scroll_worked:
                        try:
                            next_position = current_scroll_position + 1000
                            self.driver.execute_script(
                                "arguments[0].scrollTo({top: arguments[1], behavior: 'smooth'});", 
                                scroller, next_position
                            )
                            scroll_worked = True
                            print(f"Scrolled to position {next_position}")
                        except Exception as e:
                            print(f"Method 2 scroll failed: {str(e)}")
                    
                    # Method 3: If all else fails, try using keyboard
                    if not scroll_worked:
                        try:
                            # Focus on the element first
                            self.driver.execute_script("arguments[0].focus();", scroller)
                            # Send Page Down key multiple times
                            actions = ActionChains(self.driver)
                            for _ in range(3):
                                actions.send_keys(Keys.PAGE_DOWN).perform()
                                time.sleep(0.3)
                            scroll_worked = True
                            print("Scrolled using PAGE_DOWN keys")
                        except Exception as e:
                            print(f"Method 3 scroll failed: {str(e)}")
                            
                    # Method 4: Last resort - direct DOM manipulation
                    if not scroll_worked:
                        try:
                            print("Trying direct DOM manipulation...")
                            # Force scroll through DOM directly
                            self.driver.execute_script("""
                                arguments[0].scrollTop = arguments[0].scrollTop + 1000;
                                document.documentElement.scrollTop += 1000;
                                window.scrollTo(0, window.scrollY + 1000);
                            """, scroller)
                            scroll_worked = True
                        except Exception as e:
                            print(f"Method 4 scroll failed: {str(e)}")
                    
                    # Give time for new content to load
                    print(f"Waiting {max_wait_time}s for content to load...")
                    time.sleep(max_wait_time)
                    
                    # After scrolling, expand any "More" buttons to see full review text
                    try:
                        more_buttons = self.driver.find_elements(By.XPATH, 
                            '//button[contains(., "More") or contains(., "more") or contains(., "Lainnya")]')
                        
                        expanded = 0
                        for button in more_buttons[:7]:  # Process more buttons per scroll
                            if button.is_displayed():
                                try:
                                    # Scroll to make sure button is in view
                                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                                    time.sleep(0.2)
                                    
                                    # Try JavaScript click - more reliable
                                    self.driver.execute_script("arguments[0].click();", button)
                                    expanded += 1
                                    time.sleep(0.3)
                                except:
                                    try:
                                        button.click()
                                        expanded += 1
                                        time.sleep(0.3)
                                    except:
                                        pass
                        
                        if expanded > 0:
                            print(f"Expanded {expanded} review text(s)")
                    except Exception as e:
                        print(f"Error expanding reviews: {str(e)}")
                        
                    # Random delay to avoid detection
                    random_delay = 0.5 + (random.random() * 1.0)
                    time.sleep(random_delay)
                    
                    # Now find and process all visible reviews
                    review_elements = []
                    
                    # Try multiple selectors to find reviews
                    try:
                        # First try data-review-id attribute
                        review_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-review-id]')
                        print(f"Found {len(review_elements)} reviews with data-review-id")
                        
                        # If too few, try looking for reviews by structure
                        if len(review_elements) < 5:
                            star_reviews = self.driver.find_elements(By.XPATH, 
                                '//div[.//span[contains(@aria-label, "stars")] and .//div[contains(@class, "fontBodyMedium")]]')
                            
                            if len(star_reviews) > len(review_elements):
                                review_elements = star_reviews
                                print(f"Found {len(review_elements)} reviews with stars and text")
                    except Exception as e:
                        print(f"Error finding reviews: {str(e)}")
                    
                    # Process reviews
                    new_reviews = 0
                    if review_elements:
                        for element in review_elements:
                            try:
                                # Generate a unique ID for this review
                                review_id = element.get_attribute('data-review-id')
                                if not review_id:
                                    try:
                                        # Create a position-based ID if attribute not available
                                        reviewer_element = element.find_element(By.XPATH, './/div[contains(@class, "fontHeadlineSmall")]')
                                        reviewer_name = reviewer_element.text.strip()
                                        review_id = f"pos_{reviewer_name}_{review_elements.index(element)}"
                                    except:
                                        review_id = f"pos_{review_elements.index(element)}"
                                
                                # Skip if already processed
                                if review_id in seen_review_ids:
                                    continue
                                
                                # Extract the review data
                                review_data = self._extract_review_data(element)
                                if review_data:
                                    # Mark as seen using both ID and content signature
                                    seen_review_ids.add(review_id)
                                    
                                    # Create a signature based on reviewer name and text 
                                    review_text = review_data.get('review_text', '').strip()
                                    review_signature = f"{review_data.get('reviewer_name')}:{review_text[:50]}"
                                    
                                    if review_signature not in seen_review_texts:
                                        seen_review_texts.add(review_signature)
                                        all_reviews.append(review_data)
                                        new_reviews += 1
                                        
                                        # Update progress bar
                                        if len(all_reviews) > pbar.n:
                                            pbar.update(len(all_reviews) - pbar.n)
                                        
                                        if len(all_reviews) >= target_reviews:
                                            break
                            except Exception as e:
                                print(f"Error processing review: {str(e)}")
                                continue
                    
                    # Report progress
                    print(f"Found {new_reviews} new reviews, total now: {len(all_reviews)}")
                    
                    # Check if we've made progress
                    if new_reviews > 0:
                        consecutive_no_new_reviews = 0
                    else:
                        consecutive_no_new_reviews += 1
                        print(f"No new reviews found in {consecutive_no_new_reviews} consecutive attempts")
                    
                    # If we're not making progress after several attempts, try more aggressive scrolling
                    if consecutive_no_new_reviews >= 2:
                        try:
                            print("Trying aggressive scrolling...")
                            # Try scrolling to the bottom
                            self.driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", scroller)
                            time.sleep(2)
                            
                            # Then scroll back up a bit to trigger loading
                            self.driver.execute_script("arguments[0].scrollBy(0, -300);", scroller)
                            time.sleep(2)
                            
                            # Then down again
                            self.driver.execute_script("arguments[0].scrollBy(0, 500);", scroller)
                            time.sleep(2)
                        except Exception as e:
                            print(f"Aggressive scroll failed: {str(e)}")
                    
                    # After a few no-progress iterations, try clicking on a different part of the page
                    if consecutive_no_new_reviews == 3:
                        try:
                            print("Trying to reset the page view...")
                            # Try clicking in an empty area
                            self.driver.execute_script(
                                "var el = document.createElement('div'); " +
                                "el.setAttribute('style', 'height: 100px; width: 100px; position: absolute; left: 0; top: 0;'); " +
                                "document.body.appendChild(el); " +
                                "el.click(); " +
                                "document.body.removeChild(el);"
                            )
                            time.sleep(1)
                            
                            # Try refreshing the scroller reference
                            try:
                                # Re-find the scroller element as the reference might be stale
                                if scroller.tag_name != 'body':  # Only if we're not using body
                                    for locator_type, locator in review_containers:
                                        elements = self.driver.find_elements(locator_type, locator)
                                        if elements:
                                            scroller = elements[0]
                                            print("Refreshed scroller reference")
                                            break
                            except:
                                pass
                        except Exception as e:
                            print(f"Reset attempt failed: {str(e)}")
                    
                    # Check if we've exhausted all attempts
                    if consecutive_no_new_reviews >= 5:
                        print("No new reviews found after multiple attempts, ending collection")
                        break
                
                print(f"Scrolling complete. Collected {len(all_reviews)} reviews total.")
        except KeyboardInterrupt:
            print("\nCollection interrupted by user. Saving collected reviews...")
        except Exception as e:
            print(f"\nError during review collection: {str(e)}")
            print("Saving reviews collected so far...")
        
        print(f"Finished review collection. Found {len(all_reviews)} unique reviews.")
        return all_reviews[:target_reviews]

    def _extract_review_data(self, review_element):
        """Extract data from a review element using a simplified approach"""
        try:
            # Try to scroll the element into view first to ensure it's fully loaded
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", review_element)
                time.sleep(0.5)  # Wait longer to ensure it's loaded
            except:
                pass
                
            # Extract reviewer name (simplified)
            reviewer_name = "Unknown Reviewer"
            try:
                name_elements = review_element.find_elements(By.XPATH, './/div[contains(@class, "fontHeadlineSmall")]')
                if not name_elements:
                    name_elements = review_element.find_elements(By.XPATH, './/div[contains(@class, "fontTitleLarge")]')
                if not name_elements:
                    name_elements = review_element.find_elements(By.XPATH, './/div[contains(@class, "d4r55")]')
                
                for element in name_elements:
                    if element.is_displayed() and element.text.strip():
                        reviewer_name = element.text.strip()
                        break
            except:
                pass
            
            # Extract rating (simplified)
            rating_value = 0.0
            try:
                star_elements = review_element.find_elements(By.XPATH, './/span[contains(@aria-label, "star") or contains(@aria-label, "stars")]')
                for star in star_elements:
                    if star.is_displayed():
                        aria_label = star.get_attribute('aria-label')
                        if aria_label:
                            # Extract digits from aria-label
                            digits = re.findall(r'\d+[,.]?\d*', aria_label.replace(',', '.'))
                            if digits:
                                rating_value = float(digits[0])
                                break
            except:
                pass
            
            # Try to expand the review if possible FIRST before extracting text
            try:
                more_buttons = review_element.find_elements(By.XPATH, 
                    './/button[contains(., "More") or contains(., "more") or contains(., "Lainnya")]')
                for button in more_buttons:
                    if button.is_displayed():
                        try:
                            # Try JS click first
                            self.driver.execute_script("arguments[0].click();", button)
                            print("Expanded a review with JS click")
                            time.sleep(0.5)
                        except:
                            try:
                                button.click()
                                print("Expanded a review with normal click")
                                time.sleep(0.5)
                            except:
                                pass
                        break
            except:
                pass
                
            # Extract review text (main content) - using more methods to ensure we get the text
            review_text = ""
            
            # Save all potential text elements to check later
            potential_text_elements = []
            
            try:
                # Find the main text content by class and content
                text_selectors = [
                    './/div[contains(@class, "fontBodyMedium") and not(contains(@class, "MyEned"))]',  # Main review text
                    './/span[contains(@class, "wiI7pd")]',  # Common expanded text class
                    './/div[contains(@class, "review-full-text")]',  # Another review text class
                    './/div[@class="MyEned"]/following-sibling::div',  # Text after date element
                    './/div[contains(@class, "fontBodyMedium")]',  # Any medium body text
                    './/div[@data-js-log-root]',  # Root review element
                ]
                
                # First try specific review text selectors
                for selector in text_selectors:
                    text_elements = review_element.find_elements(By.XPATH, selector)
                    for element in text_elements:
                        if element.is_displayed():
                            text = element.text.strip()
                            # Only consider viable texts
                            if len(text) > 5:
                                potential_text_elements.append((element, text))
                                
                                # Check if this looks like a real review (longer text)
                                if len(text) > 20 and not text.endswith('ago') and not any(month in text.lower() for month in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']):
                                    if len(text) > len(review_text):
                                        review_text = text
                
                # If no specific review text found, look at all text in the review
                if not review_text and potential_text_elements:
                    # Sort by length (longest first)
                    potential_text_elements.sort(key=lambda x: len(x[1]), reverse=True)
                    for _, text in potential_text_elements:
                        # Skip texts that look like dates or ratings
                        if "stars" in text.lower() or "ago" in text.lower() or len(text) < 10:
                            continue
                        review_text = text
                        break
                
                # If still no text, try getting text directly from the element
                if not review_text:
                    direct_text = review_element.text.strip()
                    # Parse out the longest line from the direct text
                    lines = direct_text.split('\n')
                    lines = [line.strip() for line in lines if len(line.strip()) > 10]
                    if lines:
                        longest_line = max(lines, key=len)
                        review_text = longest_line
                
                # Last resort: get all text in the element and do basic cleaning
                if not review_text:
                    all_text = review_element.text
                    # Remove names, timestamps, and rating patterns
                    cleaned_lines = []
                    for line in all_text.split('\n'):
                        if (len(line.strip()) > 15 and 
                            'star' not in line.lower() and 
                            'ago' not in line.lower() and
                            not any(month in line.lower() for month in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'])):
                            cleaned_lines.append(line.strip())
                    
                    if cleaned_lines:
                        review_text = max(cleaned_lines, key=len)
            except Exception as e:
                print(f"Error extracting review text: {str(e)}")
            
            # Extract date (separate pass)
            date = "Unknown Date"
            try:
                # Look specifically for date elements by class and content
                date_selectors = [
                    './/div[contains(@class, "MyEned")]',  # Main date class
                    './/div[contains(@class, "rsqaWe")]',  # Another date class
                    './/div[contains(text(), "ago") and string-length() < 30]',  # Texts like "2 months ago"
                    './/div[contains(@class, "fontBodySmall") and (contains(text(), "ago") or contains(text(), "/") or contains(text(), "-"))]'  # Small text with date indicators
                ]
                
                for selector in date_selectors:
                    date_elements = review_element.find_elements(By.XPATH, selector)
                    for element in date_elements:
                        if element.is_displayed() and element.text.strip():
                            text = element.text.strip()
                            # Check if it looks like a date
                            if len(text) < 30 and (
                                    "ago" in text.lower() or 
                                    any(month in text.lower() for month in ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]) or
                                    re.search(r'\d+/\d+', text) or  # MM/DD format
                                    re.search(r'\d+-\d+', text)  # MM-DD format
                                ):
                                date = text
                                break
            except:
                pass
            
            # Has photos (simplified)
            has_photos = False
            try:
                photos = review_element.find_elements(By.XPATH, './/button[contains(@jsaction, "reviewPhoto")]//img') or \
                         review_element.find_elements(By.XPATH, './/button[contains(@aria-label, "Photo")]') or \
                         review_element.find_elements(By.XPATH, './/img[not(contains(@src, "profile"))]')
                has_photos = len(photos) > 0
            except:
                pass
            
            # If the review text is empty but date has a long description, it might be a review text incorrectly classified
            if not review_text and len(date) > 50:
                review_text = date
                date = "Unknown Date"
            
            # Get review time if available
            time_ago = ""
            try:
                time_elements = review_element.find_elements(By.XPATH, './/div[contains(text(), "ago") and string-length() < 30]')
                for time_element in time_elements:
                    if time_element.is_displayed():
                        time_text = time_element.text.strip()
                        if "ago" in time_text.lower() and len(time_text) < 30:
                            time_ago = time_text
                            break
            except:
                pass
                
            # If we found time but not date, use time as the date
            if time_ago and date == "Unknown Date":
                date = time_ago
            
            try:
                # Cari elemen yang menandakan review diterjemahkan
                translated_elements = review_element.find_elements(
                    By.XPATH,
                    ".//*[contains(text(), 'Translated by Google') or contains(text(), 'Terjemahan oleh Google')]"
                )
                if translated_elements:
                    print("Lewati review hasil terjemahan Google")
                    return None  # Lewati review terjemahan
            except Exception as e:
                pass
                
            # Fill in the review data, ensuring we have at least some text for the review
            review_data = {
                'reviewer_name': reviewer_name,
                'rating': rating_value,
                'date': date,
                'review_text': review_text or "No review text found",
                'has_photos': has_photos
            }
            
            # Skip reviews without meaningful content
            if review_data['review_text'] == "No review text found" and review_data['rating'] == 0.0:
                print("Skipping review with no meaningful content")
                return None
                
            return review_data
            
        except Exception as e:
            print(f"Error extracting review data: {str(e)}")
            return None
    
    def save_reviews_to_files(self, reviews, output_dir=DATA_DIR):
        """Save the reviews to CSV and JSON files"""
        if not reviews:
            print("No reviews to save")
            return
        
        # Ensure output_dir exists
        os.makedirs(output_dir, exist_ok=True)

        output_file = os.path.join(output_dir, "google_maps_reviews.json")
        
        # Get all unique keys
        fieldnames = set()
        for review in reviews:
            fieldnames.update(review.keys())
        fieldnames = list(fieldnames)
        
        # Save to CSV
        # with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
        #     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        #     writer.writeheader()
        #     writer.writerows(reviews)
        
        # print(f"Reviews saved to {output_file}")
        
        # Save to JSON
        json_file = output_file.replace('.csv', '.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(reviews, f, ensure_ascii=False, indent=4)
        
        print(f"Reviews also saved as JSON to {json_file}")
        
        # Print sample of reviews
        print("\nSample of reviews scraped:")
        for i, review in enumerate(reviews[:3]):
            print(f"\nReview {i+1}:")
            print(f"Reviewer: {review['reviewer_name']}")
            print(f"Rating: {review['rating']}")
            print(f"Date: {review['date']}")
            print(f"Text: {review['review_text'][:100]}..." if len(review['review_text']) > 100 else f"Text: {review['review_text']}")
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            print("Browser closed")


def main():
    print("Google Maps Maximum Review Extractor")
    print("---------------------------------")
    
    # Get Chrome binary path
    print("\nDo you want to specify a Chrome binary path? (useful for WSL)")
    print("Common locations:")
    print("- For Chrome installed in Windows accessed via WSL: /mnt/c/Program Files/Google/Chrome/Application/chrome.exe")
    print("- For Chrome installed directly in WSL: /usr/bin/google-chrome")
    
    use_binary = input("Specify Chrome binary path? (y/n), default is n: ").strip().lower() or "n"
    
    chrome_binary_path = None
    if use_binary == "y":
        chrome_binary_path = input("Enter Chrome binary path: ").strip()
        
        if not os.path.exists(chrome_binary_path):
            print(f"Warning: The specified path {chrome_binary_path} does not exist.")
            proceed = input("Continue anyway? (y/n): ").strip().lower() or "n"
            if proceed != "y":
                print("Exiting.")
                return
    
    # Get headless mode preference
    headless_choice = input("\nRun in headless mode? (y/n), default is n: ").strip().lower() or "n"
    headless = headless_choice == "y"
    
    # Get the place URL
    place_url = input("\nEnter Google Maps place URL: ")
    
    # Get number of reviews
    num_reviews_input = input("Enter number of reviews to scrape (default: 100): ").strip() or "100"
    try:
        num_reviews = int(num_reviews_input)
    except ValueError:
        print("Invalid number, using default of 100")
        num_reviews = 100
    
    # Get max wait time
    wait_input = input("Enter seconds to wait between scrolls (default: 3): ").strip() or "3"
    try:
        max_wait = float(wait_input)
    except ValueError:
        print("Invalid number, using default of 3")
        max_wait = 3
    
    # Get max scroll attempts
    attempts_input = input("Enter maximum scroll attempts (default: 30): ").strip() or "30"
    try:
        max_attempts = int(attempts_input)
    except ValueError:
        print("Invalid number, using default of 30")
        max_attempts = 30
    
    # Get overall timeout
    timeout_input = input("Enter overall timeout in seconds (default: 300): ").strip() or "300"
    try:
        overall_timeout = int(timeout_input)
    except ValueError:
        print("Invalid number, using default of 300")
        overall_timeout = 300
    
    scraper = None
    reviews = []
    
    try:
        print("\nInitializing browser...")
        # Initialize the scraper
        scraper = GoogleMapsMaxReviewScraper(
            headless=headless,
            chrome_binary_path=chrome_binary_path
        )
        
        # Setup watchdog timer for the entire process
        import threading
        def timeout_handler():
            print(f"\n\nTimeout reached ({overall_timeout} seconds). Stopping review collection.")
            if scraper:
                print("Saving any reviews collected so far...")
                if len(reviews) > 0:
                    output_file = "timeout_reviews.csv"
                    scraper.save_reviews_to_files(reviews, output_file)
                    print(f"Saved {len(reviews)} reviews to {output_file}")
                try:
                    scraper.close()
                except:
                    pass
                os._exit(0)  # Force exit if needed
        
        # Start the timeout timer if requested
        timer = None
        if overall_timeout > 0:
            timer = threading.Timer(overall_timeout, timeout_handler)
            timer.daemon = True
            timer.start()
            print(f"Set timeout for {overall_timeout} seconds")
            
        # Scrape the reviews
        try:
            reviews = scraper.scrape_reviews(
                place_url=place_url,
                target_reviews=num_reviews,
                max_wait_time=max_wait,
                max_scroll_attempts=max_attempts
            )
        except KeyboardInterrupt:
            print("\nCollection interrupted by user. Saving collected reviews so far...")
            # Canceling the timeout timer
            if timer:
                timer.cancel()
        
        # Save the results
        if reviews:
            print(f"\nSuccessfully scraped {len(reviews)} reviews")
            output_file = input("Enter output file name (default: google_maps_reviews.csv): ") or "google_maps_reviews.csv"
            scraper.save_reviews_to_files(reviews, output_file)
        else:
            print("No reviews were scraped.")
            
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
        if reviews:
            print(f"Saving {len(reviews)} reviews collected so far...")
            scraper.save_reviews_to_files(reviews, "interrupted_reviews.csv")
            print("Reviews saved to interrupted_reviews.csv")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Try to save any reviews collected before the error
        if scraper and reviews:
            print(f"Saving {len(reviews)} reviews collected before the error...")
            try:
                scraper.save_reviews_to_files(reviews, "error_recovery_reviews.csv")
                print("Reviews saved to error_recovery_reviews.csv")
            except:
                print("Failed to save reviews after error")
    
    finally:
        # Cancel timeout timer if it exists
        if 'timer' in locals() and timer:
            timer.cancel()
            
        if 'scraper' in locals() and scraper:
            try:
                scraper.close()
            except:
                print("Failed to close browser properly")

def scrape_gmaps_reviews(
    place_url: str,
    num_reviews: int = 10,
    max_wait: float = 5,
    max_attempts: int = 30,
    headless: bool = True,
    chrome_binary_path: str = None,
    output_file: str = DATA_DIR
):
    scraper = GoogleMapsMaxReviewScraper(
        headless=headless,
        chrome_binary_path=chrome_binary_path
    )
    try:
        reviews = scraper.scrape_reviews(
            place_url=place_url,
            target_reviews=num_reviews,
            max_wait_time=max_wait,
            max_scroll_attempts=max_attempts
        )
        if output_file:
            scraper.save_reviews_to_files(reviews, output_file)
        return reviews
    finally:
        scraper.close()

if __name__ == "__main__":
    main() 