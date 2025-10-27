from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch()
    page = browser.new_page()

    # Test registration
    page.goto("http://127.0.0.1:5000/register.html")
    page.fill('input[placeholder="Inserisci il tuo nome"]', "Test")
    page.fill('input[placeholder="Inserisci il tuo cognome"]', "User")
    page.fill('input[placeholder="iltuoindirizzo@email.com"]', "test@example.com")
    page.fill('input[placeholder="Inserisci il tuo numero"]', "1234567890")
    page.fill('input[type="password"]', "password")
    page.click('button[type="submit"]')
    page.wait_for_url("http://127.0.0.1:5000/login.html")
    assert page.url == "http://127.0.0.1:5000/login.html"
    page.screenshot(path="jules-scratch/verification/login_after_register.png")

    # Test login and booking
    page.fill('input[type="email"]', "test@example.com")
    page.fill('input[type="password"]', "password")
    page.click('button[type="submit"]')
    page.wait_for_url("http://127.0.0.1:5000/booking.html")

    # Test calendar and booking
    page.click("text=15")
    page.click("text=14:00")
    page.click("text=Continua")
    page.on("dialog", lambda dialog: dialog.accept()) # Handle alert

    # Test navigation links from landing page
    page.goto("http://127.0.0.1:5000/")
    page.click("text=Scopri gli spazi")
    page.wait_for_url("http://127.0.0.1:5000/studiospaces.html")
    page.screenshot(path="jules-scratch/verification/studiospaces_page.png")

    # Test hamburger menu
    page.goto("http://127.0.0.1:5000/booking.html")
    page.click("#menu-button")
    page.wait_for_selector("#mobile-menu:not(.hidden)")
    page.screenshot(path="jules-scratch/verification/hamburger_menu.png")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
