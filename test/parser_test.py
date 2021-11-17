from src.parser import Parser


def test_parse():
    parser = Parser("datasets/digital_video_games.tsv",
                    "review_id", ["review_headline", "review_body"])
    text = parser.parse("\t")

    assert text != ""
    assert "RSH1OZ87OYK92" in text
    assert "R1JEEW4C6R89BA" in text
    assert "A slight improvement from last year." in text["RSH1OZ87OYK92"]
