from tokenizer import Tokenizer

tokenizer = Tokenizer("datasets/digital_video_games.tsv")

assert len(tokenizer.get_tokens()) == 0

tokenizer.tokenize(
    "review_id", ["product_title", "review_heading", "review_body"])

assert len(tokenizer.get_tokens()) > 0
