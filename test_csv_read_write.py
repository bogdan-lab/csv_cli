import csv_read_write as crw


def test_convert_to_text():
    test = crw.FileContent(None, [])  # empty file
    assert len(crw.convert_to_text(test)) == 0
    test = crw.FileContent('header', [])  # with header but no content
    assert crw.convert_to_text(test) == 'header'
    # no header with content
    test = crw.FileContent(None, ['one', 'two', 'three'])
    assert crw.convert_to_text(test) == 'one\ntwo\nthree'
    test = crw.FileContent('header', ['one'])  # with header and content
    assert crw.convert_to_text(test) == 'header\none'
