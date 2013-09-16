Feature: Survey features

  Scenario: List survey page
    Given I am logged in as researcher
    And I have 100 surveys
    And I visit surveys listing page
    Then I should see the survey list paginated
    And if I click the add survey button
    Then I should see the new survey form

  Scenario: Link to batch list
    Given I am logged in as researcher
    And I have a survey
    And I visit surveys listing page
    And I click on a survey name
    Then I should see a list of the batches under the survey

  Scenario: Add a survey
    Given I am logged in as researcher
    And I visit the new survey page
    When I fill in the survey details
    And I click save button
    Then I should see that the survey was saved successfully