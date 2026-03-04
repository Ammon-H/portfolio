import os
import csv
from datetime import datetime
from ideation_creation import add_idea_to_csv, search_ideas_in_csv
TEST_CSV = 'test_ideas.csv'

def setup_module(module):
    # Create a fresh test CSV file before each test module
    with open(TEST_CSV, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["character", "Test Name", "A test description", "2025-07-05 22:38:45"])
def teardown_module(module):
    # Remove the test CSV file after tests
    if os.path.exists(TEST_CSV):
        os.remove(TEST_CSV)

def test_add_idea_to_csv():
    category = "creature"
    name = "Test Creature"
    description = "A test creature description"
    date_created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    add_idea_to_csv(category, name, description, date_created, filename=TEST_CSV)
    with open(TEST_CSV, 'r') as csvfile:
        rows = list(csv.reader(csvfile))
        assert [category, name, description, date_created] in rows

def test_search_ideas_in_csv():
    # Should find the character row
    results = search_ideas_in_csv("character", filename=TEST_CSV)
    assert any("Test Name" in row for row in results)
    # Should not find a non-existent category
    results = search_ideas_in_csv("nonexistent", filename=TEST_CSV)
    assert results == []

# python -m unittest test_ideation_creation.py