from arsene_wenger.cogs.fixtures import find_fixtures, parse_arsenal


class TestFixtures:
    def test_mens_fixture_list_returns_correct_num_responses(self):
        fixtures = parse_arsenal(gender="men")
        fixture_list = find_fixtures(fixtures, 3)
        assert 0 < len(fixture_list) < 4

    def test_mens_fixtures_list_returns_correct_team(self):
        fixtures = parse_arsenal(gender="men")
        fixture_list = find_fixtures(fixtures, 3)
        for fixture in fixture_list:
            assert fixture.team != "Arsenal"

    def test_womens_fixture_list_returns_correct_num_responses(self):
        fixtures = parse_arsenal(gender="women")
        fixture_list = find_fixtures(fixtures, 3)
        assert 0 < len(fixture_list) < 4

    def test_womens_fixtures_list_returns_correct_team(self):
        fixtures = parse_arsenal(gender="women")
        fixture_list = find_fixtures(fixtures, 3)
        for fixture in fixture_list:
            assert fixture.team != "Arsenal"
