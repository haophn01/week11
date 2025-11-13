from app.calc import add, sub  # import from the app package

def test_add():
    assert add(2, 3) == 5
    # Testing github

def test_sub():
    assert sub(10, 4) == 6
