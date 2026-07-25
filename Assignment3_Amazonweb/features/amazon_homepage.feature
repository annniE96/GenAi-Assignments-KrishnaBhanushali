@homepage
Feature: Amazon Homepage - Core interactions
  In order to verify Amazon homepage functionality
  As a QA engineer
  I want automated Cucumber scenarios that exercise common homepage features

  Background:
    Given I am on the Amazon homepage
    And the homepage has fully loaded

  @search
  Scenario Outline: Search products across departments
    Given the search category is set to "<Department>"
    When I enter "<SearchTerm>" into the main search box
    And I submit the search
    Then I should see search results for "<SearchTerm>"
    And the results should be scoped to the "<Department>" department

    Examples:
      | Department        | SearchTerm       |
      | All               | headphones       |
      | Electronics       | bluetooth speaker|
      | Books             | test automation  |

  @deliver-to
  Scenario: Change delivery location using Deliver to control
    Given the Deliver to control is visible
    When I open the Deliver to control
    And I set the delivery location to "Beverly Hills, CA 90210"
    Then the Deliver to control should show "Beverly Hills, CA 90210"
    And product availability and shipping estimates should refresh accordingly

  @signin
  Scenario: Open Account & Lists and navigate to sign in
    Given the Account & Lists control is visible
    When I open Account & Lists
    Then I should see a sign-in prompt or account menu
    When I choose to sign in with valid credentials
    Then I should be taken to the account overview page

  @orders
  Scenario: Open Returns & Orders and view order history
    Given the Returns & Orders control is visible
    When I click Returns & Orders
    Then I should be taken to the orders page
    And I should see a list of recent orders or a sign-in prompt if not signed in

  @cart
  Scenario: View shopping cart and item count
    Given the Cart control is visible
    When I open the Cart
    Then I should see the current number of items in the cart
    And the cart page should list each item with price and quantity

  @language-region
  Scenario: Switch language or shopping country/region
    Given the language/region selector is visible in the header or footer
    When I change the language to "Español" or the region to "United States"
    Then the homepage content should update to reflect the selected language/region

  @category-menu
  Scenario: Open the main category menu and navigate
    Given the main category menu (hamburger/menu) is visible
    When I open the main category menu
    And I select the "Electronics" top-level category
    Then I should be taken to the Electronics landing page

  @hero-carousel
  Scenario: Browse featured promotions in the hero carousel
    Given the hero carousel is visible on the homepage
    When I advance the hero carousel to the next slide
    Then the carousel should display the next promotion
    And clicking the promotion should navigate to the correct landing page

  @high-level-nav
  Scenario Outline: Navigate to high-level shopping areas
    When I click the "<Area>" link in the header or homepage modules
    Then I should land on the respective area page

    Examples:
      | Area           |
      | Today's Deals  |
      | Prime Video    |
      | Gift Cards     |
      | Sell           |
      | Customer Service|
      | Registry       |

  @collections
  Scenario: Explore curated collections and deal tiles
    Given the homepage modules with curated collections are visible
    When I click a featured collection tile
    Then I should be taken to the collection's browse page
    And I should see products or deals relevant to that collection

  @footer-links
  Scenario: Open footer links for help and policies
    Given the footer is visible
    When I open the footer and click "Help"
    Then I should be taken to the Help & Customer Service page
    When I click "Conditions of Use" or "Privacy Notice"
    Then the corresponding policy page should open

  @back-to-top
  Scenario: Navigate back to the top from the footer
    Given I am scrolled to the bottom of the homepage
    When I click the back-to-top control in the footer
    Then the viewport should scroll to the top of the page

  @accessibility
  Scenario: Basic accessibility checks on homepage
    Given I run an automated accessibility scan for the homepage
    Then there should be no critical accessibility violations
