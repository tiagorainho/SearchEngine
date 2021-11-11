from src.tokenizer import Tokenizer


def test_instantiation():
    tokenizer = Tokenizer(10, "stop_words.txt")

    assert len(tokenizer.stop_words) == 127
    assert "i" in tokenizer.stop_words
    assert tokenizer.min_token_length == 10


def test_tokenize_no_min_len():
    tokenizer = Tokenizer(0)
    tokens = tokenizer.tokenize("Hello, I am Vasco Sousa from Portugal")

    assert len(tokens) == 7
    assert "hello" in tokens
    assert "i" in tokens
    assert "am" in tokens
    assert "vasco" in tokens
    assert "sousa" in tokens
    assert "from" in tokens
    assert "portugal" in tokens


def test_tokenize_min_len_8():
    tokenizer = Tokenizer(8)
    tokens = tokenizer.tokenize("Hello, I am Vasco Sousa from Portugal")

    assert len(tokens) == 1
    assert "vasco" not in tokens
    assert "sousa" not in tokens
    assert "hello" not in tokens
    assert "portugal" in tokens


def test_tokenize_no_stop_words():
    tokenizer = Tokenizer(0)
    tokens = tokenizer.tokenize("Hello, I am Vasco Sousa from Portugal")

    assert len(tokens) == 7
    assert "hello" in tokens
    assert "i" in tokens
    assert "am" in tokens
    assert "vasco" in tokens
    assert "sousa" in tokens
    assert "from" in tokens
    assert "portugal" in tokens


def test_tokenize_no_stop_words():
    tokenizer = Tokenizer(0)
    tokens = tokenizer.tokenize("Hello, I am Vasco Sousa from Portugal")

    assert len(tokens) == 7
    assert "hello" in tokens
    assert "i" in tokens
    assert "am" in tokens
    assert "vasco" in tokens
    assert "sousa" in tokens
    assert "from" in tokens
    assert "portugal" in tokens


def test_tokenize_stop_words():
    tokenizer = Tokenizer(0, "stop_words.txt")
    tokens = tokenizer.tokenize("Hello, I am Vasco Sousa from Portugal")

    assert len(tokens) == 4
    assert "hello" in tokens
    assert "vasco" in tokens
    assert "sousa" in tokens
    assert "portugal" in tokens


def test_tokenize_stemmer():
    tokenizer = Tokenizer(0, "stop_words.txt", "english")
    tokens = tokenizer.tokenize("Hello, I am Vasco Sousa from Portugal")

    assert len(tokens) == 4
    assert "hello" in tokens
    assert "vasco" in tokens
    assert "sousa" in tokens
    assert "portug" in tokens
